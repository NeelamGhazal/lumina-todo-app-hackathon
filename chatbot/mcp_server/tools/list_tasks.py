# Task T016: Implement list_tasks Tool
"""MCP Tool: list_tasks - List tasks for a user with optional filtering.

User Story 2 (P1): AI Agent Lists User's Tasks
An AI agent retrieves a user's tasks to answer questions like
"What's on my todo list?" or "Show me my completed tasks."

References:
- spec.md: FR-020-024 (list_tasks requirements)
- spec.md: US2 acceptance scenarios
- contracts/mcp-tools.yaml: ListTasksParams, ListTasksResponse
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Task
from mcp_server.schemas import ListTasksParams, TaskStatus
from mcp_server.logging import with_tool_logging, get_logger
from mcp_server.tools import register_tool
from mcp_server.tools.base import (
    database_error,
    build_list_tasks_response,
)

logger = get_logger("tools.list_tasks")


@register_tool(
    name="list_tasks",
    description="List tasks for a user. Optionally filter by status (all, pending, completed).",
    params_model=ListTasksParams,
)
@with_tool_logging("list_tasks")
async def list_tasks(params: ListTasksParams, db: AsyncSession) -> dict[str, Any]:
    """List tasks for a user with optional status filtering.

    Implements FR-020-024:
    - FR-020: Accept user_id (required), status filter (optional)
    - FR-021: Default to "all" when status not provided
    - FR-022: Return only tasks belonging to user_id
    - FR-023: Return tasks as array with id, title, description, completed
    - FR-024: Return empty array when user has no tasks

    Args:
        params: Validated ListTasksParams from request
        db: Database session

    Returns:
        ListTasksResponse dict with tasks array

    Raises:
        ToolError: On database failure
    """
    try:
        # Build query for user's tasks
        query = select(Task).where(Task.user_id == params.user_id)

        # Apply status filter (FR-020, FR-021)
        if params.status == TaskStatus.PENDING:
            query = query.where(Task.completed == False)  # noqa: E712
        elif params.status == TaskStatus.COMPLETED:
            query = query.where(Task.completed == True)  # noqa: E712
        # TaskStatus.ALL - no additional filter

        # Order by creation date (newest first)
        query = query.order_by(Task.created_at.desc())

        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()

        logger.info(
            "tasks_listed",
            user_id=str(params.user_id),
            status_filter=params.status.value,
            task_count=len(tasks),
        )

        # Convert to response format (FR-023)
        task_dicts = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value if task.priority else "medium",
                "category": task.category.value if task.category else "personal",
                "created_at": task.created_at.isoformat() if task.created_at else None,
            }
            for task in tasks
        ]

        # Build response (empty array if no tasks per FR-024)
        return build_list_tasks_response(task_dicts)

    except Exception as e:
        logger.error(
            "list_tasks_failed",
            error=str(e),
            user_id=str(params.user_id),
        )
        raise database_error(
            message="Failed to list tasks",
            operation="select",
        ) from e
