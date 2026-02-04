"""Task database model."""

from datetime import UTC, datetime, date, time
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, JSON


class TaskPriority(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategory(str, Enum):
    """Task category types."""

    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


class Task(SQLModel, table=True):
    """Task database model."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    category: TaskCategory = Field(default=TaskCategory.PERSONAL)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: date | None = Field(default=None)
    due_time: time | None = Field(default=None)
    completed: bool = Field(default=False)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
