"""Tests for notification service."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlmodel import select

from app.core.database import get_session
from app.models.notification import Notification, NotificationType
from app.models.task import Task
from app.models.user import User
from app.services.notification_service import (
    check_duplicate_exists,
    cleanup_old_notifications,
    create_notification,
    generate_due_soon_notifications,
    generate_overdue_notifications,
)


async def get_test_user_id(email: str = "test@example.com"):
    """Helper to get user ID from email."""
    async for session in get_session():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return user.id
        return None


async def create_task_for_user(
    user_id,
    title: str = "Test Task",
    due_date=None,
    completed: bool = False,
):
    """Helper to create a task directly in the database."""
    async for session in get_session():
        task = Task(
            user_id=user_id,
            title=title,
            due_date=due_date,
            completed=completed,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


class TestCreateNotification:
    """Tests for create_notification function."""

    async def test_create_notification_success(
        self, client: AsyncClient, test_user: dict
    ):
        """Test creating a notification successfully."""
        user_id = await get_test_user_id()

        async for session in get_session():
            notification = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="Test notification",
            )
            await session.commit()

            assert notification is not None
            assert notification.user_id == user_id
            assert notification.type == NotificationType.TASK_DUE_SOON
            assert notification.message == "Test notification"
            assert notification.is_read is False
            break

    async def test_create_notification_with_task_id(
        self, client: AsyncClient, test_user: dict
    ):
        """Test creating a notification linked to a task."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id, title="Task with notification")

        async for session in get_session():
            notification = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="Task is due soon",
                task_id=task.id,
            )
            await session.commit()

            assert notification is not None
            assert notification.task_id == task.id
            break

    async def test_create_notification_prevents_duplicates(
        self, client: AsyncClient, test_user: dict
    ):
        """Test that duplicate notifications are prevented for same task+type."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id, title="Duplicate test task")

        async for session in get_session():
            # First notification should succeed
            n1 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="First notification",
                task_id=task.id,
            )
            await session.commit()
            assert n1 is not None

            # Second notification with same task+type should return None
            n2 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="Duplicate notification",
                task_id=task.id,
            )

            assert n2 is None
            break

    async def test_create_notification_allows_different_types(
        self, client: AsyncClient, test_user: dict
    ):
        """Test that different notification types for same task are allowed."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id, title="Multi-type test task")

        async for session in get_session():
            # Create DUE_SOON notification
            n1 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="Due soon",
                task_id=task.id,
            )
            await session.commit()

            # Create OVERDUE notification for same task (should succeed)
            n2 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_OVERDUE,
                message="Overdue",
                task_id=task.id,
            )
            await session.commit()

            assert n1 is not None
            assert n2 is not None
            break

    async def test_create_notification_completed_allows_duplicates(
        self, client: AsyncClient, test_user: dict
    ):
        """Test that TASK_COMPLETED notifications can have duplicates."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id, title="Completed task")

        async for session in get_session():
            # First completion notification
            n1 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_COMPLETED,
                message="Completed first time",
                task_id=task.id,
            )
            await session.commit()

            # Second completion notification (user uncompleted then completed again)
            n2 = await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_COMPLETED,
                message="Completed second time",
                task_id=task.id,
            )
            await session.commit()

            assert n1 is not None
            assert n2 is not None
            break


class TestCheckDuplicateExists:
    """Tests for check_duplicate_exists function."""

    async def test_check_duplicate_returns_false_when_none(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns False when no notification exists."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id)

        async for session in get_session():
            exists = await check_duplicate_exists(
                session=session,
                task_id=task.id,
                notification_type=NotificationType.TASK_DUE_SOON,
            )
            assert exists is False
            break

    async def test_check_duplicate_returns_true_when_exists(
        self, client: AsyncClient, test_user: dict
    ):
        """Test returns True when notification exists."""
        user_id = await get_test_user_id()
        task = await create_task_for_user(user_id)

        async for session in get_session():
            # Create a notification
            await create_notification(
                session=session,
                user_id=user_id,
                notification_type=NotificationType.TASK_DUE_SOON,
                message="Test",
                task_id=task.id,
            )
            await session.commit()

            # Check duplicate
            exists = await check_duplicate_exists(
                session=session,
                task_id=task.id,
                notification_type=NotificationType.TASK_DUE_SOON,
            )
            assert exists is True
            break


class TestGenerateDueSoonNotifications:
    """Tests for generate_due_soon_notifications function."""

    async def test_generate_due_soon_finds_tasks_due_tomorrow(
        self, client: AsyncClient, test_user: dict
    ):
        """Test finds tasks with due_date = tomorrow."""
        user_id = await get_test_user_id()
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()

        # Create task due tomorrow
        task = await create_task_for_user(
            user_id, title="Due tomorrow task", due_date=tomorrow
        )

        async for session in get_session():
            count = await generate_due_soon_notifications(session)
            await session.commit()

            assert count == 1

            # Verify notification was created
            result = await session.execute(
                select(Notification).where(
                    Notification.task_id == task.id,
                    Notification.type == NotificationType.TASK_DUE_SOON,
                )
            )
            notification = result.scalar_one_or_none()
            assert notification is not None
            assert "Due tomorrow task" in notification.message
            break

    async def test_generate_due_soon_ignores_completed_tasks(
        self, client: AsyncClient, test_user: dict
    ):
        """Test ignores tasks that are already completed."""
        user_id = await get_test_user_id()
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()

        # Create completed task due tomorrow
        await create_task_for_user(
            user_id, title="Completed task", due_date=tomorrow, completed=True
        )

        async for session in get_session():
            count = await generate_due_soon_notifications(session)
            assert count == 0
            break

    async def test_generate_due_soon_no_duplicates(
        self, client: AsyncClient, test_user: dict
    ):
        """Test doesn't create duplicate notifications."""
        user_id = await get_test_user_id()
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()

        await create_task_for_user(user_id, title="Task", due_date=tomorrow)

        async for session in get_session():
            # First run creates notification
            count1 = await generate_due_soon_notifications(session)
            await session.commit()
            assert count1 == 1

            # Second run should create 0 (duplicate prevention)
            count2 = await generate_due_soon_notifications(session)
            assert count2 == 0
            break


