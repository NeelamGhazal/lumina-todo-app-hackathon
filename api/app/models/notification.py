"""Notification database model."""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    """Notification type categories."""

    TASK_DUE_SOON = "TASK_DUE_SOON"
    TASK_OVERDUE = "TASK_OVERDUE"
    TASK_COMPLETED = "TASK_COMPLETED"


class Notification(SQLModel, table=True):
    """Notification database model."""

    __tablename__ = "notifications"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    task_id: UUID | None = Field(default=None, foreign_key="tasks.id")
    type: NotificationType
    message: str = Field(max_length=500)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
