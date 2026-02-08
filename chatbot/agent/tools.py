# Task T008-T012: MCP Tool Integration
"""MCP tool integration layer for the agent.

This module provides:
- Fetching MCP tool schemas from the MCP server
- Converting MCP schemas to OpenAI function format
- Executing MCP tools via HTTP calls
- Error handling for tool operations

References:
- data-model.md: OpenAI Function Definitions section
- plan.md: ADR-005 (manual tool execution), ADR-007 (startup loading)
- spec.md: FR-025-026 (tool schema conversion)
"""

from typing import Any
from uuid import UUID

import httpx
import structlog

from agent.config import get_agent_settings

logger = structlog.get_logger(__name__)

# Tool names that are available
TOOL_NAMES = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]

# Fields to exclude from LLM-visible parameters (injected by system)
SYSTEM_INJECTED_FIELDS = {"user_id"}


class MCPToolError(Exception):
    """Error during MCP tool operations."""

    def __init__(self, message: str, code: str = "MCP_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class MCPServerUnavailable(MCPToolError):
    """MCP server is not reachable."""

    def __init__(self, url: str, error: str):
        super().__init__(
            f"MCP server unavailable at {url}: {error}",
            code="MCP_UNAVAILABLE",
            details={"url": url, "error": error},
        )


class ToolExecutionError(MCPToolError):
    """Tool execution failed."""

    def __init__(self, tool_name: str, error: str, details: dict | None = None):
        super().__init__(
            f"Tool '{tool_name}' failed: {error}",
            code="TOOL_EXECUTION_ERROR",
            details={"tool": tool_name, "error": error, **(details or {})},
        )


class ToolValidationError(MCPToolError):
    """Tool parameter validation failed."""

    def __init__(self, tool_name: str, errors: list[dict]):
        super().__init__(
            f"Invalid parameters for tool '{tool_name}'",
            code="VALIDATION_ERROR",
            details={"tool": tool_name, "errors": errors},
        )


# === T008: Fetch MCP Tools ===


async def fetch_mcp_tools() -> list[dict[str, Any]]:
    """Fetch tool schemas from MCP server.

    Makes a GET request to /mcp/tools endpoint to retrieve
    all available tool definitions.

    Returns:
        List of MCP tool definitions

    Raises:
        MCPServerUnavailable: If MCP server is not reachable
    """
    settings = get_agent_settings()
    url = f"{settings.mcp_server_url}/mcp/tools"

    logger.debug("fetching_mcp_tools", url=url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            tools = data.get("tools", [])
            logger.info("mcp_tools_fetched", count=len(tools))
            return tools
    except httpx.ConnectError as e:
        raise MCPServerUnavailable(url, str(e))
    except httpx.HTTPStatusError as e:
        raise MCPServerUnavailable(url, f"HTTP {e.response.status_code}")
    except Exception as e:
        raise MCPServerUnavailable(url, str(e))


# === T009: Convert MCP to OpenAI Function Format ===


def mcp_to_openai_function(mcp_tool: dict[str, Any]) -> dict[str, Any]:
    """Convert MCP tool schema to OpenAI function format.

    Transforms the MCP tool definition to match OpenAI's
    function calling schema. Excludes user_id from parameters
    as it's injected by the system.

    Args:
        mcp_tool: MCP tool definition with name, description, parameters

    Returns:
        OpenAI function definition
    """
    name = mcp_tool["name"]
    description = mcp_tool["description"]
    mcp_params = mcp_tool.get("parameters", {})

    # Filter out system-injected fields from properties
    properties = mcp_params.get("properties", {})
    filtered_properties = {
        key: value
        for key, value in properties.items()
        if key not in SYSTEM_INJECTED_FIELDS
    }

    # Filter out system-injected fields from required list
    required = mcp_params.get("required", [])
    filtered_required = [
        field for field in required
        if field not in SYSTEM_INJECTED_FIELDS
    ]

    # Build OpenAI function schema
    openai_params = {
        "type": "object",
        "properties": filtered_properties,
        "required": filtered_required,
    }

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": openai_params,
        },
    }


# === T010: Get All Tools in OpenAI Format ===


