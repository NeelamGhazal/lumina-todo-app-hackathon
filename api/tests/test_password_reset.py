"""Tests for password reset functionality."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlmodel import select

from app.core.security import generate_reset_token, hash_reset_token
from app.models.user import User


class TestForgotPassword:
    """Tests for POST /api/auth/forgot-password endpoint."""

    async def test_forgot_password_existing_user(
        self, client: AsyncClient, test_user: dict
    ):
        """Test forgot password for existing user returns success message."""
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "If an account exists" in data["message"]

    async def test_forgot_password_nonexistent_user(self, client: AsyncClient):
        """Test forgot password for non-existent user returns same message (enumeration prevention)."""
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "If an account exists" in data["message"]

    async def test_forgot_password_invalid_email_format(self, client: AsyncClient):
        """Test forgot password with invalid email format returns validation error."""
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    async def test_forgot_password_rate_limiting(
        self, client: AsyncClient, test_user: dict
    ):
        """Test rate limiting blocks 4th request within 1 hour."""
        email = "test@example.com"

        # Make 3 requests (should all succeed)
        for i in range(3):
            response = await client.post(
                "/api/auth/forgot-password",
                json={"email": email},
            )
            assert response.status_code == 200, f"Request {i+1} should succeed"

        # 4th request should be rate limited
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": email},
        )
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["error"] == "RATE_LIMIT_EXCEEDED"


class TestVerifyResetToken:
    """Tests for GET /api/auth/verify-reset-token/{token} endpoint."""

    async def test_verify_valid_token(self, client: AsyncClient, test_user: dict):
        """Test verify token with valid token returns valid=true."""
        # First request a password reset to generate a token
        await client.post(
            "/api/auth/forgot-password",
            json={"email": "test@example.com"},
        )

        # Get the token from the database (in real test, we'd capture from email)
        # For this test, we'll generate a token and set it directly
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        # Update user with token directly for testing
        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        response = await client.get(f"/api/auth/verify-reset-token/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["email"] == "test@example.com"

    async def test_verify_invalid_token(self, client: AsyncClient):
        """Test verify token with invalid token returns valid=false."""
        response = await client.get("/api/auth/verify-reset-token/invalid-token-12345")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Invalid" in data["error"]

    async def test_verify_expired_token(self, client: AsyncClient, test_user: dict):
        """Test verify token with expired token returns valid=false with expired message."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        # Set expired token
        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) - timedelta(minutes=1)  # Expired
            session.add(user)
            await session.commit()
            break

        response = await client.get(f"/api/auth/verify-reset-token/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "expired" in data["error"].lower()


class TestResetPassword:
    """Tests for POST /api/auth/reset-password endpoint."""

    async def test_reset_password_success(self, client: AsyncClient, test_user: dict):
        """Test successful password reset."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        # Set valid token
        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "NewPassword123",
                "password_confirm": "NewPassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify can login with new password
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "NewPassword123"},
        )
        assert login_response.status_code == 200

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test reset password with invalid token returns error."""
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid-token",
                "password": "NewPassword123",
                "password_confirm": "NewPassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_TOKEN"

    async def test_reset_password_expired_token(
        self, client: AsyncClient, test_user: dict
    ):
        """Test reset password with expired token returns error."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) - timedelta(minutes=1)
            session.add(user)
            await session.commit()
            break

        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "NewPassword123",
                "password_confirm": "NewPassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "TOKEN_EXPIRED"

    async def test_reset_password_mismatch(
        self, client: AsyncClient, test_user: dict
    ):
        """Test reset password with mismatched passwords returns error."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "NewPassword123",
                "password_confirm": "DifferentPassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "PASSWORD_MISMATCH"

    async def test_reset_password_weak_password(
        self, client: AsyncClient, test_user: dict
    ):
        """Test reset password with weak password returns validation errors."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        # Test password too short
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "short",
                "password_confirm": "short",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"] == "INVALID_PASSWORD"
        assert any("8 characters" in detail for detail in data["detail"]["details"])

    async def test_reset_password_token_invalidated_after_use(
        self, client: AsyncClient, test_user: dict
    ):
        """Test that token is invalidated after successful password reset."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        # First reset should succeed
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "NewPassword123",
                "password_confirm": "NewPassword123",
            },
        )
        assert response.status_code == 200

        # Second reset with same token should fail (token invalidated)
        response = await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "AnotherPassword123",
                "password_confirm": "AnotherPassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_TOKEN"


class TestSecurityVerification:
    """Tests to verify security requirements."""

    async def test_token_is_hashed_in_database(
        self, client: AsyncClient, test_user: dict
    ):
        """Verify that plain token is never stored in database."""
        # Request password reset
        await client.post(
            "/api/auth/forgot-password",
            json={"email": "test@example.com"},
        )

        # Check database - token should be hashed (64 char hex string)
        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()

            # Token hash should be 64 characters (SHA-256 hex)
            assert user.reset_token_hash is not None
            assert len(user.reset_token_hash) == 64
            # Should only contain hex characters
            assert all(c in "0123456789abcdef" for c in user.reset_token_hash)
            break

    async def test_token_cleared_after_reset(
        self, client: AsyncClient, test_user: dict
    ):
        """Verify token is cleared from database after successful reset."""
        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        from app.core.database import get_session

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            user.reset_token_hash = token_hash
            user.reset_token_expiry = datetime.now(UTC) + timedelta(minutes=15)
            session.add(user)
            await session.commit()
            break

        # Reset password
        await client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "password": "NewPassword123",
                "password_confirm": "NewPassword123",
            },
        )

        # Verify token is cleared
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            assert user.reset_token_hash is None
            assert user.reset_token_expiry is None
            break
