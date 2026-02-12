# Data Model: In-App Notifications

**Feature**: 009-notifications | **Date**: 2026-02-12

## Notification Entity

### Schema Definition

```
Notification
├── id: UUID (PK)
├── user_id: UUID (FK → users.id, indexed)
├── task_id: UUID | None (FK → tasks.id, nullable)
├── type: NotificationType (enum)
├── message: str (max 500 chars)
├── is_read: bool (default: false)
└── created_at: datetime (indexed, default: now)
```

### NotificationType Enum

| Value | Description | Trigger |
|-------|-------------|---------|
| `TASK_DUE_SOON` | Task due tomorrow | Hourly cron, day before due_date |
| `TASK_OVERDUE` | Task past due date | Hourly cron, after due_date |
| `TASK_COMPLETED` | Task marked complete | Inline, when task.completed = true |

### Relationships

```
User (1) ──────< (N) Notification
Task (1) ──────< (N) Notification (optional)
```

- One user has many notifications
- One task can have multiple notifications (due_soon, overdue, completed)
- task_id is nullable (future notification types may not relate to tasks)

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_notifications_user_id` | user_id | Filter by user |
| `ix_notifications_task_type` | task_id, type | Duplicate prevention |
| `ix_notifications_created_at` | created_at | Ordering, cleanup queries |

### SQLModel Definition

```python
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    TASK_DUE_SOON = "TASK_DUE_SOON"
    TASK_OVERDUE = "TASK_OVERDUE"
    TASK_COMPLETED = "TASK_COMPLETED"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    task_id: UUID | None = Field(default=None, foreign_key="tasks.id")
    type: NotificationType
    message: str = Field(max_length=500)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

## Query Patterns

### List User Notifications (newest first, limit 20)

```sql
SELECT * FROM notifications
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 20
```

### Get Unread Count

```sql
SELECT COUNT(*) FROM notifications
WHERE user_id = ? AND is_read = false
```

### Check Duplicate (before creating due_soon/overdue)

```sql
SELECT EXISTS(
  SELECT 1 FROM notifications
  WHERE task_id = ? AND type = ?
)
```

### Find Tasks Due Tomorrow (for due_soon notifications)

```sql
SELECT t.* FROM tasks t
WHERE t.due_date = DATE('now', '+1 day')
  AND t.completed = false
  AND NOT EXISTS (
    SELECT 1 FROM notifications n
    WHERE n.task_id = t.id AND n.type = 'TASK_DUE_SOON'
  )
```

### Find Overdue Tasks (for overdue notifications)

```sql
SELECT t.* FROM tasks t
WHERE t.due_date < DATE('now')
  AND t.completed = false
  AND NOT EXISTS (
    SELECT 1 FROM notifications n
    WHERE n.task_id = t.id AND n.type = 'TASK_OVERDUE'
  )
```

### Cleanup Old Notifications

```sql
DELETE FROM notifications
WHERE created_at < DATETIME('now', '-30 days')
```

## Migration Notes

- New table, no existing data migration needed
- Foreign key to users table (existing)
- Foreign key to tasks table (existing)
- SQLModel will auto-create table via `SQLModel.metadata.create_all()`
