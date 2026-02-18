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
from agent.api_client import (
    api_create_task,
    api_list_tasks,
    api_complete_task,
    api_delete_task,
    api_update_task,
    APIClientError,
)

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
    """Create a new task with smart defaults. Call this only ONCE per user request.

    NATURAL LANGUAGE PARSING:
    - Parse "today/tomorrow/weekday names" to YYYY-MM-DD dates
    - Parse "X AM/PM" to HH:MM 24-hour times
    - Auto-detect category from keywords (shopping, work, health words)
    - Apply smart defaults for missing fields

    Args:
        title: Clean task title (remove scheduling/priority words)
        description: Optional descriptive text
        priority: "high", "medium", or "low" (default: "medium")
        category: "work", "personal", "shopping", "health", or "other" (default: "personal", or auto-detect)
        tags: Comma-separated tags if mentioned
        due_date: YYYY-MM-DD format (parsed from natural language)
        due_time: HH:MM 24-hour format (parsed from AM/PM)

    Returns:
        JSON string with task creation result
    """
    context = _get_current_context()
    auth_token = context.get("auth_token")

    if not auth_token:
        return json.dumps({"error": "Authentication required. Please log in again."})

    # Validate title
    if not title or not title.strip():
        return json.dumps({"error": "Task title is required"})

    try:
        # Validate priority
        p = priority.strip().lower() if priority else "medium"
        if p not in ("high", "medium", "low"):
            return json.dumps({"error": f"Invalid priority '{priority}'. Must be high, medium, or low."})

        # Validate category
        c = category.strip().lower() if category else "personal"
        if c not in ("work", "personal", "shopping", "health", "other"):
            return json.dumps({"error": f"Invalid category '{category}'. Must be work, personal, shopping, health, or other."})

        # Validate date format
        d = due_date.strip() if due_date else None
        if d and not (len(d) == 10 and d[4] == '-' and d[7] == '-'):
            return json.dumps({"error": f"Invalid date format '{due_date}'. Use YYYY-MM-DD."})

        # Validate time format
        t = due_time.strip() if due_time else None
        if t and not (len(t) == 5 and t[2] == ':'):
            return json.dumps({"error": f"Invalid time format '{due_time}'. Use HH:MM."})

        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else None

        result = await api_create_task(
            auth_token=auth_token,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=p,
            category=c,
            tags=tag_list,
            due_date=d,
            due_time=t,
        )
        return json.dumps(result)
    except APIClientError as e:
        return json.dumps({"error": e.message})


@function_tool
async def list_tasks(status: str = "all") -> str:
    """List tasks for the user.

    Args:
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        JSON string with list of tasks
    """
    context = _get_current_context()
    auth_token = context.get("auth_token")

    if not auth_token:
        return json.dumps({"error": "Authentication required. Please log in again."})

    try:
        result = await api_list_tasks(
            auth_token=auth_token,
            status=status,
        )
        return json.dumps(result)
    except APIClientError as e:
        return json.dumps({"error": e.message})


@function_tool
async def complete_task(task_id: str) -> str:
    """Mark a task as completed.

    Args:
        task_id: The UUID of the task to complete

    Returns:
        JSON string with completion result
    """
    context = _get_current_context()
    auth_token = context.get("auth_token")

    if not auth_token:
        return json.dumps({"error": "Authentication required. Please log in again."})

    try:
        result = await api_complete_task(
            auth_token=auth_token,
            task_id=task_id,
        )
        return json.dumps(result)
    except APIClientError as e:
        return json.dumps({"error": e.message})


@function_tool
async def delete_task(task_id: str) -> str:
    """Delete a task.

    Args:
        task_id: The UUID of the task to delete

    Returns:
        JSON string with deletion result
    """
    context = _get_current_context()
    auth_token = context.get("auth_token")

    if not auth_token:
        return json.dumps({"error": "Authentication required. Please log in again."})

    try:
        result = await api_delete_task(
            auth_token=auth_token,
            task_id=task_id,
        )
        return json.dumps(result)
    except APIClientError as e:
        return json.dumps({"error": e.message})


@function_tool
async def update_task(
    task_id: str,
    title: str = "",
    description: str = "",
    priority: str = "",
    category: str = "",
    tags: str = "",
    due_date: str = "",
    due_time: str = "",
    clear_due_date: bool = False,
    clear_due_time: bool = False,
    clear_description: bool = False,
) -> str:
    """Update specific fields of a task. ONLY updates fields that are explicitly provided.

    STRICT RULES:
    - Only pass fields the user explicitly mentioned
    - Do NOT infer or guess missing fields
    - Do NOT put priority/date/time/tags into description
    - Each field maps to its exact database column

    Args:
        task_id: The UUID of the task to update (required)
        title: New title - only if user wants to change the title
        description: New description text - only if user wants to change description
        priority: New priority "high", "medium", or "low" - only if user specifies
        category: New category "work", "personal", "shopping", "health", "other"
        tags: Comma-separated new tags - replaces existing tags
        due_date: New due date in YYYY-MM-DD format
        due_time: New due time in HH:MM format (24-hour)
        clear_due_date: Set True to remove the due date
        clear_due_time: Set True to remove the due time
        clear_description: Set True to remove the description

    Returns:
        JSON string with update result
    """
    context = _get_current_context()
    auth_token = context.get("auth_token")

    if not auth_token:
        return json.dumps({"error": "Authentication required. Please log in again."})

    # Build update params - only include provided fields
    update_title = title.strip() if title and title.strip() else None
    update_description = description.strip() if description and description.strip() else None
    update_priority = priority.strip().lower() if priority and priority.strip().lower() in ("high", "medium", "low") else None
    update_category = category.strip().lower() if category and category.strip().lower() in ("work", "personal", "shopping", "health", "other") else None
    update_tags = [t.strip() for t in tags.split(",") if t.strip()] if tags and tags.strip() else None
    update_due_date = due_date.strip() if due_date and due_date.strip() else None
    update_due_time = due_time.strip() if due_time and due_time.strip() else None

    # Handle clear flags by setting to empty string (API will interpret as clearing)
    if clear_description:
        update_description = ""
    if clear_due_date:
        update_due_date = ""
    if clear_due_time:
        update_due_time = ""

    # Check if any updates provided
    has_updates = any([
        update_title, update_description is not None, update_priority,
        update_category, update_tags, update_due_date is not None,
        update_due_time is not None
    ])

    if not has_updates:
        return json.dumps({"error": "No fields to update. Please specify what you want to change."})

    try:
        result = await api_update_task(
            auth_token=auth_token,
            task_id=task_id,
            title=update_title,
            description=update_description,
            priority=update_priority,
            category=update_category,
            tags=update_tags,
            due_date=update_due_date,
            due_time=update_due_time,
        )
        return json.dumps(result)
    except APIClientError as e:
        return json.dumps({"error": e.message})


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
    auth_token: str | None = None,
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

    # Set user context for tool execution (includes auth token for API calls)
    token = _set_current_context({
        "user_id": str(user_id),
        "auth_token": auth_token,
    })

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
