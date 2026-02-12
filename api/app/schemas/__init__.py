"""Pydantic schemas for API request/response."""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    SessionResponse,
    UserResponse,
)
from app.schemas.notification import (
    ClearNotificationsResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
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
    # Notification
    "ClearNotificationsResponse",
    "NotificationListResponse",
    "NotificationResponse",
    "UnreadCountResponse",
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
