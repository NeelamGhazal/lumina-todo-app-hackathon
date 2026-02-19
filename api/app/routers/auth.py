"""Authentication routes."""

import logging
import smtplib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.email import send_password_reset_email
from app.core.security import (
    create_access_token,
    generate_reset_token,
    get_password_hash,
    hash_reset_token,
    validate_password_strength,
    verify_password,
    verify_reset_token,
)
from app.models.user import User
from app.schemas.auth import (
    ErrorResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    OAuthLoginRequest,
    OAuthLoginResponse,
    OAuthUser,
    PasswordValidationErrorResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SessionResponse,
    UserResponse,
    VerifyTokenResponse,
)

logger = logging.getLogger(__name__)

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

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )

    # Check if user is OAuth-only (no password set)
    if user.hashed_password is None:
        provider = user.oauth_provider or "social login"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "OAUTH_ACCOUNT",
                "message": f"This account uses {provider}. Please sign in with {provider} instead.",
            },
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
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


# Password Reset Functions


def check_rate_limit(user: User) -> bool:
    """
    Check if user has exceeded rate limit for password reset requests.

    Returns True if rate limit exceeded (should block), False if allowed.
    """
    now = datetime.now(UTC)
    max_requests = settings.password_reset_max_requests_per_hour

    # If no window exists or window has expired (> 1 hour), allow
    if user.reset_request_window_start is None:
        return False

    # Handle naive datetime from database
    window_start = user.reset_request_window_start
    if window_start.tzinfo is None:
        window_start = window_start.replace(tzinfo=UTC)

    window_age = now - window_start
    if window_age > timedelta(hours=1):
        return False  # Window expired, will be reset

    # Check if count exceeds limit
    return user.reset_request_count >= max_requests


def update_rate_limit(user: User) -> None:
    """
    Update rate limit counters for user.

    Resets window if expired, otherwise increments count.
    """
    now = datetime.now(UTC)

    # If no window or window expired, start new window
    if user.reset_request_window_start is None:
        user.reset_request_window_start = now
        user.reset_request_count = 1
    else:
        # Handle naive datetime from database
        window_start = user.reset_request_window_start
        if window_start.tzinfo is None:
            window_start = window_start.replace(tzinfo=UTC)

        window_age = now - window_start
        if window_age > timedelta(hours=1):
            # Window expired, reset
            user.reset_request_window_start = now
            user.reset_request_count = 1
        else:
            # Within window, increment
            user.reset_request_count += 1


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: DbSession,
) -> ForgotPasswordResponse:
    """
    Request password reset email.

    Always returns same response to prevent email enumeration.
    Rate limited to 3 requests per email per hour.
    """
    # Look up user by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return same response to prevent enumeration
    response = ForgotPasswordResponse()

    if user is None:
        # User doesn't exist - return generic response without doing anything
        # Log for monitoring but don't expose to client
        logger.info(f"Password reset requested for non-existent email: {request.email}")
        return response

    # T020: Check if user is OAuth-only (no password set)
    if user.hashed_password is None:
        # OAuth-only user - return generic response without generating token
        # Log for monitoring but don't expose to client (prevents enumeration)
        logger.info(
            f"Password reset requested for OAuth-only user: {request.email} "
            f"(provider: {user.oauth_provider})"
        )
        return response

    # Check rate limit
    if check_rate_limit(user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Too many reset requests. Please try again later.",
            },
        )

    # Generate token and hash
    plain_token = generate_reset_token()
    token_hash = hash_reset_token(plain_token)

    # Update user with token (replaces any existing token)
    user.reset_token_hash = token_hash
    user.reset_token_expiry = datetime.now(UTC) + timedelta(
        minutes=settings.password_reset_token_expiry_minutes
    )

    # Update rate limit counters
    update_rate_limit(user)

    # Commit changes
    session.add(user)
    await session.flush()

    # Generate reset link using primary frontend URL
    reset_link = f"{settings.primary_frontend_url}/reset-password?token={plain_token}"

    # Send email (don't expose failure to client)
    email_sent = send_password_reset_email(to_email=user.email, reset_link=reset_link)
    if not email_sent:
        logger.error(f"Failed to send password reset email to {user.email}")
        # Still return success to prevent enumeration

    logger.info(f"Password reset token generated for user: {user.email}")

    return response


