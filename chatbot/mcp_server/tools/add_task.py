# Task T014: Implement add_task Tool
"""MCP Tool: add_task - Create a new task for a user.

User Story 1 (P1): AI Agent Creates a Task
An AI agent creates a new todo task on behalf of a user.

References:
- spec.md: FR-010-014 (add_task requirements)
- spec.md: US1 acceptance scenarios
- contracts/mcp-tools.yaml: AddTaskParams, AddTaskResponse
"""

from datetime import date, time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task, TaskPriority, TaskCategory
from mcp_server.schemas import AddTaskParams
from mcp_server.logging import with_tool_logging, get_logger
from mcp_server.tools import register_tool
from mcp_server.tools.base import (
    ToolError,
    database_error,
    build_add_task_response,
)

logger = get_logger("tools.add_task")


def _parse_date(date_str: str | None) -> date | None:
    """Parse date string in YYYY-MM-DD format."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        logger.warning("invalid_date_format", date_str=date_str)
        return None


def _parse_time(time_str: str | None) -> time | None:
    """Parse time string in HH:MM format."""
    if not time_str:
        return None
    try:
        return time.fromisoformat(time_str)
    except ValueError:
        logger.warning("invalid_time_format", time_str=time_str)
        return None


@register_tool(
    name="add_task",
    description="Create a new task for a user. Requires title. Supports description, priority (high/medium/low), category (work/personal/shopping/health/other), tags, due_date (YYYY-MM-DD), and due_time (HH:MM).",
    params_model=AddTaskParams,
)
@with_tool_logging("add_task")
async def add_task(params: AddTaskParams, db: AsyncSession) -> dict[str, Any]:
    """Create a new task for a user.

    Implements FR-010-014:
    - FR-010: Accept user_id (required), title (required), description (optional)
    - FR-011: Validate title length 1-200 chars (via Pydantic)
    - FR-012: Validate description max 1000 chars (via Pydantic)
    - FR-013: Return task_id, status "created", title
    - FR-014: Associate task with user_id

    Args:
        params: Validated AddTaskParams from request
        db: Database session

    Returns:
        AddTaskResponse dict with task_id, status, title

    Raises:
        ToolError: On database failure
    """
    try:
        # Parse optional date/time fields
        parsed_due_date = _parse_date(params.due_date)
        parsed_due_time = _parse_time(params.due_time)

        # Map priority and category enums
        priority = TaskPriority(params.priority.value)
        category = TaskCategory(params.category.value)

        # Create task with all fields
        task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description,
            priority=priority,
            category=category,
            tags=params.tags,
            due_date=parsed_due_date,
            due_time=parsed_due_time,
        )

        # Persist to database
        db.add(task)
        await db.flush()  # Get the ID without committing
        await db.commit()  # Commit immediately to ensure task is saved

        logger.info(
            "task_created",
            task_id=str(task.id),
            user_id=str(params.user_id),
            title=params.title,
            priority=priority.value,
            category=category.value,
            has_due_date=parsed_due_date is not None,
        )

        # Build response per FR-013
        return build_add_task_response(
            task_id=task.id,
            title=task.title,
        )

    except ToolError:
        raise
    except Exception as e:
        logger.error(
            "add_task_failed",
            error=str(e),
            user_id=str(params.user_id),
        )
        raise database_error(
            message="Failed to create task",
            operation="insert",
        ) from e
