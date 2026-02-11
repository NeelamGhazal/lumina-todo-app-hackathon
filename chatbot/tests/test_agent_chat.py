# Task T027: Agent Chat Tests (Updated for OpenAI Agents SDK)
"""Tests for chat orchestration module.

Tests:
- Message processing flow
- Agent response handling
- Error handling

Updated to work with OpenAI Agents SDK integration.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Conversation
from agent.schemas import ChatResponse, ToolCallSummary
from agent.chat import process_chat


class TestProcessChat:
    """Tests for process_chat function."""

    @pytest.mark.asyncio
    async def test_creates_conversation(self, test_session: AsyncSession):
        """Test conversation is created for new user."""
        user_id = uuid4()

        # Mock the agent SDK
        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.return_value = ("Hello! How can I help?", [])

            response = await process_chat("Hello", user_id, test_session)

            assert isinstance(response, ChatResponse)
            assert response.conversation_id is not None
            assert response.message == "Hello! How can I help?"

    @pytest.mark.asyncio
    async def test_stores_messages(self, test_session: AsyncSession):
        """Test user and assistant messages are stored."""
        user_id = uuid4()

        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.return_value = ("Response", [])

            response = await process_chat("User message", user_id, test_session)

            # Verify messages were stored
            from agent.conversation import get_context_messages
            messages = await get_context_messages(
                test_session, response.conversation_id
            )

            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "User message"
            assert messages[1]["role"] == "assistant"
            assert messages[1]["content"] == "Response"

    @pytest.mark.asyncio
    async def test_handles_tool_calls(self, test_session: AsyncSession):
        """Test tool calls are executed and reported."""
        user_id = uuid4()

        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.return_value = (
                "I've added your task!",
                [{"tool": "add_task", "success": True, "result_preview": "Created"}]
            )

            response = await process_chat("Add a task", user_id, test_session)

            assert response.message == "I've added your task!"
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].tool == "add_task"
            assert response.tool_calls[0].success is True

    @pytest.mark.asyncio
    async def test_handles_agent_not_ready(self, test_session: AsyncSession):
        """Test handling when agent is not initialized."""
        user_id = uuid4()

        with patch("agent.chat.is_agent_ready") as mock_ready:
            mock_ready.return_value = False

            response = await process_chat("Hello", user_id, test_session)

            assert "not available" in response.message.lower()

    @pytest.mark.asyncio
    async def test_continues_existing_conversation(self, test_session: AsyncSession):
        """Test continuing an existing conversation."""
        user_id = uuid4()

        # Create existing conversation
        conv = Conversation(user_id=user_id)
        test_session.add(conv)
        await test_session.flush()

        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.return_value = ("Response", [])

            response = await process_chat(
                "Hello", user_id, test_session, conversation_id=conv.id
            )

            assert response.conversation_id == conv.id

    @pytest.mark.asyncio
    async def test_handles_agent_error(self, test_session: AsyncSession):
        """Test handling of agent errors."""
        user_id = uuid4()

        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.side_effect = Exception("Agent Error")

            response = await process_chat("Hello", user_id, test_session)

            # Should return error message
            assert "error" in response.message.lower()

    @pytest.mark.asyncio
    async def test_tool_call_summary_format(self, test_session: AsyncSession):
        """Test tool call summaries are properly formatted."""
        user_id = uuid4()

        with patch("agent.chat.is_agent_ready") as mock_ready, \
             patch("agent.chat.run_agent") as mock_run:

            mock_ready.return_value = True
            mock_run.return_value = (
                "Done!",
                [
                    {"tool": "list_tasks", "success": True, "result_preview": "3 tasks"},
                    {"tool": "complete_task", "success": True, "result_preview": "Completed"},
                ]
            )

            response = await process_chat("List and complete", user_id, test_session)

            assert response.tool_calls is not None
            assert len(response.tool_calls) == 2
            assert response.tool_calls[0].tool == "list_tasks"
            assert response.tool_calls[1].tool == "complete_task"
