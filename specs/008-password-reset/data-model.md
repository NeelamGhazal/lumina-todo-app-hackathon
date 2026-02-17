# Data Model: Password Reset

**Feature**: 008-password-reset | **Date**: 2026-02-12

## Entity Changes

### User Model (MODIFY)

**Current Fields** (from `api/app/models/user.py`):
```python
class User(SQLModel, table=True):
    id: UUID
    email: str
    hashed_password: str
    name: str | None
    created_at: datetime
    updated_at: datetime
```

**New Fields to Add**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `reset_token_hash` | `str \| None` | `None` | SHA-256 hash of reset token |
| `reset_token_expiry` | `datetime \| None` | `None` | Token expiry timestamp (UTC) |
| `reset_request_count` | `int` | `0` | Requests in current rate limit window |
| `reset_request_window_start` | `datetime \| None` | `None` | Start of rate limit window |

**Updated Model**:
```python
class User(SQLModel, table=True):
    """User database model."""

    __tablename__ = "users"

    # Existing fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    name: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Password reset fields (NEW)
    reset_token_hash: str | None = Field(default=None, max_length=64)
    reset_token_expiry: datetime | None = Field(default=None)
    reset_request_count: int = Field(default=0)
    reset_request_window_start: datetime | None = Field(default=None)
```

## Validation Rules

### Password Requirements (FR-010)

| Rule | Validation | Error Message |
|------|------------|---------------|
| Minimum length | `len(password) >= 8` | "Password must be at least 8 characters" |
| Uppercase | `re.search(r'[A-Z]', password)` | "Password must contain at least 1 uppercase letter" |
| Number | `re.search(r'[0-9]', password)` | "Password must contain at least 1 number" |

### Email Validation (FR-002)

- Use Pydantic's `EmailStr` type for automatic validation
- No additional custom validation needed

### Token Validation (FR-009)

| Check | Condition | Error |
|-------|-----------|-------|
| Token exists | `user.reset_token_hash is not None` | "Invalid reset link" |
| Token matches | `hash(token) == user.reset_token_hash` | "Invalid reset link" |
| Not expired | `datetime.now(UTC) < user.reset_token_expiry` | "Reset link has expired" |

### Rate Limiting (FR-007)

| Check | Condition | Action |
|-------|-----------|--------|
| Window expired | `now - window_start > 1 hour` | Reset count to 1 |
| Under limit | `count < 3` | Allow request, increment count |
| At limit | `count >= 3` | Reject with rate limit error |

## State Transitions

### Token Lifecycle

```
[No Token]
    │
    ▼ (forgot-password request)
[Token Generated]
    │
    ├──▶ [Token Expired] ──▶ [No Token]
    │         (after 15 min)
    │
    └──▶ [Password Reset] ──▶ [No Token]
              (token used)
```

### Rate Limit Window

```
[No Window]
    │
    ▼ (first request)
[Window Active: count=1]
    │
    ├──▶ [count=2] ──▶ [count=3] ──▶ [BLOCKED]
    │    (request)     (request)     (4th request)
    │
    └──▶ [Window Expired] ──▶ [New Window: count=1]
              (after 1 hour)
```

## Database Migration

SQLModel with SQLite handles schema changes automatically on restart. No manual migration needed for development.

For production, the migration would be:

```sql
-- Add password reset fields to users table
ALTER TABLE users ADD COLUMN reset_token_hash VARCHAR(64) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_request_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN reset_request_window_start TIMESTAMP DEFAULT NULL;
```

## Indexes

No additional indexes needed:
- `email` is already indexed (for forgot-password lookup)
- Token lookups are done after email lookup (no separate token index needed)

## Data Retention

- Reset token fields are cleared after:
  1. Successful password reset
  2. New token requested (replaces old)
- Rate limit fields are soft-reset when window expires (count reset to 0)
- No historical reset data stored (per Out of Scope)