async def get_openai_tools() -> list[dict[str, Any]]:
    """Get all MCP tools converted to OpenAI function format.

    Fetches tools from MCP server and converts each to
    OpenAI's function calling format with user_id excluded.

    Returns:
        List of OpenAI function definitions

    Raises:
        MCPServerUnavailable: If MCP server is not reachable
    """
    mcp_tools = await fetch_mcp_tools()
    openai_tools = [mcp_to_openai_function(tool) for tool in mcp_tools]

    logger.debug(
        "openai_tools_converted",
        count=len(openai_tools),
        tools=[t["function"]["name"] for t in openai_tools],
    )

    return openai_tools


# === T011: Execute MCP Tool ===


async def execute_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
    user_id: UUID,
) -> dict[str, Any]:
    """Execute an MCP tool with the given arguments.

    Makes a POST request to /mcp/call endpoint with the
    tool name and parameters. Injects user_id into parameters.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from LLM (without user_id)
        user_id: User ID to inject into parameters

    Returns:
        Tool execution result

    Raises:
        MCPServerUnavailable: If MCP server is not reachable
        ToolValidationError: If parameters are invalid
        ToolExecutionError: If tool execution fails
    """
    settings = get_agent_settings()
    url = f"{settings.mcp_server_url}/mcp/call"

    # Inject user_id into parameters
    parameters = {**arguments, "user_id": str(user_id)}

    logger.debug(
        "executing_mcp_tool",
        tool=tool_name,
        url=url,
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={"tool": tool_name, "parameters": parameters},
            )
            response.raise_for_status()
            result = response.json()

            # Check for tool-level errors
            if result.get("status") == "error":
                error = result.get("error", {})
                error_code = error.get("code", "UNKNOWN_ERROR")
                error_message = error.get("message", "Unknown error")
                error_details = error.get("details")

                # Handle validation errors specifically
                if error_code == "VALIDATION_ERROR":
                    errors = error_details.get("errors", []) if error_details else []
                    raise ToolValidationError(tool_name, errors)

                raise ToolExecutionError(tool_name, error_message, error_details)

            logger.info(
                "mcp_tool_executed",
                tool=tool_name,
                status="success",
            )

            return result.get("data", {})

    except httpx.ConnectError as e:
        raise MCPServerUnavailable(url, str(e))
    except httpx.HTTPStatusError as e:
        raise MCPServerUnavailable(url, f"HTTP {e.response.status_code}")
    except (ToolValidationError, ToolExecutionError):
        raise
    except Exception as e:
        if isinstance(e, MCPToolError):
            raise
        raise ToolExecutionError(tool_name, str(e))


# === T012: Error Handling Utilities ===


def format_tool_error_for_user(error: MCPToolError) -> str:
    """Format a tool error as a user-friendly message.

    Args:
        error: The MCPToolError exception

    Returns:
        User-friendly error message
    """
    if isinstance(error, MCPServerUnavailable):
        return "I'm having trouble connecting to the task service. Please try again in a moment."

    if isinstance(error, ToolValidationError):
        # Extract validation error details if available
        errors = error.details.get("errors", [])
        if errors:
            # Format first error for user
            first_error = errors[0]
            field = first_error.get("loc", ["unknown"])[-1]
            msg = first_error.get("msg", "invalid value")
            return f"There was a problem with the {field}: {msg}"
        return "The request couldn't be processed due to invalid data."

    if isinstance(error, ToolExecutionError):
        # Check for specific error codes
        details = error.details
        if details.get("error") == "TASK_NOT_FOUND":
            return "I couldn't find that task. It may have been deleted or doesn't exist."
        if details.get("error") == "UNAUTHORIZED":
            return "You don't have permission to access that task."
        return f"I encountered an issue: {error.message}"

    return "Something went wrong while processing your request. Please try again."


def build_tool_result_message(
    tool_call_id: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Build a tool result message for OpenAI.

    Args:
        tool_call_id: ID of the tool call from OpenAI
        result: Tool execution result (if successful)
        error: Error message (if failed)

    Returns:
        Message dict for OpenAI's tool result format
    """
    import json

    if error:
        content = json.dumps({"error": error})
    else:
        content = json.dumps(result or {})

    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }


# Export public API
__all__ = [
    # Errors
    "MCPToolError",
    "MCPServerUnavailable",
    "ToolExecutionError",
    "ToolValidationError",
    # Functions
    "fetch_mcp_tools",
    "mcp_to_openai_function",
    "get_openai_tools",
    "execute_mcp_tool",
    "format_tool_error_for_user",
    "build_tool_result_message",
    # Constants
    "TOOL_NAMES",
]
