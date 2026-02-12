"""Notification routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select, func

from app.core.deps import CurrentUser, DbSession
from app.models.notification import Notification
from app.schemas.notification import (
    ClearNotificationsResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def notification_to_response(notification: Notification) -> NotificationResponse:
    """Convert Notification model to response schema."""
    return NotificationResponse(
        id=str(notification.id),
        userId=str(notification.user_id),
        taskId=str(notification.task_id) if notification.task_id else None,
        type=notification.type,
        message=notification.message,
        isRead=notification.is_read,
        createdAt=notification.created_at.isoformat(),
    )


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(20, ge=1, le=50),
    unread_only: bool = Query(False, alias="unreadOnly"),
) -> NotificationListResponse:
    """List notifications for the authenticated user.

    Returns notifications sorted by created_at DESC (newest first).
    """
    # Build query
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)  # noqa: E712

    # Order by newest first and apply limit
    query = query.order_by(Notification.created_at.desc()).limit(limit)

    result = await session.execute(query)
    notifications = result.scalars().all()

    # Get unread count
    unread_query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,  # noqa: E712
    )
    unread_result = await session.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    return NotificationListResponse(
        notifications=[notification_to_response(n) for n in notifications],
        total=len(notifications),
        unreadCount=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: CurrentUser,
    session: DbSession,
) -> UnreadCountResponse:
    """Get unread notification count (lightweight endpoint for polling)."""
    query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,  # noqa: E712
    )
    result = await session.execute(query)
    count = result.scalar() or 0

    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> NotificationResponse:
    """Mark a single notification as read."""
    result = await session.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOTIFICATION_NOT_FOUND", "message": "Notification not found"},
        )

    notification.is_read = True
    await session.flush()
    await session.refresh(notification)

    return notification_to_response(notification)


@router.delete("", response_model=ClearNotificationsResponse)
async def clear_all_notifications(
    current_user: CurrentUser,
    session: DbSession,
) -> ClearNotificationsResponse:
    """Clear all notifications for the current user."""
    # Get all notifications for user
    result = await session.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    notifications = result.scalars().all()

    deleted_count = len(notifications)

    # Delete each notification
    for notification in notifications:
        await session.delete(notification)

    return ClearNotificationsResponse(success=True, deletedCount=deleted_count)