@router.get("/verify-reset-token/{token}", response_model=VerifyTokenResponse)
async def verify_reset_token_endpoint(
    token: str,
    session: DbSession,
) -> VerifyTokenResponse:
    """
    Verify if a password reset token is valid.

    Used by frontend to validate token before showing reset form.
    Returns token validity status and user email if valid.
    """
    # Find user by token hash
    token_hash = hash_reset_token(token)
    result = await session.execute(
        select(User).where(User.reset_token_hash == token_hash)
    )
    user = result.scalar_one_or_none()

    # Token not found or doesn't match any user
    if user is None:
        return VerifyTokenResponse(
            valid=False,
            email=None,
            error="Invalid reset link",
        )

    # Check if token has expired
    # Handle both timezone-aware and naive datetimes from database
    token_expiry = user.reset_token_expiry
    if token_expiry is not None and token_expiry.tzinfo is None:
        token_expiry = token_expiry.replace(tzinfo=UTC)
    if token_expiry is None or datetime.now(UTC) > token_expiry:
        return VerifyTokenResponse(
            valid=False,
            email=None,
            error="This reset link has expired",
        )

    # Token is valid
    return VerifyTokenResponse(
        valid=True,
        email=user.email,
        error=None,
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    session: DbSession,
) -> ResetPasswordResponse:
    """
    Reset password using a valid token.

    Validates token, password requirements, and password confirmation.
    Invalidates token after successful password change.
    """
    # Find user by token hash
    token_hash = hash_reset_token(request.token)
    result = await session.execute(
        select(User).where(User.reset_token_hash == token_hash)
    )
    user = result.scalar_one_or_none()

    # Token not found
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_TOKEN",
                "message": "Invalid reset link. Please request a new one.",
            },
        )

    # Check if token has expired
    # Handle both timezone-aware and naive datetimes from database
    token_expiry = user.reset_token_expiry
    if token_expiry is not None and token_expiry.tzinfo is None:
        token_expiry = token_expiry.replace(tzinfo=UTC)
    if token_expiry is None or datetime.now(UTC) > token_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "TOKEN_EXPIRED",
                "message": "This reset link has expired. Please request a new one.",
            },
        )

    # Validate passwords match
    if request.password != request.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PASSWORD_MISMATCH",
                "message": "Passwords do not match",
            },
        )

    # Validate password strength
    password_errors = validate_password_strength(request.password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_PASSWORD",
                "message": "Password does not meet requirements",
                "details": password_errors,
            },
        )

    # Update password and invalidate token
    user.hashed_password = get_password_hash(request.password)
    user.reset_token_hash = None
    user.reset_token_expiry = None
    user.updated_at = datetime.now(UTC)

    session.add(user)
    await session.flush()

    logger.info(f"Password reset successful for user: {user.email}")

    return ResetPasswordResponse(
        success=True,
        message="Password has been reset successfully",
    )


# OAuth Endpoints

VALID_OAUTH_PROVIDERS = {"google", "github"}


@router.post("/oauth", response_model=OAuthLoginResponse)
async def oauth_login(
    request: OAuthLoginRequest,
    session: DbSession,
    response: Response,
) -> OAuthLoginResponse:
    """
    OAuth login/signup endpoint.

    Called by frontend after successful OAuth provider authentication.
    - If email exists: Link OAuth provider to existing account
    - If email not found: Create new OAuth-only user (no password)
    """
    # Validate provider
    if request.provider not in VALID_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PROVIDER",
                "message": f"Provider must be one of: {', '.join(VALID_OAUTH_PROVIDERS)}",
            },
        )

    # Check if user exists by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    is_new_user = False

    if user:
        # Link OAuth provider to existing account
        user.oauth_provider = request.provider
        user.oauth_provider_id = request.provider_id
        if request.name and not user.name:
            user.name = request.name
        if request.image_url:
            user.image_url = request.image_url
        user.updated_at = datetime.now(UTC)
        logger.info(f"OAuth linked to existing user: {user.email} (provider: {request.provider})")
    else:
        # Create new OAuth-only user (no password)
        user = User(
            email=request.email,
            hashed_password=None,  # OAuth-only user
            name=request.name,
            oauth_provider=request.provider,
            oauth_provider_id=request.provider_id,
            image_url=request.image_url,
        )
        session.add(user)
        is_new_user = True
        logger.info(f"New OAuth user created: {request.email} (provider: {request.provider})")

    await session.flush()
    await session.refresh(user)

    # Create JWT token
    token = create_access_token(str(user.id))

    # Set session cookie (same as regular login)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )

    return OAuthLoginResponse(
        access_token=token,
        token_type="bearer",
        user=OAuthUser(
            id=str(user.id),
            email=user.email,
            name=user.name,
            is_new_user=is_new_user,
        ),
    )


# Debug endpoint for SMTP testing (remove in production)
@router.get("/debug-smtp")
async def debug_smtp() -> dict:
    """
    Debug endpoint to test SMTP configuration.
    Returns config status and attempts SMTP connection.
    """
    result = {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user or "NOT SET",
        "smtp_pass": "SET" if settings.smtp_pass else "NOT SET",
        "resend_api_key": "SET" if settings.resend_api_key else "NOT SET",
        "smtp_test": None,
        "smtp_error": None,
    }

    # Test SMTP connection if credentials are set
    if settings.smtp_user and settings.smtp_pass:
        try:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.quit()
            result["smtp_test"] = "SUCCESS - Login worked!"
        except Exception as e:
            result["smtp_test"] = "FAILED"
            result["smtp_error"] = str(e)
    else:
        result["smtp_test"] = "SKIPPED - credentials not set"

    return result
