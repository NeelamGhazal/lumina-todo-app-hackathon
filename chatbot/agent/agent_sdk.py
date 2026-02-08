# Task: OpenAI Agents SDK Integration
"""OpenAI Agents SDK agent implementation using OpenRouter.

This module replaces the manual OpenRouter client with the official
OpenAI Agents SDK, configured to use OpenRouter as the backend.

Per hackathon spec: Must use OpenAI Agents SDK (but can use OpenRouter API key
since the SDK accepts third-party endpoints).

References:
- https://openai.github.io/openai-agents-python/
- https://github.com/openai/openai-agents-python
"""

import json
from typing import Any
from uuid import UUID

import structlog
from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client, function_tool

from agent.config import get_agent_settings
from agent.tools import execute_mcp_tool, MCPToolError, format_tool_error_for_user

logger = structlog.get_logger(__name__)

# Global agent instance (initialized at startup)
_todo_agent: Agent | None = None
_agent_initialized: bool = False


def _configure_openrouter_client() -> None:
    """Configure OpenAI Agents SDK to use OpenRouter as backend.

    Uses set_default_openai_client to point the SDK at OpenRouter's
    API endpoint while using the OpenRouter API key.
    """
    settings = get_agent_settings()

    if not settings.is_configured:
        logger.warning("agent_not_configured", message="OPENROUTER_API_KEY not set")
        return

    # Create OpenAI client pointing to OpenRouter
    openrouter_client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        default_headers={
            "HTTP-Referer": "https://evolution-todo.app",
            "X-Title": "Evolution Todo Agent",
        },
    )

    # Set as default client for the Agents SDK
    set_default_openai_client(openrouter_client)

    logger.info(
        "openrouter_client_configured",
        base_url=settings.openrouter_base_url,
        model=settings.agent_model,
    )


# === MCP Tool Wrappers as Function Tools ===
# These wrap the MCP tool execution to work with the Agents SDK


@function_tool
async def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    category: str = "personal",
    tags: str = "",
    due_date: str = "",
    due_time: str = "",
) -> str:
    """Create a new task for the user.

    Args:
        title: The task title (required)
        description: Optional task description
        priority: Task priority - "high", "medium", or "low" (default: medium)
        category: Task category - "work", "personal", "shopping", "health", "other" (default: personal)
        tags: Comma-separated list of tags (e.g., "urgent,meeting")
        due_date: Due date in YYYY-MM-DD format (e.g., "2024-12-31")
        due_time: Due time in HH:MM format, 24-hour (e.g., "14:30")

    Returns:
        JSON string with task creation result
    """
    # Note: user_id is injected from context during execution
    context = _get_current_context()
    user_id = context.get("user_id")

    if not user_id:
        return json.dumps({"error": "No user context available"})

    try:
        # Build parameters
        params: dict[str, Any] = {"title": title}

        if description:
            params["description"] = description
        if priority and priority in ("high", "medium", "low"):
            params["priority"] = priority
        if category and category in ("work", "personal", "shopping", "health", "other"):
            params["category"] = category
        if tags:
            params["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
        if due_date:
            params["due_date"] = due_date
        if due_time:
            params["due_time"] = due_time

        result = await execute_mcp_tool("add_task", params, UUID(user_id))
        return json.dumps(result)
    except MCPToolError as e:
        return json.dumps({"error": format_tool_error_for_user(e)})


@function_tool
async def list_tasks(status: str = "all") -> str:
    """List tasks for the user.

    Args:
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        JSON string with list of tasks
    """
    context = _get_current_context()
    user_id = context.get("user_id")

    if not user_id:
        return json.dumps({"error": "No user context available"})

    try:
        result = await execute_mcp_tool(
            "list_tasks",
            {"status": status},
            UUID(user_id),
        )
        return json.dumps(result)
    except MCPToolError as e:
        return json.dumps({"error": format_tool_error_for_user(e)})


@function_tool
async def complete_task(task_id: str) -> str:
    """Mark a task as completed.

    Args:
        task_id: The UUID of the task to complete

    Returns:
        JSON string with completion result
    """
    context = _get_current_context()
    user_id = context.get("user_id")

    if not user_id:
        return json.dumps({"error": "No user context available"})

    try:
        result = await execute_mcp_tool(
            "complete_task",
            {"task_id": task_id},
            UUID(user_id),
        )
        return json.dumps(result)
    except MCPToolError as e:
        return json.dumps({"error": format_tool_error_for_user(e)})


@function_tool
async def delete_task(task_id: str) -> str:
    """Delete a task.

    Args:
        task_id: The UUID of the task to delete

    Returns:
        JSON string with deletion result
    """
    context = _get_current_context()
    user_id = context.get("user_id")

    if not user_id:
        return json.dumps({"error": "No user context available"})

    try:
        result = await execute_mcp_tool(
            "delete_task",
            {"task_id": task_id},
            UUID(user_id),
        )
        return json.dumps(result)
    except MCPToolError as e:
        return json.dumps({"error": format_tool_error_for_user(e)})


@function_tool
async def update_task(task_id: str, title: str = "", description: str = "") -> str:
    """Update a task's title or description.

    Args:
        task_id: The UUID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        JSON string with update result
    """
    context = _get_current_context()
    user_id = context.get("user_id")

    if not user_id:
        return json.dumps({"error": "No user context available"})

    # Build arguments with only provided fields
    args: dict[str, Any] = {"task_id": task_id}
    if title:
        args["title"] = title
    if description:
        args["description"] = description

    try:
        result = await execute_mcp_tool("update_task", args, UUID(user_id))
        return json.dumps(result)
    except MCPToolError as e:
        return json.dumps({"error": format_tool_error_for_user(e)})


# === Context Management ===
# Thread-local context for passing user_id to tool functions

import contextvars

_current_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "agent_context", default={}
)


