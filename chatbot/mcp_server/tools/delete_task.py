# Task T020: Implement delete_task Tool
"""MCP Tool: delete_task - Permanently remove a task.

User Story 4 (P2): AI Agent Deletes a Task
An AI agent permanently removes a task when the user requests deletion.

References:
- spec.md: FR-040-043 (delete_task requirements)
- spec.md: US4 acceptance scenarios
- contracts/mcp-tools.yaml: DeleteTaskParams, DeleteTaskResponse
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task
from mcp_server.schemas import DeleteTaskParams
from mcp_server.logging import with_tool_logging, get_logger
from mcp_server.tools import register_tool
from mcp_server.tools.base import (
    ToolError,
    task_not_found,
    unauthorized,
    database_error,
    build_delete_task_response,
)

logger = get_logger("tools.delete_task")


@register_tool(
    name="delete_task",
    description="Permanently delete a task. Requires user_id and task_id.",
    params_model=DeleteTaskParams,
)
@with_tool_logging("delete_task")
async def delete_task(params: DeleteTaskParams, db: AsyncSession) -> dict[str, Any]:
    """Permanently delete a task.

    Implements FR-040-043:
    - FR-040: Accept user_id (required) and task_id (required)
    - FR-041: Permanently remove task from database
    - FR-042: Verify task belongs to user before deleting
    - FR-043: Return confirmation with deleted task's id and title

    Args:
        params: Validated DeleteTaskParams from request
        db: Database session

    Returns:
        DeleteTaskResponse dict with task_id, status "deleted", title

    Raises:
        ToolError: On task not found, unauthorized, or database failure
    """
    try:
        # Find task by ID
        query = select(Task).where(Task.id == params.task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        # Check if task exists (US4 scenario 2)
        if task is None:
            raise task_not_found(params.task_id)

        # Check ownership (FR-042, US4 scenario 3)
        if task.user_id != params.user_id:
            raise unauthorized(params.user_id, params.task_id)

        # Store title for response before deletion
        task_title = task.title
        task_id = task.id

        # Delete task (FR-041)
        await db.delete(task)
        await db.flush()

        logger.info(
            "task_deleted",
            task_id=str(task_id),
            user_id=str(params.user_id),
            title=task_title,
        )

        # Build response (FR-043)
        return build_delete_task_response(
            task_id=task_id,
            title=task_title,
        )

    except ToolError:
        raise
    except Exception as e:
        logger.error(
            "delete_task_failed",
            error=str(e),
            user_id=str(params.user_id),
            task_id=str(params.task_id),
        )
        raise database_error(
            message="Failed to delete task",
            operation="delete",
        ) from e
