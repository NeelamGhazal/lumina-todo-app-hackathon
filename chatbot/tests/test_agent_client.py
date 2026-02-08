# Task T024: Agent Client Tests
"""Tests for OpenRouter client module.

Tests:
- Client initialization
- Tool registration
- Chat completion (mocked)
- Singleton pattern
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.config import AgentSettings
from agent.client import (
    OpenRouterClient,
    get_openrouter_client,
    reset_client,
    initialize_agent,
)


class TestOpenRouterClient:
    """Tests for OpenRouterClient class."""

    def test_initialization(self):
        """Test client initializes with settings."""
        settings = AgentSettings(
            openrouter_api_key="test-key",
            agent_model="gpt-4o-mini",
        )

        client = OpenRouterClient(settings)

        assert client.settings == settings
        assert client.tools == []
        assert client.client is not None

    def test_set_tools(self):
        """Test tool registration."""
        settings = AgentSettings(openrouter_api_key="test-key")
        client = OpenRouterClient(settings)

        tools = [
            {"type": "function", "function": {"name": "test_tool"}},
        ]
        client.set_tools(tools)

        assert client.tools == tools
        assert len(client.tools) == 1

    def test_is_ready_with_key(self):
        """Test is_ready returns True when configured."""
        settings = AgentSettings(openrouter_api_key="test-key")
        client = OpenRouterClient(settings)

        assert client.is_ready is True

    def test_is_ready_without_key(self):
        """Test is_ready returns False when not configured."""
        settings = AgentSettings(openrouter_api_key="")
        client = OpenRouterClient(settings)

        assert client.is_ready is False

    @pytest.mark.asyncio
    async def test_create_chat_completion_without_tools(self):
        """Test chat completion without tools."""
        settings = AgentSettings(openrouter_api_key="test-key")
        client = OpenRouterClient(settings)

        # Mock the OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Hello!"

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "Hi"}]
        response = await client.create_chat_completion(messages, use_tools=False)

        assert response == mock_response
        client.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_chat_completion_with_tools(self):
        """Test chat completion with tools."""
        settings = AgentSettings(openrouter_api_key="test-key")
        client = OpenRouterClient(settings)

        tools = [{"type": "function", "function": {"name": "add_task"}}]
        client.set_tools(tools)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "tool_calls"

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "Add a task"}]
        await client.create_chat_completion(messages, use_tools=True)

        # Verify tools were included in the call
        call_kwargs = client.client.chat.completions.create.call_args[1]
        assert "tools" in call_kwargs
        assert call_kwargs["tools"] == tools

    @pytest.mark.asyncio
    async def test_submit_tool_results(self):
        """Test submitting tool results."""
        settings = AgentSettings(openrouter_api_key="test-key")
        client = OpenRouterClient(settings)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Task added!"

        client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "Add task"}]
        tool_results = [
            {"role": "tool", "tool_call_id": "123", "content": "{}"}
        ]

        response = await client.submit_tool_results(messages, tool_results)

        assert response == mock_response
        # Should have combined messages
        call_args = client.client.chat.completions.create.call_args[1]
        assert len(call_args["messages"]) == 2


class TestSingletonPattern:
    """Tests for singleton pattern."""

    def test_get_openrouter_client_returns_instance(self):
        """Test get_openrouter_client returns client instance."""
        reset_client()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}, clear=False):
            client = get_openrouter_client()
            assert isinstance(client, OpenRouterClient)

    def test_reset_client_clears_instance(self):
        """Test reset_client clears the singleton."""
        reset_client()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}, clear=False):
            client1 = get_openrouter_client()
            reset_client()
            client2 = get_openrouter_client()

            # After reset, should get new instance
            assert client1 is not client2


class TestInitializeAgent:
    """Tests for initialize_agent function."""

    @pytest.mark.asyncio
    async def test_initialize_agent_not_configured(self):
        """Test initialize returns False when not configured."""
        reset_client()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            from agent.config import get_agent_settings
            get_agent_settings.cache_clear()

            result = await initialize_agent()
            assert result is False

    @pytest.mark.asyncio
    async def test_initialize_agent_mcp_unavailable(self):
        """Test initialize handles MCP server unavailable."""
        reset_client()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            from agent.config import get_agent_settings
            get_agent_settings.cache_clear()

            # Mock get_openai_tools to raise MCPServerUnavailable
            with patch("agent.tools.get_openai_tools") as mock_tools:
                from agent.tools import MCPServerUnavailable
                mock_tools.side_effect = MCPServerUnavailable("http://test", "connection refused")

                result = await initialize_agent()
                assert result is False

    @pytest.mark.asyncio
    async def test_initialize_agent_success(self):
        """Test initialize succeeds with tools."""
        reset_client()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
            from agent.config import get_agent_settings
            get_agent_settings.cache_clear()

            mock_tools_data = [
                {"type": "function", "function": {"name": "add_task"}},
            ]

            with patch("agent.tools.get_openai_tools", new=AsyncMock(return_value=mock_tools_data)):
                result = await initialize_agent()
                assert result is True

                # Verify tools were registered
                client = get_openrouter_client()
                assert len(client.tools) == 1