def _get_current_context() -> dict[str, Any]:
    """Get the current execution context."""
    return _current_context.get()


def _set_current_context(context: dict[str, Any]) -> contextvars.Token:
    """Set the current execution context."""
    return _current_context.set(context)


# === Agent Initialization ===


def create_todo_agent() -> Agent:
    """Create the Todo Assistant agent with MCP tools.

    Returns:
        Configured Agent instance
    """
    settings = get_agent_settings()

    return Agent(
        name="Todo Assistant",
        instructions=settings.agent_instructions,
        model=settings.agent_model,
        tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    )


async def initialize_agents_sdk() -> bool:
    """Initialize the OpenAI Agents SDK with OpenRouter.

    Should be called during application startup.

    Returns:
        True if initialization succeeded, False otherwise
    """
    global _todo_agent, _agent_initialized

    settings = get_agent_settings()

    if not settings.is_configured:
        logger.warning(
            "agents_sdk_not_configured",
            message="OPENROUTER_API_KEY not set",
        )
        return False

    try:
        # Configure OpenRouter as the backend
        _configure_openrouter_client()

        # Create the agent
        _todo_agent = create_todo_agent()
        _agent_initialized = True

        logger.info(
            "agents_sdk_initialized",
            model=settings.agent_model,
            tool_count=5,
        )
        return True

    except Exception as e:
        logger.error(
            "agents_sdk_init_failed",
            error=str(e),
        )
        return False


def get_todo_agent() -> Agent | None:
    """Get the initialized Todo Agent.

    Returns:
        Agent instance or None if not initialized
    """
    return _todo_agent


def is_agent_ready() -> bool:
    """Check if the agent is ready for use."""
    return _agent_initialized and _todo_agent is not None


# === Agent Execution ===


async def run_agent(
    message: str,
    user_id: UUID,
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Run the agent with a user message.

    Args:
        message: User's message
        user_id: User's UUID (for MCP tool context)
        conversation_history: Previous messages for context

    Returns:
        Tuple of (response_text, tool_calls_summary)

    Raises:
        RuntimeError: If agent is not initialized
    """
    if not is_agent_ready():
        raise RuntimeError("Agent not initialized. Call initialize_agents_sdk() first.")

    agent = get_todo_agent()

    # Set user context for tool execution
    token = _set_current_context({"user_id": str(user_id)})

    try:
        # Build input with conversation context
        if conversation_history:
            # Format history as context for the agent
            context_str = "\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in conversation_history[-10:]  # Last 10 messages
            ])
            full_input = f"Previous conversation:\n{context_str}\n\nUser: {message}"
        else:
            full_input = message

        logger.debug(
            "running_agent",
            user_id=str(user_id),
            message_length=len(message),
            has_history=bool(conversation_history),
        )

        # Run the agent
        result = await Runner.run(agent, full_input)

        # Extract tool calls from the result
        tool_calls = []
        if hasattr(result, 'raw_responses'):
            for response in result.raw_responses:
                if hasattr(response, 'output') and response.output:
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'function_call':
                            tool_calls.append({
                                "tool": item.name,
                                "success": True,
                                "result_preview": "Executed",
                            })

        response_text = result.final_output or "I couldn't generate a response."

        logger.info(
            "agent_run_completed",
            user_id=str(user_id),
            response_length=len(response_text),
            tool_calls=len(tool_calls),
        )

        return response_text, tool_calls

    except Exception as e:
        logger.error(
            "agent_run_failed",
            user_id=str(user_id),
            error=str(e),
        )
        raise

    finally:
        # Reset context
        _current_context.reset(token)


# Export public API
__all__ = [
    "initialize_agents_sdk",
    "get_todo_agent",
    "is_agent_ready",
    "run_agent",
    "create_todo_agent",
]
