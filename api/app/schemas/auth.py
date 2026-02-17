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


# Password Reset Schemas


class ForgotPasswordRequest(BaseModel):
    """Forgot password request body."""

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Forgot password response (always same to prevent enumeration)."""

    message: str = "If an account exists with this email, you will receive a reset link shortly"


class VerifyTokenResponse(BaseModel):
    """Token verification response."""

    valid: bool
    email: str | None = None
    error: str | None = None


class ResetPasswordRequest(BaseModel):
    """Reset password request body."""

    token: str
    password: str = Field(max_length=100)
    password_confirm: str = Field(max_length=100)


class ResetPasswordResponse(BaseModel):
    """Reset password success response."""

    success: bool
    message: str


class PasswordValidationErrorResponse(BaseModel):
    """Password validation error response."""

    error: str = "INVALID_PASSWORD"
    message: str = "Password does not meet requirements"
    details: list[str]


class ErrorResponse(BaseModel):
    """Generic error response."""

    error: str
    message: str


# OAuth Schemas


class OAuthLoginRequest(BaseModel):
    """OAuth login request body - called by frontend after OAuth provider authentication."""

    provider: str = Field(description="OAuth provider: 'google' or 'github'")
    provider_id: str = Field(description="Unique user ID from the OAuth provider")
    email: EmailStr = Field(description="User's email from OAuth provider")
    name: str | None = Field(default=None, max_length=100, description="User's display name")
    image_url: str | None = Field(default=None, max_length=500, description="Profile image URL")


class OAuthUser(BaseModel):
    """OAuth user info in response."""

    id: str
    email: str
    name: str | None = None
    is_new_user: bool = Field(description="True if user was just created")


class OAuthLoginResponse(BaseModel):
    """OAuth login response with JWT and user info."""

    access_token: str
    token_type: str = "bearer"
    user: OAuthUser
