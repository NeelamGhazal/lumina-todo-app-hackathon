"""Authentication routes."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    SessionResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def user_to_response(user: User) -> UserResponse:
    """Convert User model to response schema."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        createdAt=user.created_at.isoformat(),
        updatedAt=user.updated_at.isoformat(),
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: DbSession,
    response: Response,
) -> RegisterResponse:
    """Register a new user."""
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "EMAIL_ALREADY_EXISTS", "message": "Email already registered"},
        )

    # Create user
    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        name=request.name,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)

    # Create token and set cookie
    token = create_access_token(str(user.id))
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )

    return RegisterResponse(user=user_to_response(user), token=token)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: DbSession,
    response: Response,
) -> LoginResponse:
    """Login a user."""
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )

    # Create token and set cookie
    token = create_access_token(str(user.id))
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )

    return LoginResponse(user=user_to_response(user), token=token)


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Logout the current user."""
    response.delete_cookie(key="session_token", path="/")
    return {"success": True}


@router.get("/session", response_model=SessionResponse)
async def get_session(current_user: CurrentUser) -> SessionResponse:
    """Get current session information."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return SessionResponse(
        user=user_to_response(current_user),
        expiresAt=expires_at.isoformat(),
    )
