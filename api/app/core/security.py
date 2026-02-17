"""Security utilities for authentication and password hashing."""

import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Decode and validate a JWT token. Returns user_id or None if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        return user_id
    except JWTError:
        return None


# Password Reset Token Functions


def generate_reset_token() -> str:
    """Generate a cryptographically secure reset token (256-bit entropy)."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """Hash a reset token using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(token: str, token_hash: str) -> bool:
    """Verify a reset token against its hash using constant-time comparison."""
    return secrets.compare_digest(hash_reset_token(token), token_hash)


def validate_password_strength(password: str) -> list[str]:
    """
    Validate password meets security requirements.
    Returns list of validation errors (empty if valid).

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 number
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least 1 uppercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least 1 number")
    return errors
