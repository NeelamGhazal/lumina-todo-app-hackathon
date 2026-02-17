"""APScheduler configuration and background jobs for notifications."""

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import async_session_maker
from app.services.notification_service import (
    cleanup_old_notifications,
    generate_due_soon_notifications,
    generate_overdue_notifications,
)

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def generate_task_notifications_job():
    """Background job to generate due-soon and overdue notifications.

    Runs hourly (at minute 0 of each hour).
    """
    logger.info("Running generate_task_notifications job...")

    async with async_session_maker() as session:
        try:
            due_soon_count = await generate_due_soon_notifications(session)
            overdue_count = await generate_overdue_notifications(session)
            await session.commit()

            logger.info(
                f"Notification job complete: {due_soon_count} due-soon, {overdue_count} overdue"
            )
            return {"due_soon_count": due_soon_count, "overdue_count": overdue_count}
        except Exception as e:
            logger.error(f"Error in notification job: {e}")
            await session.rollback()
            raise


async def cleanup_notifications_job():
    """Background job to delete old notifications.

    Runs daily at midnight (00:00).
    Removes notifications older than 30 days.
    """
    logger.info("Running cleanup_notifications job...")

    async with async_session_maker() as session:
        try:
            deleted_count = await cleanup_old_notifications(session, days=30)
            await session.commit()

            logger.info(f"Cleanup job complete: {deleted_count} notifications deleted")
            return {"deleted_count": deleted_count}
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
            await session.rollback()
            raise


def start_scheduler():
    """Start the scheduler with configured jobs."""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    # Add hourly notification generation job (at minute 0)
    scheduler.add_job(
        generate_task_notifications_job,
        trigger=CronTrigger(minute=0),  # Every hour at :00
        id="generate_task_notifications",
        name="Generate task notifications",
        replace_existing=True,
    )
    logger.info("Scheduled job 'generate_task_notifications' with pattern '0 * * * *'")

    # Add daily cleanup job (at midnight)
    scheduler.add_job(
        cleanup_notifications_job,
        trigger=CronTrigger(hour=0, minute=0),  # Daily at 00:00
        id="cleanup_old_notifications",
        name="Cleanup old notifications",
        replace_existing=True,
    )
    logger.info("Scheduled job 'cleanup_old_notifications' with pattern '0 0 * * *'")

    scheduler.start()
    logger.info("Scheduler started successfully")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown complete")


async def trigger_notification_job_manually():
    """Manually trigger the notification generation job.

    Used for testing to verify cron job logic works correctly.
    Returns the counts of notifications created.
    """
    logger.info("Manually triggering notification job...")
    return await generate_task_notifications_job()
