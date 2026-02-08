# Task T025: Agent Tools Tests
"""Tests for MCP tool integration module.

Tests:
- MCP to OpenAI schema conversion
- Tool execution (mocked)
- Error handling
- user_id exclusion from LLM params
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from agent.tools import (
    mcp_to_openai_function,
    fetch_mcp_tools,
    get_openai_tools,
    execute_mcp_tool,
    format_tool_error_for_user,
    build_tool_result_message,
    MCPServerUnavailable,
    ToolExecutionError,
    ToolValidationError,
    SYSTEM_INJECTED_FIELDS,
)


class TestMcpToOpenaiFunction:
    """Tests for MCP to OpenAI schema conversion."""

    def test_basic_conversion(self):
        """Test basic schema conversion."""
        mcp_tool = {
            "name": "add_task",
            "description": "Add a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                },
                "required": ["title"],
            },
        }

        result = mcp_to_openai_function(mcp_tool)

        assert result["type"] == "function"
        assert result["function"]["name"] == "add_task"
        assert result["function"]["description"] == "Add a new task"
        assert "title" in result["function"]["parameters"]["properties"]

    def test_excludes_user_id(self):
        """Test user_id is excluded from LLM-visible parameters."""
        mcp_tool = {
            "name": "add_task",
            "description": "Add a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "title": {"type": "string"},
                },
                "required": ["user_id", "title"],
            },
        }

        result = mcp_to_openai_function(mcp_tool)

        # user_id should be excluded
        assert "user_id" not in result["function"]["parameters"]["properties"]
        assert "user_id" not in result["function"]["parameters"]["required"]
        # title should still be there
        assert "title" in result["function"]["parameters"]["properties"]
        assert "title" in result["function"]["parameters"]["required"]

    def test_preserves_optional_fields(self):
        """Test optional fields are preserved."""
        mcp_tool = {
            "name": "update_task",
            "description": "Update a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["user_id", "task_id"],
            },
        }

        result = mcp_to_openai_function(mcp_tool)

        props = result["function"]["parameters"]["properties"]
        assert "task_id" in props
        assert "title" in props
        assert "description" in props
        assert "user_id" not in props


class TestFetchMcpTools:
    """Tests for fetching tools from MCP server."""

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Test successful tool fetch."""
        mock_tools = [
            {"name": "add_task", "description": "Add task", "parameters": {}},
            {"name": "list_tasks", "description": "List tasks", "parameters": {}},
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {"tools": mock_tools}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)

        with patch("agent.tools.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            tools = await fetch_mcp_tools()

            assert len(tools) == 2
            assert tools[0]["name"] == "add_task"

    @pytest.mark.asyncio
    async def test_fetch_connection_error(self):
        """Test handling of connection error."""
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with patch("agent.tools.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(MCPServerUnavailable):
                await fetch_mcp_tools()


class TestGetOpenaiTools:
    """Tests for getting all tools in OpenAI format."""

    @pytest.mark.asyncio
    async def test_converts_all_tools(self):
        """Test all tools are converted to OpenAI format."""
        mock_mcp_tools = [
            {
                "name": "add_task",
                "description": "Add a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                    },
                    "required": ["user_id", "title"],
                },
            },
        ]

        with patch("agent.tools.fetch_mcp_tools", return_value=mock_mcp_tools):
            tools = await get_openai_tools()

            assert len(tools) == 1
            assert tools[0]["type"] == "function"
            # user_id should be excluded
            assert "user_id" not in tools[0]["function"]["parameters"]["properties"]


class TestExecuteMcpTool:
    """Tests for tool execution."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful tool execution."""
        user_id = uuid4()
        expected_result = {"task_id": str(uuid4()), "status": "created"}

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": expected_result}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        with patch("agent.tools.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await execute_mcp_tool("add_task", {"title": "Test"}, user_id)

            assert result == expected_result
            # Verify user_id was injected
            call_args = mock_client_instance.post.call_args
            params = call_args[1]["json"]["parameters"]
            assert params["user_id"] == str(user_id)

    @pytest.mark.asyncio
    async def test_execute_validation_error(self):
        """Test handling of validation error."""
        user_id = uuid4()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid parameters",
                "details": {"errors": [{"loc": ["title"], "msg": "required"}]},
            },
        }
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        with patch("agent.tools.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(ToolValidationError):
                await execute_mcp_tool("add_task", {}, user_id)

    @pytest.mark.asyncio
    async def test_execute_tool_error(self):
        """Test handling of tool execution error."""
        user_id = uuid4()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": "Task not found",
            },
        }
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        with patch("agent.tools.httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(ToolExecutionError):
                await execute_mcp_tool("complete_task", {"task_id": str(uuid4())}, user_id)


class TestErrorFormatting:
    """Tests for error formatting utilities."""

    def test_format_mcp_unavailable(self):
        """Test formatting MCP unavailable error."""
        error = MCPServerUnavailable("http://test", "connection refused")
        message = format_tool_error_for_user(error)

        assert "trouble connecting" in message.lower()

    def test_format_validation_error(self):
        """Test formatting validation error."""
        error = ToolValidationError("add_task", [{"loc": ["title"], "msg": "required"}])
        message = format_tool_error_for_user(error)

        assert "title" in message.lower()

    def test_format_tool_execution_error(self):
        """Test formatting tool execution error."""
        error = ToolExecutionError("add_task", "Something went wrong")
        message = format_tool_error_for_user(error)

        assert len(message) > 0


class TestBuildToolResultMessage:
    """Tests for building tool result messages."""

    def test_build_success_result(self):
        """Test building success result message."""
        result = {"task_id": "123", "status": "created"}
        message = build_tool_result_message("call_123", result=result)

        assert message["role"] == "tool"
        assert message["tool_call_id"] == "call_123"
        assert "123" in message["content"]

    def test_build_error_result(self):
        """Test building error result message."""
        message = build_tool_result_message("call_456", error="Task not found")

        assert message["role"] == "tool"
        assert message["tool_call_id"] == "call_456"
        assert "error" in message["content"]
