"""Tests for notification API endpoints."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlmodel import select

from app.core.database import get_session
from app.models.notification import Notification, NotificationType
from app.models.user import User


async def create_notification(
    user_id,
    notification_type: NotificationType = NotificationType.TASK_DUE_SOON,
    message: str = "Test notification",
    is_read: bool = False,
    task_id=None,
) -> Notification:
    """Helper to create a notification directly in the database."""
    async for session in get_session():
        notification = Notification(
            user_id=user_id,
            task_id=task_id,
            type=notification_type,
            message=message,
            is_read=is_read,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification


async def get_user_id_from_email(email: str):
    """Helper to get user ID from email."""
    async for session in get_session():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one()
        return user.id


class TestGetNotifications:
    """Tests for GET /api/notifications endpoint."""

    async def test_get_notifications_empty(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns empty list for user with no notifications."""
        token = test_user["token"]
        response = await client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notifications"] == []
        assert data["total"] == 0
        assert data["unreadCount"] == 0

    async def test_get_notifications_with_data(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns notifications sorted by created_at DESC (newest first)."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create notifications
        n1 = await create_notification(user_id, message="First notification")
        n2 = await create_notification(user_id, message="Second notification")
        n3 = await create_notification(
            user_id, message="Third notification", is_read=True
        )

        response = await client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["unreadCount"] == 2  # n1 and n2 are unread

        # Verify order (newest first)
        notifications = data["notifications"]
        assert len(notifications) == 3
        assert notifications[0]["message"] == "Third notification"
        assert notifications[1]["message"] == "Second notification"
        assert notifications[2]["message"] == "First notification"

    async def test_get_notifications_with_limit(
        self, client: AsyncClient, test_user: dict
    ):
        """Test limit parameter restricts number of results."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create 5 notifications
        for i in range(5):
            await create_notification(user_id, message=f"Notification {i}")

        response = await client.get(
            "/api/notifications?limit=2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["notifications"]) == 2

    async def test_get_notifications_unread_only(
        self, client: AsyncClient, test_user: dict
    ):
        """Test unreadOnly parameter filters to only unread notifications."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create mix of read and unread
        await create_notification(user_id, message="Unread 1", is_read=False)
        await create_notification(user_id, message="Read 1", is_read=True)
        await create_notification(user_id, message="Unread 2", is_read=False)

        response = await client.get(
            "/api/notifications?unreadOnly=true",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(not n["isRead"] for n in data["notifications"])

    async def test_get_notifications_unauthorized(self, client: AsyncClient):
        """Test returns 401 without authentication."""
        response = await client.get("/api/notifications")
        assert response.status_code == 401


class TestGetUnreadCount:
    """Tests for GET /api/notifications/unread-count endpoint."""

    async def test_get_unread_count_zero(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns count of 0 for user with no unread notifications."""
        token = test_user["token"]
        response = await client.get(
            "/api/notifications/unread-count",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

    async def test_get_unread_count_with_notifications(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns correct unread count."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create notifications (2 unread, 1 read)
        await create_notification(user_id, is_read=False)
        await create_notification(user_id, is_read=False)
        await create_notification(user_id, is_read=True)

        response = await client.get(
            "/api/notifications/unread-count",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    async def test_get_unread_count_unauthorized(self, client: AsyncClient):
        """Test returns 401 without authentication."""
        response = await client.get("/api/notifications/unread-count")
        assert response.status_code == 401


class TestMarkNotificationRead:
    """Tests for PATCH /api/notifications/{id}/read endpoint."""

    async def test_mark_notification_read(
        self, client: AsyncClient, test_user: dict
    ):
        """Test marking a notification as read."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        notification = await create_notification(user_id, is_read=False)

        response = await client.patch(
            f"/api/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isRead"] is True
        assert data["id"] == str(notification.id)

    async def test_mark_notification_read_already_read(
        self, client: AsyncClient, test_user: dict
    ):
        """Test marking an already-read notification (should succeed)."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        notification = await create_notification(user_id, is_read=True)

        response = await client.patch(
            f"/api/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["isRead"] is True

    async def test_mark_notification_read_not_found(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns 404 for non-existent notification."""
        token = test_user["token"]
        fake_id = uuid4()

        response = await client.patch(
            f"/api/notifications/{fake_id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "NOTIFICATION_NOT_FOUND"

    async def test_mark_notification_read_belongs_to_other_user(
        self, client: AsyncClient, test_user: dict
    ):
        """Test cannot mark another user's notification as read."""
        token = test_user["token"]

        # Create notification for a different user
        other_user_id = uuid4()
        async for session in get_session():
            notification = Notification(
                user_id=other_user_id,
                type=NotificationType.TASK_DUE_SOON,
                message="Other user's notification",
                is_read=False,
            )
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            break

        response = await client.patch(
            f"/api/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404  # Returns 404 to prevent enumeration


class TestClearAllNotifications:
    """Tests for DELETE /api/notifications endpoint."""

    async def test_clear_all_notifications(
        self, client: AsyncClient, test_user: dict
    ):
        """Test clearing all notifications for user."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create notifications
        await create_notification(user_id)
        await create_notification(user_id)
        await create_notification(user_id)

        response = await client.delete(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletedCount"] == 3

        # Verify notifications are gone
        list_response = await client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.json()["total"] == 0

    async def test_clear_all_notifications_empty(
        self, client: AsyncClient, test_user: dict
    ):
        """Test clearing when no notifications exist."""
        token = test_user["token"]

        response = await client.delete(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletedCount"] == 0

    async def test_clear_notifications_only_clears_own(
        self, client: AsyncClient, test_user: dict
    ):
        """Test clearing only removes current user's notifications."""
        token = test_user["token"]
        user_id = await get_user_id_from_email("test@example.com")

        # Create notifications for test user
        await create_notification(user_id)
        await create_notification(user_id)

        # Create notification for different user
        other_user_id = uuid4()
        async for session in get_session():
            notification = Notification(
                user_id=other_user_id,
                type=NotificationType.TASK_DUE_SOON,
                message="Other user's notification",
            )
            session.add(notification)
            await session.commit()
            break

        # Clear test user's notifications
        response = await client.delete(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deletedCount"] == 2

        # Verify other user's notification still exists
        async for session in get_session():
            result = await session.execute(
                select(Notification).where(Notification.user_id == other_user_id)
            )
            other_notifications = result.scalars().all()
            assert len(other_notifications) == 1
            break
