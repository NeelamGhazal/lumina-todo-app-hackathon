# Task T013: Base Tool Utilities
"""Base utilities for MCP tool implementations.

Provides:
- Error handling helpers
- Response builders
- Common validation utilities

References:
- spec.md: FR-005 (standardized error responses)
- contracts/mcp-tools.yaml: ErrorResponse schema
"""

from typing import Any
from uuid import UUID

from mcp_server.schemas import (
    ErrorCode,
    ErrorResponse,
    AddTaskResponse,
    ListTasksResponse,
    CompleteTaskResponse,
    DeleteTaskResponse,
    UpdateTaskResponse,
    TaskSummary,
)


class ToolError(Exception):
    """Exception raised by tool handlers.

    Captures structured error information for MCP responses.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """Initialize tool error.

        Args:
            code: Machine-readable error code
            message: Human-readable error message
            details: Additional error context
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_response(self) -> ErrorResponse:
        """Convert to ErrorResponse model."""
        return ErrorResponse(
            code=self.code,
            message=self.message,
            details=self.details,
        )


# === Error Helpers ===


def validation_error(message: str, field: str | None = None) -> ToolError:
    """Create a validation error.

    Args:
        message: Error message
        field: Field that failed validation (optional)

    Returns:
        ToolError with VALIDATION_ERROR code
    """
    details = {"field": field} if field else None
    return ToolError(
        code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details,
    )


def task_not_found(task_id: UUID) -> ToolError:
    """Create a task not found error.

    Args:
        task_id: ID of the missing task

    Returns:
        ToolError with TASK_NOT_FOUND code
    """
    return ToolError(
        code=ErrorCode.TASK_NOT_FOUND,
        message=f"Task {task_id} not found",
        details={"task_id": str(task_id)},
    )


def unauthorized(user_id: UUID, task_id: UUID) -> ToolError:
    """Create an unauthorized access error.

    Args:
        user_id: User attempting access
        task_id: Task being accessed

    Returns:
        ToolError with UNAUTHORIZED code
    """
    return ToolError(
        code=ErrorCode.UNAUTHORIZED,
        message="You do not have permission to access this task",
        details={"user_id": str(user_id), "task_id": str(task_id)},
    )


def database_error(message: str, operation: str | None = None) -> ToolError:
    """Create a database error.

    Args:
        message: Error message
        operation: Database operation that failed

    Returns:
        ToolError with DATABASE_ERROR code
    """
    details = {"operation": operation} if operation else None
    return ToolError(
        code=ErrorCode.DATABASE_ERROR,
        message=message,
        details=details,
    )


def internal_error(message: str = "An internal error occurred") -> ToolError:
    """Create an internal error.

    Args:
        message: Error message

    Returns:
        ToolError with INTERNAL_ERROR code
    """
    return ToolError(
        code=ErrorCode.INTERNAL_ERROR,
        message=message,
    )


# === Response Builders ===


def build_add_task_response(task_id: UUID, title: str) -> dict[str, Any]:
    """Build response for add_task tool.

    Args:
        task_id: Created task ID
        title: Task title

    Returns:
        Dict matching AddTaskResponse schema
    """
    return AddTaskResponse(
        task_id=task_id,
        status="created",
        title=title,
    ).model_dump(mode="json")


def build_list_tasks_response(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Build response for list_tasks tool.

    Args:
        tasks: List of task dicts

    Returns:
        Dict matching ListTasksResponse schema
    """
    task_summaries = [
        TaskSummary(
            id=t["id"],
            title=t["title"],
            description=t.get("description"),
            completed=t["completed"],
            priority=t.get("priority", "medium"),
            category=t.get("category", "personal"),
            created_at=t["created_at"],
        )
        for t in tasks
    ]
    return ListTasksResponse(tasks=task_summaries).model_dump(mode="json")


def build_complete_task_response(
    task_id: UUID, completed: bool, title: str
) -> dict[str, Any]:
    """Build response for complete_task tool.

    Args:
        task_id: Task ID
        completed: New completion status
        title: Task title

    Returns:
        Dict matching CompleteTaskResponse schema
    """
    return CompleteTaskResponse(
        task_id=task_id,
        status="completed" if completed else "pending",
        title=title,
    ).model_dump(mode="json")


def build_delete_task_response(task_id: UUID, title: str) -> dict[str, Any]:
    """Build response for delete_task tool.

    Args:
        task_id: Deleted task ID
        title: Task title

    Returns:
        Dict matching DeleteTaskResponse schema
    """
    return DeleteTaskResponse(
        task_id=task_id,
        status="deleted",
        title=title,
    ).model_dump(mode="json")


def build_update_task_response(
    task_id: UUID,
    title: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Build response for update_task tool.

    Args:
        task_id: Updated task ID
        title: Task title
        description: Task description

    Returns:
        Dict matching UpdateTaskResponse schema
    """
    return UpdateTaskResponse(
        task_id=task_id,
        status="updated",
        title=title,
        description=description,
    ).model_dump(mode="json")


def build_error_response(error: ToolError) -> dict[str, Any]:
    """Build error response from ToolError.

    Args:
        error: ToolError exception

    Returns:
        Dict matching ErrorResponse schema
    """
    return error.to_response().model_dump(mode="json")


# Export public API
__all__ = [
    # Exception
    "ToolError",
    # Error helpers
    "validation_error",
    "task_not_found",
    "unauthorized",
    "database_error",
    "internal_error",
    # Response builders
    "build_add_task_response",
    "build_list_tasks_response",
    "build_complete_task_response",
    "build_delete_task_response",
    "build_update_task_response",
    "build_error_response",
]
