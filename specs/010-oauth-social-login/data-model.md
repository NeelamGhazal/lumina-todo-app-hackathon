# Data Model: OAuth Social Login

**Feature**: 010-oauth-social-login
**Date**: 2026-02-13
**Database**: SQLite via SQLModel

## Entity Changes

### User (Extended)

The existing `User` model is extended with OAuth support fields.

**Current Fields** (unchanged):
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| email | str | Unique, indexed, max 255 | User's email (unique identifier for linking) |
| name | str | Optional, max 100 | Display name |
| created_at | datetime | Auto-set | Account creation timestamp |
| updated_at | datetime | Auto-set | Last update timestamp |
| reset_token_hash | str | Optional, max 64 | Password reset token |
| reset_token_expiry | datetime | Optional | Reset token expiration |
| reset_request_count | int | Default 0 | Rate limiting counter |
| reset_request_window_start | datetime | Optional | Rate limiting window |

**Modified Fields**:
| Field | Type | Change | Rationale |
|-------|------|--------|-----------|
| hashed_password | str \| None | Now **nullable** | OAuth-only users have no password |

**New Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| oauth_provider | str \| None | Optional, max 50 | Provider name: 'google', 'github', or NULL |
| oauth_provider_id | str \| None | Optional, max 255 | Provider's unique user ID |
| image_url | str \| None | Optional, max 500 | Profile image URL from OAuth |

### User Model Definition

```python
class User(SQLModel, table=True):
    """User database model with OAuth support."""

    __tablename__ = "users"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Core identity
    email: str = Field(unique=True, index=True, max_length=255)
    name: str | None = Field(default=None, max_length=100)

    # Password auth (nullable for OAuth-only users)
    hashed_password: str | None = Field(default=None, max_length=255)

    # OAuth fields
    oauth_provider: str | None = Field(default=None, max_length=50)
    oauth_provider_id: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)

    # Password reset
    reset_token_hash: str | None = Field(default=None, max_length=64)
    reset_token_expiry: datetime | None = Field(default=None)
    reset_request_count: int = Field(default=0)
    reset_request_window_start: datetime | None = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                          User                                │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ email (unique) ─────────────────────┐                       │
│ name                                │ Account linking       │
│ hashed_password (nullable)          │ by email match        │
│ oauth_provider ─────────┐           │                       │
│ oauth_provider_id ──────┼───────────┘                       │
│ image_url               │                                   │
│ ...                     │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │    OAuth Providers      │
            ├─────────────────────────┤
            │ • google                │
            │ • github                │
            └─────────────────────────┘
```

## State Transitions

### User Authentication States

```
                    ┌──────────────────┐
                    │   New Visitor    │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ Email Signup  │ │ Google OAuth  │ │ GitHub OAuth  │
    │ (password)    │ │ (no password) │ │ (no password) │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────────────────────────────────────────────┐
    │                  Authenticated User                  │
    │  • Can access all features                          │
    │  • Can link additional OAuth providers              │
    └─────────────────────────────────────────────────────┘
```

### Account Linking States

```
     OAuth Login with Email "user@example.com"
                    │
                    ▼
        ┌───────────────────────┐
        │ User exists with      │
        │ this email?           │
        └───────────┬───────────┘
                    │
         ┌──────────┴──────────┐
         │ YES                 │ NO
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Link OAuth to   │   │ Create new user │
│ existing user   │   │ (OAuth-only)    │
│ - Update        │   │ - password=NULL │
│   oauth_provider│   │ - Set OAuth     │
│ - Update        │   │   fields        │
│   oauth_id      │   │                 │
└────────┬────────┘   └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌───────────────────┐
         │ Return JWT token  │
         └───────────────────┘
```

## Validation Rules

### Email
- Required for all users
- Must be unique across all users
- Max 255 characters
- Validated by OAuth provider (trusted)

### OAuth Provider
- Must be one of: 'google', 'github', or NULL
- NULL for email/password-only users

### OAuth Provider ID
- Required when oauth_provider is set
- Unique per provider (not globally unique)
- Max 255 characters

### Password
- Required for email/password users (non-NULL, non-empty)
- NULL for OAuth-only users
- Min 8 chars, 1 uppercase, 1 number (when set)

## Migration Notes

### Backward Compatibility

1. **Existing users unaffected**: All new fields are nullable with defaults
2. **No data migration needed**: Empty OAuth fields = email/password user
3. **Password login still works**: Check `hashed_password IS NOT NULL` before password auth

### Index Recommendations

```sql
-- Existing
CREATE UNIQUE INDEX ix_users_email ON users(email);

-- No new indexes needed (OAuth fields queried via email first)
```

## Multi-Provider Considerations

The current design stores the **most recent** OAuth provider used. If a user links both Google and GitHub (same email), the latest one overwrites `oauth_provider` and `oauth_provider_id`.

**For future multi-provider support** (out of scope):
- Create separate `oauth_accounts` table
- One-to-many relationship: User → OAuthAccounts
- Store multiple provider links per user
