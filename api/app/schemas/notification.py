"""Notification schemas."""

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Notification response model matching frontend expectations."""

    id: str
    userId: str
    taskId: str | None = None
    type: NotificationType
    message: str
    isRead: bool
    createdAt: str


class NotificationListResponse(BaseModel):
    """List notifications response."""

    notifications: list[NotificationResponse]
    total: int
    unreadCount: int


class UnreadCountResponse(BaseModel):
    """Unread count response (lightweight for polling)."""

    count: int


class ClearNotificationsResponse(BaseModel):
    """Clear all notifications response."""

    success: bool
    deletedCount: int