class TestGenerateOverdueNotifications:
    """Tests for generate_overdue_notifications function."""

    async def test_generate_overdue_finds_past_due_tasks(
        self, client: AsyncClient, test_user: dict
    ):
        """Test finds tasks with due_date < today."""
        user_id = await get_test_user_id()
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date()

        task = await create_task_for_user(
            user_id, title="Overdue task", due_date=yesterday
        )

        async for session in get_session():
            count = await generate_overdue_notifications(session)
            await session.commit()

            assert count == 1

            # Verify notification was created
            result = await session.execute(
                select(Notification).where(
                    Notification.task_id == task.id,
                    Notification.type == NotificationType.TASK_OVERDUE,
                )
            )
            notification = result.scalar_one_or_none()
            assert notification is not None
            assert "overdue" in notification.message.lower()
            break

    async def test_generate_overdue_ignores_completed_tasks(
        self, client: AsyncClient, test_user: dict
    ):
        """Test ignores completed overdue tasks."""
        user_id = await get_test_user_id()
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date()

        await create_task_for_user(
            user_id, title="Completed overdue", due_date=yesterday, completed=True
        )

        async for session in get_session():
            count = await generate_overdue_notifications(session)
            assert count == 0
            break


class TestCleanupOldNotifications:
    """Tests for cleanup_old_notifications function."""

    async def test_cleanup_removes_old_notifications(
        self, client: AsyncClient, test_user: dict
    ):
        """Test removes notifications older than specified days."""
        user_id = await get_test_user_id()

        async for session in get_session():
            # Create an old notification (manually set created_at)
            old_notification = Notification(
                user_id=user_id,
                type=NotificationType.TASK_DUE_SOON,
                message="Old notification",
            )
            session.add(old_notification)
            await session.flush()

            # Update created_at to 31 days ago
            old_notification.created_at = datetime.now(UTC) - timedelta(days=31)
            await session.commit()

            # Create a recent notification
            recent_notification = Notification(
                user_id=user_id,
                type=NotificationType.TASK_DUE_SOON,
                message="Recent notification",
            )
            session.add(recent_notification)
            await session.commit()

            # Run cleanup
            deleted_count = await cleanup_old_notifications(session, days=30)
            await session.commit()

            assert deleted_count == 1

            # Verify old notification is gone, recent remains
            result = await session.execute(
                select(Notification).where(Notification.user_id == user_id)
            )
            remaining = result.scalars().all()
            assert len(remaining) == 1
            assert remaining[0].message == "Recent notification"
            break

    async def test_cleanup_with_no_old_notifications(
        self, client: AsyncClient, test_user: dict
    ):
        """Test cleanup when no old notifications exist."""
        user_id = await get_test_user_id()

        async for session in get_session():
            # Create only recent notifications
            notification = Notification(
                user_id=user_id,
                type=NotificationType.TASK_DUE_SOON,
                message="Recent",
            )
            session.add(notification)
            await session.commit()

            deleted_count = await cleanup_old_notifications(session, days=30)
            assert deleted_count == 0
            break
