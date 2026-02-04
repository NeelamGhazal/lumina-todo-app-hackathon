"""FastAPI dependencies."""

from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import decode_access_token, get_password_hash
from app.models.user import User

# Default development user ID (fixed UUID for consistency)
DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
DEV_USER_EMAIL = "dev@example.com"
DEV_USER_NAME = "Development User"


async def get_or_create_dev_user(session: AsyncSession) -> User:
    """Get or create a default development user."""
    result = await session.execute(select(User).where(User.id == DEV_USER_ID))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=DEV_USER_ID,
            email=DEV_USER_EMAIL,
            name=DEV_USER_NAME,
            hashed_password=get_password_hash("devpassword"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    authorization: Annotated[str | None, Header()] = None,
    session_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """Get current authenticated user from Authorization header or session cookie.

    In development mode, bypasses authentication and returns a default dev user.

    Supports both:
    - Authorization: Bearer <token> (preferred, per spec)
    - session_token cookie (fallback)
    """
    settings = get_settings()

    # Bypass authentication in development mode
    if settings.is_development:
        return await get_or_create_dev_user(session)

    token: str | None = None

    # Try Authorization header first (per spec: Authorization: Bearer <token>)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    # Fall back to cookie
    elif session_token:
        token = session_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "UNAUTHORIZED", "message": "Not authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "SESSION_EXPIRED", "message": "Session expired. Please log in again."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "UNAUTHORIZED", "message": "Invalid session"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "UNAUTHORIZED", "message": "User not found"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
