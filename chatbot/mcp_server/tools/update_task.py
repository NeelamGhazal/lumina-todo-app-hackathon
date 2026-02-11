# Task T022: Implement update_task Tool
"""MCP Tool: update_task - Update any task field.

User Story 5 (P3): AI Agent Updates a Task
An AI agent modifies an existing task when the user wants to change details.

References:
- spec.md: FR-050-054 (update_task requirements)
- spec.md: US5 acceptance scenarios
- contracts/mcp-tools.yaml: UpdateTaskParams, UpdateTaskResponse
"""

from datetime import UTC, datetime, date, time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task, TaskPriority, TaskCategory
from mcp_server.schemas import UpdateTaskParams
from mcp_server.logging import with_tool_logging, get_logger
from mcp_server.tools import register_tool
from mcp_server.tools.base import (
    ToolError,
    task_not_found,
    unauthorized,
    database_error,
    build_update_task_response,
)

logger = get_logger("tools.update_task")


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
    name="update_task",
    description="Update any task field: title, description, priority, category, tags, due_date, due_time. Only updates fields that are explicitly provided.",
    params_model=UpdateTaskParams,
)
@with_tool_logging("update_task")
async def update_task(params: UpdateTaskParams, db: AsyncSession) -> dict[str, Any]:
    """Update task fields - ONLY the fields explicitly provided.

    Implements FR-050-054:
    - FR-050: Accept user_id, task_id (required), and optional update fields
    - FR-051: Require at least one field to update (validated by Pydantic)
    - FR-052: Apply same validation as add_task for updated fields
    - FR-053: Verify task belongs to user before updating
    - FR-054: Return updated task data in response

    STRICT FIELD MAPPING:
    - Only updates fields that are explicitly provided
    - Does NOT infer or guess missing fields
    - Preserves existing values for unspecified fields

    Args:
        params: Validated UpdateTaskParams from request
        db: Database session

    Returns:
        UpdateTaskResponse dict with task_id, status "updated", and updated fields

    Raises:
        ToolError: On task not found, unauthorized, or database failure
    """
    try:
        # Find task by ID
        query = select(Task).where(Task.id == params.task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        # Check if task exists
        if task is None:
            raise task_not_found(params.task_id)

        # Check ownership (FR-053, US5 scenario 4)
        if task.user_id != params.user_id:
            raise unauthorized(params.user_id, params.task_id)

        # Track what was updated for logging
        updates = []

        # Update title if provided
        if params.title is not None:
            task.title = params.title
            updates.append("title")

        # Update description if provided OR clear if requested
        if params.clear_description:
            task.description = None
            updates.append("description (cleared)")
        elif params.description is not None:
            task.description = params.description
            updates.append("description")

        # Update priority if provided
        if params.priority is not None:
            task.priority = TaskPriority(params.priority.value)
            updates.append("priority")

        # Update category if provided
        if params.category is not None:
            task.category = TaskCategory(params.category.value)
            updates.append("category")

        # Update tags if provided (replaces existing tags)
        if params.tags is not None:
            task.tags = params.tags
            updates.append("tags")

        # Update due_date if provided OR clear if requested
        if params.clear_due_date:
            task.due_date = None
            updates.append("due_date (cleared)")
        elif params.due_date is not None:
            parsed_date = _parse_date(params.due_date)
            if parsed_date:
                task.due_date = parsed_date
                updates.append("due_date")

        # Update due_time if provided OR clear if requested
        if params.clear_due_time:
            task.due_time = None
            updates.append("due_time (cleared)")
        elif params.due_time is not None:
            parsed_time = _parse_time(params.due_time)
            if parsed_time:
                task.due_time = parsed_time
                updates.append("due_time")

        # Update timestamp
        task.updated_at = datetime.now(UTC)

        await db.flush()
        await db.commit()

        logger.info(
            "task_updated",
            task_id=str(task.id),
            user_id=str(params.user_id),
            updated_fields=updates,
        )

        # Build response (FR-054)
        return build_update_task_response(
            task_id=task.id,
            title=task.title,
            description=task.description,
        )

    except ToolError:
        raise
    except Exception as e:
        logger.error(
            "update_task_failed",
            error=str(e),
            user_id=str(params.user_id),
            task_id=str(params.task_id),
        )
        raise database_error(
            message="Failed to update task",
            operation="update",
        ) from e
