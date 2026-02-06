# Task T001: Create SQLModel Classes
"""SQLModel entities for Phase III MCP Server.

Entities:
- Task: Todo item (from Phase II, direct database access)
- Conversation: Interaction session between AI agent and user
- Message: Single exchange within a conversation
- MessageRole: Enum for message sender role

References:
- data-model.md: Entity definitions
- spec.md: FR-070, FR-071, FR-072 (database requirements)
- api/app/models/task.py: Phase II Task model (copied for direct access)
"""

from datetime import UTC, datetime, date, time
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, JSON


# === Phase II Models (copied for direct database access per ADR-002) ===


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
    """Task database model (from Phase II).

    This is a copy of api/app/models/task.py for direct database access.
    Per ADR-002: MCP server accesses database directly, not via Phase II API.

    Attributes:
        id: Unique task identifier
        user_id: Owner's user ID
        title: Task title (max 200 chars)
        description: Optional description (max 1000 chars)
        priority: Priority level (high/medium/low)
        category: Category type
        tags: List of tags
        due_date: Optional due date
        due_time: Optional due time
        completed: Completion status
        completed_at: When task was completed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)  # No FK - Phase II schema doesn't enforce
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


# === Phase III Models ===


class MessageRole(str, Enum):
    """Message sender role.

    Per ADR-004: Only user and assistant messages are stored.
    Tool call internals are not persisted.
    """

    USER = "user"
    ASSISTANT = "assistant"


class Conversation(SQLModel, table=True):
    """Conversation session between AI agent and user.

    Lifecycle (per spec clarification):
    - New conversation created when user has no active conversation
    - Or when last_activity exceeds 30-minute timeout
    - Conversations are never deleted (audit trail)

    Note: user_id is not a foreign key constraint because the User model
    is in the api/ project. User validation happens at the agent layer
    before MCP tools are invoked (per spec assumptions).

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Reference to users.id (validated at application layer)
        created_at: When conversation started
        last_activity: Last message timestamp (updated on every message)
    """

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)  # No FK - validated at agent layer
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Message(SQLModel, table=True):
    """Single message within a conversation.

    Per ADR-004: Only user and assistant messages are stored.
    Tool call results are NOT stored as messages.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to conversations.id
        role: Message sender (user or assistant)
        content: Message content text
        created_at: When message was created
    """

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
