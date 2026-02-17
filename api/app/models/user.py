"""User database model."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User database model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str | None = Field(default=None, max_length=255)  # Nullable for OAuth-only users
    name: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # OAuth fields
    oauth_provider: str | None = Field(default=None, max_length=50)  # "google" or "github"
    oauth_provider_id: str | None = Field(default=None, max_length=255)  # Provider's user ID
    image_url: str | None = Field(default=None, max_length=500)  # Profile image from OAuth

    # Password reset fields
    reset_token_hash: str | None = Field(default=None, max_length=64)
    reset_token_expiry: datetime | None = Field(default=None)
    reset_request_count: int = Field(default=0)
    reset_request_window_start: datetime | None = Field(default=None)
