# Task T006, T007, T008, T009: Data Models per data-model.md
"""Task model and related enumerations for Todo CLI."""

from datetime import date, time, datetime
from enum import Enum
from typing import Optional
import random
import string

from pydantic import BaseModel, Field, field_validator


# Task T006: Implement Priority enum
class Priority(str, Enum):
    """Task priority levels with string values for serialization."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Task T007: Implement Category enum
class Category(str, Enum):
    """Task category types with string values for serialization."""
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


# Task T008: Implement Task Pydantic model
class Task(BaseModel):
    """
    Represents a todo item in the system.

    All fields per data-model.md specification.
    """
    # Identity
    id: str = Field(
        ...,
        description="6-character lowercase alphanumeric ID",
        pattern=r"^[a-z0-9]{6}$",
        examples=["a1b2c3", "x9y8z7"]
    )

    # Core fields
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (required)"
    )

    description: str = Field(
        default="",
        max_length=2000,
        description="Optional detailed description"
    )

    # Classification
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level"
    )

    category: Category = Field(
        default=Category.OTHER,
        description="Task category"
    )

    tags: list[str] = Field(
        default_factory=list,
        description="List of tags for organization"
    )

    # Scheduling
    due_date: Optional[date] = Field(
        default=None,
        description="Optional due date"
    )

    due_time: Optional[time] = Field(
        default=None,
        description="Optional due time"
    )

    # Status
    is_completed: bool = Field(
        default=False,
        description="Completion status"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )

    model_config = {
        "frozen": False,  # Allow mutation for updates
        "use_enum_values": True,  # Use enum values in serialization
    }

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v: str) -> str:
        """Strip leading/trailing whitespace from title."""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def clean_tags(cls, v: list[str]) -> list[str]:
        """Clean tags: trim whitespace, remove empty, deduplicate (case-insensitive)."""
        if not v:
            return []
        seen: set[str] = set()
        result: list[str] = []
        for tag in v:
            if isinstance(tag, str):
                tag = tag.strip()
                if tag and tag.lower() not in seen:
                    seen.add(tag.lower())
                    result.append(tag)
        return result


# Task T009: Implement generate_id function per ADR-001
def generate_id(existing_ids: set[str] | None = None) -> str:
    """
    Generate a unique 6-character lowercase alphanumeric ID.

    Per ADR-001: 6-char format provides 2.1B combinations.
    Uses collision detection when existing_ids is provided.

    Args:
        existing_ids: Set of existing IDs to avoid collisions.

    Returns:
        A unique 6-character ID string.
    """
    if existing_ids is None:
        existing_ids = set()

    charset = string.ascii_lowercase + string.digits

    while True:
        new_id = ''.join(random.choices(charset, k=6))
        if new_id not in existing_ids:
            return new_id
