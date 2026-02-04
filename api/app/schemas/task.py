"""Task schemas."""

from pydantic import BaseModel, Field

from app.models.task import TaskCategory, TaskPriority


class TaskResponse(BaseModel):
    """Task response model matching frontend expectations."""

    id: str
    userId: str
    title: str
    description: str | None = None
    priority: TaskPriority
    category: TaskCategory
    tags: list[str]
    dueDate: str | None = None
    dueTime: str | None = None
    completed: bool
    completedAt: str | None = None
    createdAt: str
    updatedAt: str


class TaskCounts(BaseModel):
    """Task count summary."""

    all: int
    pending: int
    completed: int


class CreateTaskRequest(BaseModel):
    """Create task request body."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.PERSONAL
    tags: list[str] = Field(default_factory=list)
    dueDate: str | None = None
    dueTime: str | None = None


class CreateTaskResponse(BaseModel):
    """Create task response."""

    task: TaskResponse


class UpdateTaskRequest(BaseModel):
    """Update task request body."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: TaskPriority | None = None
    category: TaskCategory | None = None
    tags: list[str] | None = None
    dueDate: str | None = None
    dueTime: str | None = None


class UpdateTaskResponse(BaseModel):
    """Update task response."""

    task: TaskResponse


class ListTasksParams(BaseModel):
    """Query parameters for listing tasks."""

    status: str | None = None  # "all" | "pending" | "completed"
    category: TaskCategory | None = None
    priority: TaskPriority | None = None
    page: int = 1
    pageSize: int = 50


class ListTasksResponse(BaseModel):
    """List tasks response."""

    tasks: list[TaskResponse]
    counts: TaskCounts


class ToggleCompleteResponse(BaseModel):
    """Toggle complete response."""

    task: TaskResponse


class DeleteTaskResponse(BaseModel):
    """Delete task response."""

    success: bool
    taskId: str
