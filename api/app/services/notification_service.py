"""Notification service for generating and managing notifications."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete

from app.models.notification import Notification, NotificationType
from app.models.task import Task

logger = logging.getLogger(__name__)


async def check_duplicate_exists(
    session: AsyncSession,
    task_id: UUID,
    notification_type: NotificationType,
) -> bool:
    """Check if a notification already exists for this task and type.

    Used to prevent duplicate due-soon and overdue notifications.
    """
    query = select(Notification).where(
        Notification.task_id == task_id,
        Notification.type == notification_type,
    )
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None


async def create_notification(
    session: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    message: str,
    task_id: UUID | None = None,
) -> Notification | None:
    """Create a notification if it doesn't already exist.

    For TASK_DUE_SOON and TASK_OVERDUE, checks for duplicates first.
    For TASK_COMPLETED, always creates (user may complete/uncomplete).

    Returns the notification if created, None if duplicate prevented.
    """
    # Check for duplicates (except for TASK_COMPLETED which can have multiple)
    if task_id and notification_type != NotificationType.TASK_COMPLETED:
        if await check_duplicate_exists(session, task_id, notification_type):
            logger.debug(
                f"Duplicate notification prevented: task_id={task_id}, type={notification_type}"
            )
            return None

    notification = Notification(
        user_id=user_id,
        task_id=task_id,
        type=notification_type,
        message=message,
    )
    session.add(notification)
    await session.flush()
    await session.refresh(notification)

    logger.info(f"Created notification: {notification_type.value} for user {user_id}")
    return notification


async def generate_due_soon_notifications(session: AsyncSession) -> int:
    """Generate notifications for tasks due tomorrow.

    Finds all incomplete tasks with due_date = tomorrow that don't already
    have a TASK_DUE_SOON notification.

    Returns the count of notifications created.
    """
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()

    # Find tasks due tomorrow without existing due-soon notification
    query = (
        select(Task)
        .where(
            Task.due_date == tomorrow,
            Task.completed == False,  # noqa: E712
        )
    )
    result = await session.execute(query)
    tasks = result.scalars().all()

    created_count = 0
    for task in tasks:
        notification = await create_notification(
            session=session,
            user_id=task.user_id,
            notification_type=NotificationType.TASK_DUE_SOON,
            message=f"Task '{task.title}' is due tomorrow",
            task_id=task.id,
        )
        if notification:
            created_count += 1

    logger.info(f"Generated {created_count} due-soon notifications")
    return created_count


async def generate_overdue_notifications(session: AsyncSession) -> int:
    """Generate notifications for overdue tasks.

    Finds all incomplete tasks with due_date < today that don't already
    have a TASK_OVERDUE notification.

    Returns the count of notifications created.
    """
    today = datetime.now(UTC).date()

    # Find overdue tasks
    query = (
        select(Task)
        .where(
            Task.due_date < today,
            Task.completed == False,  # noqa: E712
        )
    )
    result = await session.execute(query)
    tasks = result.scalars().all()

    created_count = 0
    for task in tasks:
        notification = await create_notification(
            session=session,
            user_id=task.user_id,
            notification_type=NotificationType.TASK_OVERDUE,
            message=f"Task '{task.title}' is overdue",
            task_id=task.id,
        )
        if notification:
            created_count += 1

    logger.info(f"Generated {created_count} overdue notifications")
    return created_count


async def cleanup_old_notifications(
    session: AsyncSession,
    days: int = 30,
) -> int:
    """Delete notifications older than specified days.

    Default retention is 30 days per spec.

    Returns the count of notifications deleted.
    """
    cutoff_date = datetime.now(UTC) - timedelta(days=days)

    # Count notifications to be deleted
    count_query = select(Notification).where(Notification.created_at < cutoff_date)
    count_result = await session.execute(count_query)
    notifications_to_delete = count_result.scalars().all()
    deleted_count = len(notifications_to_delete)

    # Delete old notifications
    if deleted_count > 0:
        delete_query = delete(Notification).where(Notification.created_at < cutoff_date)
        await session.execute(delete_query)

    logger.info(f"Cleaned up {deleted_count} notifications older than {days} days")
    return deleted_count
