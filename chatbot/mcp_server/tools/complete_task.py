# Task T018: Implement complete_task Tool
"""MCP Tool: complete_task - Toggle task completion status.

User Story 3 (P2): AI Agent Completes a Task
An AI agent marks a task as complete (or uncomplete) when the user
says something like "Mark 'Buy groceries' as done."

References:
- spec.md: FR-030-033 (complete_task requirements)
- spec.md: US3 acceptance scenarios
- contracts/mcp-tools.yaml: CompleteTaskParams, CompleteTaskResponse
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task
from mcp_server.schemas import CompleteTaskParams
from mcp_server.logging import with_tool_logging, get_logger
from mcp_server.tools import register_tool
from mcp_server.tools.base import (
    ToolError,
    task_not_found,
    unauthorized,
    database_error,
    build_complete_task_response,
)

logger = get_logger("tools.complete_task")


@register_tool(
    name="complete_task",
    description="Toggle a task's completion status (complete/uncomplete). Requires user_id and task_id.",
    params_model=CompleteTaskParams,
)
@with_tool_logging("complete_task")
async def complete_task(params: CompleteTaskParams, db: AsyncSession) -> dict[str, Any]:
    """Toggle task completion status.

    Implements FR-030-033:
    - FR-030: Accept user_id (required) and task_id (required)
    - FR-031: Toggle completion status (pending ↔ completed)
    - FR-032: Verify task belongs to user before modifying
    - FR-033: Return updated task status in response

    Args:
        params: Validated CompleteTaskParams from request
        db: Database session

    Returns:
        CompleteTaskResponse dict with task_id, status, title

    Raises:
        ToolError: On task not found, unauthorized, or database failure
    """
    try:
        # Find task by ID
        query = select(Task).where(Task.id == params.task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        # Check if task exists (US3 scenario 3)
        if task is None:
            raise task_not_found(params.task_id)

        # Check ownership (FR-032, US3 scenario 4)
        if task.user_id != params.user_id:
            raise unauthorized(params.user_id, params.task_id)

        # Toggle completion status (FR-031)
        task.completed = not task.completed

        # Update completed_at timestamp
        if task.completed:
            task.completed_at = datetime.now(UTC)
        else:
            task.completed_at = None

        # Update updated_at
        task.updated_at = datetime.now(UTC)

        await db.flush()

        logger.info(
            "task_completion_toggled",
            task_id=str(task.id),
            user_id=str(params.user_id),
            new_status="completed" if task.completed else "pending",
        )

        # Build response (FR-033)
        return build_complete_task_response(
            task_id=task.id,
            completed=task.completed,
            title=task.title,
        )

    except ToolError:
        raise
    except Exception as e:
        logger.error(
            "complete_task_failed",
            error=str(e),
            user_id=str(params.user_id),
            task_id=str(params.task_id),
        )
        raise database_error(
            message="Failed to update task completion",
            operation="update",
        ) from e
