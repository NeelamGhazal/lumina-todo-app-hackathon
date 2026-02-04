"""Pydantic schemas for API request/response."""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    SessionResponse,
    UserResponse,
)
from app.schemas.task import (
    CreateTaskRequest,
    CreateTaskResponse,
    DeleteTaskResponse,
    ListTasksParams,
    ListTasksResponse,
    TaskResponse,
    ToggleCompleteResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "RegisterResponse",
    "SessionResponse",
    "UserResponse",
    # Task
    "CreateTaskRequest",
    "CreateTaskResponse",
    "DeleteTaskResponse",
    "ListTasksParams",
    "ListTasksResponse",
    "TaskResponse",
    "ToggleCompleteResponse",
    "UpdateTaskRequest",
    "UpdateTaskResponse",
]
