# Task T011: Pydantic Parameter Models
"""Pydantic models for MCP tool parameters and responses.

All models are derived from contracts/mcp-tools.yaml OpenAPI spec.
These provide automatic validation for tool invocations.

References:
- contracts/mcp-tools.yaml: OpenAPI 3.1 schema definitions
- spec.md: FR-010-054 (tool parameter requirements)
"""

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# === Enums ===


class TaskStatus(str, Enum):
    """Task filter status options."""

    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class ErrorCode(str, Enum):
    """Machine-readable error codes per spec."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# === Tool Parameters ===


class TaskPriorityEnum(str, Enum):
    """Task priority levels for add_task."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategoryEnum(str, Enum):
    """Task category types for add_task."""
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


class AddTaskParams(BaseModel):
    """Parameters for add_task tool (FR-010-014).

    Attributes:
        user_id: User's unique identifier (required)
        title: Task title, 1-200 chars (required)
        description: Optional task description, max 1000 chars
        priority: Task priority (high/medium/low)
        category: Task category
        tags: List of tags
        due_date: Due date in YYYY-MM-DD format
        due_time: Due time in HH:MM format
    """

    user_id: UUID = Field(..., description="User's unique identifier")
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional task description",
    )
    priority: TaskPriorityEnum = Field(
        default=TaskPriorityEnum.MEDIUM,
        description="Task priority: high, medium, or low",
    )
    category: TaskCategoryEnum = Field(
        default=TaskCategoryEnum.PERSONAL,
        description="Task category: work, personal, shopping, health, other",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="List of tags for the task",
    )
    due_date: str | None = Field(
        default=None,
        description="Due date in YYYY-MM-DD format",
    )
    due_time: str | None = Field(
        default=None,
        description="Due time in HH:MM format (24-hour)",
    )

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, v: str) -> str:
        """Validate title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool (FR-020-024).

    Attributes:
        user_id: User's unique identifier (required)
        status: Filter by task status (default: all)
    """

    user_id: UUID = Field(..., description="User's unique identifier")
    status: TaskStatus = Field(
        default=TaskStatus.ALL,
        description="Filter by task status",
    )


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool (FR-030-033).

    Attributes:
        user_id: User's unique identifier (required)
        task_id: Task to complete/uncomplete (required)
    """

    user_id: UUID = Field(..., description="User's unique identifier")
    task_id: UUID = Field(..., description="Task to complete/uncomplete")


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool (FR-040-043).

    Attributes:
        user_id: User's unique identifier (required)
        task_id: Task to delete (required)
    """

    user_id: UUID = Field(..., description="User's unique identifier")
    task_id: UUID = Field(..., description="Task to delete")


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool (FR-050-054).

    At least one updatable field must be provided.

    Attributes:
        user_id: User's unique identifier (required)
        task_id: Task to update (required)
        title: New title, 1-200 chars (optional)
        description: New description, max 1000 chars (optional)
        priority: New priority: high, medium, or low (optional)
        category: New category (optional)
        tags: New list of tags (optional)
        due_date: New due date in YYYY-MM-DD format (optional)
        due_time: New due time in HH:MM format (optional)
        clear_due_date: Set to true to remove due date (optional)
        clear_due_time: Set to true to remove due time (optional)
        clear_description: Set to true to remove description (optional)
    """

    user_id: UUID = Field(..., description="User's unique identifier")
    task_id: UUID = Field(..., description="Task to update")
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New title",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="New description",
    )
    priority: TaskPriorityEnum | None = Field(
        default=None,
        description="New priority: high, medium, or low",
    )
    category: TaskCategoryEnum | None = Field(
        default=None,
        description="New category: work, personal, shopping, health, other",
    )
    tags: list[str] | None = Field(
        default=None,
        description="New list of tags (replaces existing tags)",
    )
    due_date: str | None = Field(
        default=None,
        description="New due date in YYYY-MM-DD format",
    )
    due_time: str | None = Field(
        default=None,
        description="New due time in HH:MM format (24-hour)",
    )
    clear_due_date: bool = Field(
        default=False,
        description="Set to true to remove the due date",
    )
    clear_due_time: bool = Field(
        default=False,
        description="Set to true to remove the due time",
    )
    clear_description: bool = Field(
        default=False,
        description="Set to true to remove the description",
    )

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, v: str | None) -> str | None:
        """Validate title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else None

    def model_post_init(self, __context: Any) -> None:
        """Validate at least one field to update is provided (FR-051)."""
        has_update = any([
            self.title is not None,
            self.description is not None,
            self.priority is not None,
            self.category is not None,
            self.tags is not None,
            self.due_date is not None,
            self.due_time is not None,
            self.clear_due_date,
            self.clear_due_time,
            self.clear_description,
        ])
        if not has_update:
            raise ValueError("At least one field must be provided to update")


# === Response Models ===


class TaskSummary(BaseModel):
    """Task summary for list responses.

    Attributes:
        id: Task unique identifier
        title: Task title
        description: Task description (may be null)
        completed: Completion status
        priority: Task priority level
        category: Task category
        created_at: Creation timestamp
    """

    id: UUID
    title: str
    description: str | None = None
    completed: bool
    priority: str = "medium"
    category: str = "personal"
    created_at: str  # ISO format datetime string


class AddTaskResponse(BaseModel):
    """Response for add_task tool."""

    task_id: UUID
    status: str = "created"
    title: str


class ListTasksResponse(BaseModel):
    """Response for list_tasks tool."""

    tasks: list[TaskSummary]


class CompleteTaskResponse(BaseModel):
    """Response for complete_task tool."""

    task_id: UUID
    status: str  # "completed" or "pending"
    title: str


class DeleteTaskResponse(BaseModel):
    """Response for delete_task tool."""

    task_id: UUID
    status: str = "deleted"
    title: str


class UpdateTaskResponse(BaseModel):
    """Response for update_task tool."""

    task_id: UUID
    status: str = "updated"
    title: str
    description: str | None = None


# === Error Response ===


class ErrorResponse(BaseModel):
    """Error response for tool failures.

    Per spec.md error handling requirements.
    """

    status: str = "error"
    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None


# === Tool Call Types ===


class ToolCallRequest(BaseModel):
    """Request to execute an MCP tool."""

    tool: str = Field(..., description="Name of the tool to execute")
    parameters: dict[str, Any] = Field(..., description="Tool-specific parameters")


class ToolCallResponse(BaseModel):
    """Response from MCP tool execution."""

    status: str = Field(..., description="success or error")
    data: dict[str, Any] | None = None
    error: ErrorResponse | None = None
