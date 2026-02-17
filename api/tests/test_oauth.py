"""Tests for OAuth authentication functionality."""

import pytest
from httpx import AsyncClient
from sqlmodel import select

from app.core.database import get_session
from app.models.user import User


class TestOAuthLogin:
    """Tests for POST /api/auth/oauth endpoint."""

    async def test_oauth_login_new_user_google(self, client: AsyncClient):
        """Test new user signup with Google OAuth creates user and returns JWT."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "117234567890123456789",
                "email": "newuser@gmail.com",
                "name": "Google User",
                "image_url": "https://lh3.googleusercontent.com/avatar.jpg",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@gmail.com"
        assert data["user"]["name"] == "Google User"
        assert data["user"]["is_new_user"] is True

        # Verify user created in database
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "newuser@gmail.com")
            )
            user = result.scalar_one()
            assert user.oauth_provider == "google"
            assert user.oauth_provider_id == "117234567890123456789"
            assert user.image_url == "https://lh3.googleusercontent.com/avatar.jpg"
            assert user.hashed_password is None  # OAuth-only user
            break

    async def test_oauth_login_new_user_github(self, client: AsyncClient):
        """Test new user signup with GitHub OAuth creates user and returns JWT."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "github",
                "provider_id": "12345678",
                "email": "developer@example.com",
                "name": "GitHub Developer",
                "image_url": "https://avatars.githubusercontent.com/u/12345678",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "developer@example.com"
        assert data["user"]["name"] == "GitHub Developer"
        assert data["user"]["is_new_user"] is True

        # Verify user created in database
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "developer@example.com")
            )
            user = result.scalar_one()
            assert user.oauth_provider == "github"
            assert user.oauth_provider_id == "12345678"
            assert user.hashed_password is None
            break

    async def test_oauth_login_link_existing_account(
        self, client: AsyncClient, test_user: dict
    ):
        """Test OAuth with existing email/password user links OAuth provider."""
        # test_user fixture creates a user with email "test@example.com"
        # Now login with OAuth using same email
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "oauth-123456",
                "email": "test@example.com",
                "name": "Test User OAuth",
                "image_url": "https://example.com/avatar.jpg",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify it's recognized as existing user
        assert data["user"]["is_new_user"] is False
        assert data["user"]["email"] == "test@example.com"
        assert "access_token" in data

        # Verify OAuth provider linked in database
        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            assert user.oauth_provider == "google"
            assert user.oauth_provider_id == "oauth-123456"
            # Original password should still be set
            assert user.hashed_password is not None
            break

    async def test_oauth_login_returning_user(self, client: AsyncClient):
        """Test returning OAuth user gets authenticated immediately."""
        # First, create an OAuth user
        first_response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "returning-user-123",
                "email": "returning@example.com",
                "name": "Returning User",
            },
        )
        assert first_response.status_code == 200
        first_data = first_response.json()
        assert first_data["user"]["is_new_user"] is True
        user_id = first_data["user"]["id"]

        # Now login again as returning user
        second_response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "returning-user-123",
                "email": "returning@example.com",
                "name": "Returning User",
            },
        )
        assert second_response.status_code == 200
        second_data = second_response.json()

        # Should be recognized as existing user
        assert second_data["user"]["is_new_user"] is False
        assert second_data["user"]["id"] == user_id
        assert "access_token" in second_data

    async def test_oauth_login_invalid_provider(self, client: AsyncClient):
        """Test OAuth with invalid provider returns 400 error."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "facebook",  # Not supported
                "provider_id": "12345",
                "email": "user@facebook.com",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_PROVIDER"
        assert "google" in data["detail"]["message"].lower()
        assert "github" in data["detail"]["message"].lower()

    async def test_oauth_login_missing_email(self, client: AsyncClient):
        """Test OAuth with missing email returns validation error."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "12345",
                # email missing
            },
        )
        assert response.status_code == 422  # Pydantic validation error

    async def test_oauth_login_missing_provider_id(self, client: AsyncClient):
        """Test OAuth with missing provider_id returns validation error."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "email": "user@example.com",
                # provider_id missing
            },
        )
        assert response.status_code == 422

    async def test_oauth_login_missing_provider(self, client: AsyncClient):
        """Test OAuth with missing provider returns validation error."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider_id": "12345",
                "email": "user@example.com",
                # provider missing
            },
        )
        assert response.status_code == 422

    async def test_oauth_login_optional_fields(self, client: AsyncClient):
        """Test OAuth works without optional name and image_url fields."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "github",
                "provider_id": "minimal-user-123",
                "email": "minimal@example.com",
                # name and image_url omitted
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "minimal@example.com"
        assert data["user"]["name"] is None
        assert data["user"]["is_new_user"] is True

    async def test_oauth_sets_session_cookie(self, client: AsyncClient):
        """Test OAuth login sets session cookie."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "cookie-user-123",
                "email": "cookie@example.com",
            },
        )
        assert response.status_code == 200

        # Check that session cookie is set
        cookies = response.cookies
        assert "session_token" in cookies

    async def test_oauth_updates_name_if_empty(
        self, client: AsyncClient, test_user: dict
    ):
        """Test OAuth updates name for existing user only if empty."""
        # test_user has name "Test User"
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "name-test-123",
                "email": "test@example.com",
                "name": "New OAuth Name",  # Should NOT replace existing name
            },
        )
        assert response.status_code == 200

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            # Original name should be preserved
            assert user.name == "Test User"
            break

    async def test_oauth_updates_image_url(
        self, client: AsyncClient, test_user: dict
    ):
        """Test OAuth updates image_url for existing user."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "image-test-123",
                "email": "test@example.com",
                "image_url": "https://new-image.example.com/avatar.jpg",
            },
        )
        assert response.status_code == 200

        async for session in get_session():
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            assert user.image_url == "https://new-image.example.com/avatar.jpg"
            break


class TestOAuthOnlyUserRestrictions:
    """Tests for OAuth-only user restrictions on password login."""

    async def test_oauth_only_user_cannot_password_login(self, client: AsyncClient):
        """Test OAuth-only user cannot login with password."""
        # First create OAuth-only user
        await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "oauth-only-user-123",
                "email": "oauthonly@example.com",
                "name": "OAuth Only User",
            },
        )

        # Try to login with password (should fail)
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "oauthonly@example.com",
                "password": "anypassword123",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "OAUTH_ACCOUNT"
        assert "google" in data["detail"]["message"].lower()

    async def test_linked_user_can_still_password_login(
        self, client: AsyncClient, test_user: dict
    ):
        """Test user with password who linked OAuth can still use password login."""
        # Link OAuth to existing user
        await client.post(
            "/api/auth/oauth",
            json={
                "provider": "google",
                "provider_id": "linked-user-123",
                "email": "test@example.com",
            },
        )

        # User should still be able to login with password
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123",  # Original password from test_user fixture
            },
        )
        assert response.status_code == 200
        assert "token" in response.json()


class TestOAuthProviderValidation:
    """Tests for OAuth provider validation."""

    @pytest.mark.parametrize("provider", ["google", "github"])
    async def test_valid_providers_accepted(self, client: AsyncClient, provider: str):
        """Test that valid providers (google, github) are accepted."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": provider,
                "provider_id": f"{provider}-test-123",
                "email": f"{provider}user@example.com",
            },
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "invalid_provider",
        ["facebook", "twitter", "apple", "linkedin", "GOOGLE", "GitHub", ""],
    )
    async def test_invalid_providers_rejected(
        self, client: AsyncClient, invalid_provider: str
    ):
        """Test that invalid providers are rejected with 400."""
        response = await client.post(
            "/api/auth/oauth",
            json={
                "provider": invalid_provider,
                "provider_id": "test-123",
                "email": "user@example.com",
            },
        )
        # Empty provider may return 422 (validation) vs 400 (business logic)
        assert response.status_code in [400, 422]
