"""Authentication schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User response (safe, without password)."""

    id: str
    email: str
    name: str | None = None
    createdAt: str
    updatedAt: str


class RegisterRequest(BaseModel):
    """Registration request body."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str | None = Field(default=None, max_length=100)


class RegisterResponse(BaseModel):
    """Registration response."""

    user: UserResponse
    token: str


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response."""

    user: UserResponse
    token: str


class SessionResponse(BaseModel):
    """Session response."""

    user: UserResponse
    expiresAt: str
