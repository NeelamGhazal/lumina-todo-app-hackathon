# Data Model: MCP Server for Todo Operations

**Feature**: 005-mcp-todo-server
**Date**: 2026-02-06
**Status**: Complete

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXISTING (Phase II)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐         ┌─────────────────────────────────────┐    │
│  │      User       │         │               Task                   │    │
│  ├─────────────────┤         ├─────────────────────────────────────┤    │
│  │ id (UUID) PK    │────1:N──│ id (UUID) PK                        │    │
│  │ email           │         │ user_id (UUID) FK                   │    │
│  │ password_hash   │         │ title (str, 200)                    │    │
│  │ name            │         │ description (str, 1000, nullable)   │    │
│  │ created_at      │         │ priority (enum)                     │    │
│  │ updated_at      │         │ category (enum)                     │    │
│  └─────────────────┘         │ tags (JSON array)                   │    │
│                               │ due_date (date, nullable)           │    │
│                               │ due_time (time, nullable)           │    │
│                               │ completed (bool)                    │    │
│                               │ completed_at (datetime, nullable)   │    │
│                               │ created_at (datetime)               │    │
│                               │ updated_at (datetime)               │    │
│                               └─────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           NEW (Phase III)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐         ┌─────────────────────────────────────┐    │
│  │  Conversation   │         │              Message                 │    │
│  ├─────────────────┤         ├─────────────────────────────────────┤    │
│  │ id (UUID) PK    │────1:N──│ id (UUID) PK                        │    │
│  │ user_id (UUID)  │         │ conversation_id (UUID) FK           │    │
│  │ created_at      │         │ role (enum: user|assistant)         │    │
│  │ last_activity   │         │ content (text)                      │    │
│  └─────────────────┘         │ created_at (datetime)               │    │
│         │                     └─────────────────────────────────────┘    │
│         │                                                                │
│         └────────────────────────────────────────────────────────────    │
│                        user_id references User.id                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Entities

### Task (Existing - Phase II)

**Table Name**: `tasks`
**Description**: Represents a todo item owned by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique task identifier |
| user_id | UUID | FK(users.id), index, NOT NULL | Owner of the task |
| title | str | max_length=200, NOT NULL | Task title |
| description | str | max_length=1000, nullable | Detailed description |
| priority | enum | default=MEDIUM | HIGH, MEDIUM, LOW |
| category | enum | default=PERSONAL | WORK, PERSONAL, SHOPPING, HEALTH, OTHER |
| tags | JSON | default=[] | Array of string tags |
| due_date | date | nullable | Due date |
| due_time | time | nullable | Due time |
| completed | bool | default=False | Completion status |
| completed_at | datetime | nullable | When task was completed |
| created_at | datetime | default=now(UTC) | Creation timestamp |
| updated_at | datetime | default=now(UTC) | Last update timestamp |

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for user-scoped queries)

**Note**: This entity is READ from Phase II. The MCP server will read/write using the same model definition.

---

### Conversation (New - Phase III)

**Table Name**: `conversations`
**Description**: Represents an interaction session between AI agent and user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique conversation identifier |
| user_id | UUID | FK(users.id), index, NOT NULL | User in conversation |
| created_at | datetime | default=now(UTC) | When conversation started |
| last_activity | datetime | default=now(UTC) | Last message timestamp |

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for user-scoped queries)
- Index on `(user_id, last_activity)` (for active conversation lookup)

**Lifecycle Rules**:
- New conversation created when user has no active conversation OR last_activity > 30 minutes ago
- `last_activity` updated on every message
- Conversations are never deleted (audit trail)

**SQLModel Definition**:
```python
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation session between AI agent and user."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

---

### Message (New - Phase III)

**Table Name**: `messages`
**Description**: Represents a single exchange within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique message identifier |
| conversation_id | UUID | FK(conversations.id), index, NOT NULL | Parent conversation |
| role | enum | NOT NULL | "user" or "assistant" |
| content | text | NOT NULL | Message content |
| created_at | datetime | default=now(UTC) | When message was created |

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` (for conversation history queries)
- Index on `(conversation_id, created_at)` (for ordered message retrieval)

**Role Enum**:
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
```

**Note**: Tool call results are NOT stored as messages (per spec clarification). Only user input and assistant responses are persisted.

**SQLModel Definition**:
```python
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Single message within a conversation."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

---

## State Transitions

### Task Completion State

```
┌──────────┐                      ┌───────────┐
│ pending  │──── complete_task ──▶│ completed │
│          │◀─── complete_task ───│           │
└──────────┘      (toggle)        └───────────┘
```

- `completed = False` → "pending"
- `completed = True` → "completed"
- `complete_task` toggles between states
- `completed_at` set when transitioning to completed, cleared when returning to pending

### Conversation Lifecycle State

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────────┐    ┌────────┐    ┌──────────┐         ┌─────┴─────┐
│   none   │───▶│ active │───▶│ inactive │────────▶│  expired  │
│          │    │        │    │ (<30min) │         │ (>=30min) │
└──────────┘    └────────┘    └──────────┘         └───────────┘
  (no conv)    (has messages)  (waiting)            (start new)
                    │                                     │
                    └─────────────────────────────────────┘
                          new message reactivates
```

---

## Validation Rules

### Task Title
- Required
- Length: 1-200 characters
- UTF-8 encoded
- Trimmed (no leading/trailing whitespace)

### Task Description
- Optional
- Length: 0-1000 characters
- UTF-8 encoded

### User ID
- Required on all tool calls
- Must be valid UUID format
- Must reference existing user in database

### Task ID
- Required on complete/delete/update operations
- Must be positive integer (legacy) or valid UUID
- Must belong to the requesting user

---

## Database Migration

### Migration Script (Alembic)

```python
"""Add Phase III conversation tables.

Revision ID: 005_add_conversations
Revises: [previous_revision]
Create Date: 2026-02-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '005_add_conversations'
down_revision = '[previous_revision]'


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_user_activity', 'conversations', ['user_id', 'last_activity'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Get User's Tasks (list_tasks)
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND (completed = :completed OR :status = 'all')
ORDER BY created_at DESC;
```

### Get Active Conversation
```sql
SELECT * FROM conversations
WHERE user_id = :user_id
  AND last_activity > NOW() - INTERVAL '30 minutes'
ORDER BY last_activity DESC
LIMIT 1;
```

### Get Conversation Messages
```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC;
```

### Verify Task Ownership
```sql
SELECT id FROM tasks
WHERE id = :task_id AND user_id = :user_id;
```
