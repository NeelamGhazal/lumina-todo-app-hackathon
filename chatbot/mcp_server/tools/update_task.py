# Task T022: Implement update_task Tool
"""MCP Tool: update_task - Update task title and/or description.

User Story 5 (P3): AI Agent Updates a Task
An AI agent modifies an existing task when the user wants to change details.

References:
- spec.md: FR-050-054 (update_task requirements)
- spec.md: US5 acceptance scenarios
- contracts/mcp-tools.yaml: UpdateTaskParams, UpdateTaskResponse
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task
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


@register_tool(
    name="update_task",
    description="Update a task's title and/or description. At least one field must be provided.",
    params_model=UpdateTaskParams,
)
@with_tool_logging("update_task")
async def update_task(params: UpdateTaskParams, db: AsyncSession) -> dict[str, Any]:
    """Update task title and/or description.

    Implements FR-050-054:
    - FR-050: Accept user_id, task_id (required), title, description (optional)
    - FR-051: Require at least one field to update (validated by Pydantic)
    - FR-052: Apply same validation as add_task for updated fields
    - FR-053: Verify task belongs to user before updating
    - FR-054: Return updated task data in response

    Args:
        params: Validated UpdateTaskParams from request
        db: Database session

    Returns:
        UpdateTaskResponse dict with task_id, status "updated", title, description

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

        # Update title if provided (US5 scenario 1)
        if params.title is not None:
            task.title = params.title
            updates.append("title")

        # Update description if provided (US5 scenario 2)
        if params.description is not None:
            task.description = params.description
            updates.append("description")

        # Update timestamp
        task.updated_at = datetime.now(UTC)

        await db.flush()

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
