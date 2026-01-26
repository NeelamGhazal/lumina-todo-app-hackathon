# Data Model: Phase I - Professional Todo Console Application

**Date**: 2026-01-26
**Branch**: `001-phase1-todo-cli`

## Overview

This document defines the data model for Phase I using Pydantic v2.

---

## Enumerations

### Priority

```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

**Display Colors**:
| Value | Color | Icon |
|-------|-------|------|
| HIGH | red | ⚠️ |
| MEDIUM | yellow | ● |
| LOW | green | ○ |

---

### Category

```python
from enum import Enum

class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"
```

**Display Icons**:
| Value | Icon |
|-------|------|
| WORK | 💼 |
| PERSONAL | 🏠 |
| SHOPPING | 🛒 |
| HEALTH | ❤️ |
| OTHER | 📌 |

---

## Entities

### Task

**Description**: Represents a todo item in the system.

**Pydantic Model**:

```python
from datetime import date, time, datetime
from pydantic import BaseModel, Field
from typing import Optional

class Task(BaseModel):
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

    class Config:
        # Allow mutation for updates
        frozen = False
        # Use enum values in serialization
        use_enum_values = True
```

---

## Field Specifications

### ID Generation

**Format**: 6-character lowercase alphanumeric
**Charset**: `abcdefghijklmnopqrstuvwxyz0123456789`
**Combinations**: 36^6 = 2,176,782,336

**Generation Algorithm**:
```python
import random
import string

def generate_id(existing_ids: set[str]) -> str:
    charset = string.ascii_lowercase + string.digits
    while True:
        new_id = ''.join(random.choices(charset, k=6))
        if new_id not in existing_ids:
            return new_id
```

---

### Title

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | Yes |
| Min Length | 1 |
| Max Length | 200 |
| Validation | Non-empty, whitespace trimmed |

---

### Description

| Attribute | Value |
|-----------|-------|
| Type | string |
| Required | No |
| Default | "" (empty string) |
| Max Length | 2000 |

---

### Priority

| Attribute | Value |
|-----------|-------|
| Type | enum |
| Required | No |
| Default | "medium" |
| Values | high, medium, low |

---

### Category

| Attribute | Value |
|-----------|-------|
| Type | enum |
| Required | No |
| Default | "other" |
| Values | work, personal, shopping, health, other |

---

### Tags

| Attribute | Value |
|-----------|-------|
| Type | list[str] |
| Required | No |
| Default | [] (empty list) |
| Validation | Each tag trimmed, duplicates removed |

---

### Due Date

| Attribute | Value |
|-----------|-------|
| Type | date (optional) |
| Required | No |
| Default | None |
| Format | YYYY-MM-DD or natural language |

**Natural Language Parsing**:
| Input | Interpretation |
|-------|----------------|
| "today" | Current date |
| "tomorrow" | Current date + 1 |
| "next monday" | Next Monday from today |
| "friday" | Next Friday (or today if Friday) |
| "2026-02-15" | Explicit date |

---

### Due Time

| Attribute | Value |
|-----------|-------|
| Type | time (optional) |
| Required | No |
| Default | None |
| Format | HH:MM or keyword |

**Keyword Mapping**:
| Keyword | Time |
|---------|------|
| "morning" | 09:00 |
| "afternoon" | 14:00 |
| "evening" | 18:00 |
| "night" | 21:00 |

---

### Is Completed

| Attribute | Value |
|-----------|-------|
| Type | boolean |
| Required | No |
| Default | False |

---

### Created At

| Attribute | Value |
|-----------|-------|
| Type | datetime |
| Required | Auto-generated |
| Default | Current timestamp on creation |
| Mutable | No |

---

## Storage Schema

### In-Memory Structure

```python
# Storage is a simple dict mapping ID to Task
tasks: dict[str, Task] = {}

# Example state:
{
    "a1b2c3": Task(
        id="a1b2c3",
        title="Buy groceries",
        priority=Priority.HIGH,
        category=Category.SHOPPING,
        due_date=date(2026, 1, 27),
        is_completed=False,
        created_at=datetime(2026, 1, 26, 10, 30, 0)
    ),
    "x9y8z7": Task(
        id="x9y8z7",
        title="Finish report",
        priority=Priority.MEDIUM,
        category=Category.WORK,
        is_completed=True,
        created_at=datetime(2026, 1, 25, 14, 0, 0)
    )
}
```

---

## Validation Rules

### Title Validation

1. Must not be empty after trimming whitespace
2. Must not exceed 200 characters
3. Unicode characters allowed
4. Leading/trailing whitespace trimmed

### Tag Validation

1. Each tag trimmed of whitespace
2. Empty tags removed
3. Duplicate tags removed (case-insensitive)
4. Maximum 10 tags per task (soft limit)

### Date Validation

1. Past dates allowed (with warning on display)
2. Invalid format shows error with examples
3. Natural language parsed before ISO format

---

## State Transitions

### Task Lifecycle

```
┌─────────┐     /complete     ┌───────────┐
│ PENDING │ ───────────────▶ │ COMPLETED │
│         │ ◀─────────────── │           │
└─────────┘     /complete     └───────────┘
      │                              │
      │         /delete              │
      └──────────────────────────────┘
                    │
                    ▼
              ┌──────────┐
              │ DELETED  │
              │ (removed)│
              └──────────┘
```

---

## Example Task JSON

```json
{
    "id": "a1b2c3",
    "title": "Buy groceries for dinner party",
    "description": "Need vegetables, chicken, and dessert",
    "priority": "high",
    "category": "shopping",
    "tags": ["food", "party", "weekend"],
    "due_date": "2026-01-28",
    "due_time": "14:00:00",
    "is_completed": false,
    "created_at": "2026-01-26T10:30:00"
}
```
