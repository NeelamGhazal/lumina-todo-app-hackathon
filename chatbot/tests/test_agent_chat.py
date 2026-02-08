# Task T027: Agent Chat Tests
"""Tests for chat orchestration module.

Tests:
- Message processing flow
- Tool execution loop
- Response formatting
- Error handling
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Conversation
from agent.schemas import ChatResponse, ToolCallSummary
from agent.chat import process_chat, _build_messages, _format_result_preview


class TestBuildMessages:
    """Tests for _build_messages helper."""

    def test_includes_system_message(self):
        """Test system message is included first."""
        messages = _build_messages(
            "You are a helpful assistant",
            [],
            "Hello",
        )

        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant"

    def test_includes_context_messages(self):
        """Test context messages are included."""
        context = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]

        messages = _build_messages("System", context, "New message")

        assert len(messages) == 3
        assert messages[1]["content"] == "Previous message"
        assert messages[2]["content"] == "Previous response"


class TestFormatResultPreview:
    """Tests for _format_result_preview helper."""

    def test_format_add_task(self):
        """Test formatting add_task result."""
        result = {"task_id": "123", "title": "Buy groceries", "status": "created"}
        preview = _format_result_preview("add_task", result)

        assert "Buy groceries" in preview
        assert "Created" in preview

    def test_format_list_tasks(self):
        """Test formatting list_tasks result."""
        result = {"tasks": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
        preview = _format_result_preview("list_tasks", result)

        assert "3" in preview

    def test_format_complete_task(self):
        """Test formatting complete_task result."""
        result = {"task_id": "123", "title": "Buy groceries", "status": "completed"}
        preview = _format_result_preview("complete_task", result)

        assert "Buy groceries" in preview
        assert "completed" in preview

    def test_format_delete_task(self):
        """Test formatting delete_task result."""
        result = {"task_id": "123", "title": "Old task", "status": "deleted"}
        preview = _format_result_preview("delete_task", result)

        assert "Old task" in preview
        assert "Deleted" in preview

    def test_format_update_task(self):
        """Test formatting update_task result."""
        result = {"task_id": "123", "title": "Updated task", "status": "updated"}
        preview = _format_result_preview("update_task", result)

        assert "Updated task" in preview

    def test_format_unknown_tool(self):
        """Test formatting unknown tool result."""
        preview = _format_result_preview("unknown_tool", {})
        assert preview == "Operation completed"


class TestProcessChat:
    """Tests for process_chat function."""

    @pytest.mark.asyncio
    async def test_creates_conversation(self, test_session: AsyncSession):
        """Test conversation is created for new user."""
        user_id = uuid4()

        # Mock the client and tools
        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings:

            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].message.content = "Hello! How can I help?"

            mock_client.create_chat_completion = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "You are helpful"
            mock_settings.return_value.max_tool_rounds = 5

            response = await process_chat("Hello", user_id, test_session)

            assert isinstance(response, ChatResponse)
            assert response.conversation_id is not None
            assert response.message == "Hello! How can I help?"

    @pytest.mark.asyncio
    async def test_stores_messages(self, test_session: AsyncSession):
        """Test user and assistant messages are stored."""
        user_id = uuid4()

        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings:

            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].message.content = "Response"

            mock_client.create_chat_completion = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "System"
            mock_settings.return_value.max_tool_rounds = 5

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
        """Test tool calls are executed."""
        user_id = uuid4()

        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings, \
             patch("agent.chat.execute_mcp_tool") as mock_execute:

            mock_client = MagicMock()

            # First response: tool call
            mock_tool_response = MagicMock()
            mock_tool_response.choices = [MagicMock()]
            mock_tool_response.choices[0].finish_reason = "tool_calls"
            mock_tool_response.choices[0].message.content = None

            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_123"
            mock_tool_call.function.name = "add_task"
            mock_tool_call.function.arguments = '{"title": "Test task"}'
            mock_tool_response.choices[0].message.tool_calls = [mock_tool_call]

            # Second response: final
            mock_final_response = MagicMock()
            mock_final_response.choices = [MagicMock()]
            mock_final_response.choices[0].finish_reason = "stop"
            mock_final_response.choices[0].message.tool_calls = None
            mock_final_response.choices[0].message.content = "I've added your task!"

            mock_client.create_chat_completion = AsyncMock(
                side_effect=[mock_tool_response, mock_final_response]
            )
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "System"
            mock_settings.return_value.max_tool_rounds = 5

            mock_execute.return_value = {
                "task_id": str(uuid4()),
                "title": "Test task",
                "status": "created",
            }

            response = await process_chat("Add a task", user_id, test_session)

            assert response.message == "I've added your task!"
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].tool == "add_task"
            assert response.tool_calls[0].success is True

    @pytest.mark.asyncio
    async def test_handles_tool_error(self, test_session: AsyncSession):
        """Test tool errors are handled gracefully."""
        user_id = uuid4()

        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings, \
             patch("agent.chat.execute_mcp_tool") as mock_execute:

            mock_client = MagicMock()

            # Tool call response
            mock_tool_response = MagicMock()
            mock_tool_response.choices = [MagicMock()]
            mock_tool_response.choices[0].finish_reason = "tool_calls"
            mock_tool_response.choices[0].message.content = None

            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_456"
            mock_tool_call.function.name = "complete_task"
            mock_tool_call.function.arguments = '{"task_id": "nonexistent"}'
            mock_tool_response.choices[0].message.tool_calls = [mock_tool_call]

            # Final response after error
            mock_final_response = MagicMock()
            mock_final_response.choices = [MagicMock()]
            mock_final_response.choices[0].finish_reason = "stop"
            mock_final_response.choices[0].message.tool_calls = None
            mock_final_response.choices[0].message.content = "I couldn't find that task."

            mock_client.create_chat_completion = AsyncMock(
                side_effect=[mock_tool_response, mock_final_response]
            )
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "System"
            mock_settings.return_value.max_tool_rounds = 5

            from agent.tools import ToolExecutionError
            mock_execute.side_effect = ToolExecutionError(
                "complete_task", "Task not found"
            )

            response = await process_chat("Complete task", user_id, test_session)

            assert response.tool_calls is not None
            assert response.tool_calls[0].success is False

    @pytest.mark.asyncio
    async def test_continues_existing_conversation(self, test_session: AsyncSession):
        """Test continuing an existing conversation."""
        user_id = uuid4()

        # Create existing conversation
        conv = Conversation(user_id=user_id)
        test_session.add(conv)
        await test_session.flush()

        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings:

            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].message.content = "Response"

            mock_client.create_chat_completion = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "System"
            mock_settings.return_value.max_tool_rounds = 5

            response = await process_chat(
                "Hello", user_id, test_session, conversation_id=conv.id
            )

            assert response.conversation_id == conv.id

    @pytest.mark.asyncio
    async def test_handles_llm_error(self, test_session: AsyncSession):
        """Test handling of LLM errors."""
        user_id = uuid4()

        with patch("agent.chat.get_openrouter_client") as mock_get_client, \
             patch("agent.chat.get_agent_settings") as mock_settings:

            mock_client = MagicMock()
            mock_client.create_chat_completion = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_client.return_value = mock_client

            mock_settings.return_value.agent_instructions = "System"
            mock_settings.return_value.max_tool_rounds = 5

            response = await process_chat("Hello", user_id, test_session)

            # Should return error message
            assert "error" in response.message.lower()
