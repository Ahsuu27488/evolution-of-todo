"""Scheduler Service for Digest Emails and Background Jobs.

[Task]: T042-T046
[From]: spec.md FR-022 - Digest email frequencies
[From]: spec.md SC-003 - Background processing

[Fix]: User timezone support + reduced reminder interval

Features:
- Daily digest emails (configurable time, default 8 AM) - RESPECTS USER TIMEZONE
- Weekly summary emails (configurable day/time, default Monday 9 AM) - RESPECTS USER TIMEZONE
- Task due reminder checks (every 15 minutes, reduced from hourly)
- Async background task processing
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_maker
from app.models.notification import NotificationPreference, EmailFrequency, NotificationType
from app.models import Task, User
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


# =============================================================================
# Scheduler Configuration
# =============================================================================

# Default schedule times (can be overridden via env vars)
DAILY_DIGEST_TIME = time(8, 0)  # 8:00 AM
WEEKLY_SUMMARY_DAY = 0  # Monday (0=Monday, 6=Sunday)
WEEKLY_SUMMARY_TIME = time(9, 0)  # 9:00 AM

# Check interval for background tasks
# [Fix]: Reduced from 60 to 15 minutes to catch tasks due in the gap
TASK_CHECK_INTERVAL_MINUTES = 15
CLEANUP_INTERVAL_HOURS = 24


# =============================================================================
# Helper Functions for Timezone-Aware Scheduling
# =============================================================================


def get_next_daily_digest_time(
    user_timezone: str,
    base_time: time = DAILY_DIGEST_TIME,
) -> datetime:
    """Calculate the next daily digest time for a user in their timezone.

    [Fix]: Timezone-aware scheduling for daily digests

    Args:
        user_timezone: User's IANA timezone string (e.g., 'America/New_York')
        base_time: The time to send the digest (default 8:00 AM)

    Returns:
        datetime object representing the next scheduled digest time in UTC
    """
    tz = ZoneInfo(user_timezone)
    now = datetime.now(tz)

    # Create today's scheduled time in user's timezone
    scheduled_today = datetime.combine(now.date(), base_time, tzinfo=tz)

    if now >= scheduled_today:
        # Already passed the time today, schedule for tomorrow
        scheduled_today += timedelta(days=1)

    # Convert to UTC for comparison with utcnow()
    return scheduled_today.astimezone(ZoneInfo("UTC"))


def get_next_weekly_summary_time(
    user_timezone: str,
    target_weekday: int = WEEKLY_SUMMARY_DAY,
    base_time: time = WEEKLY_SUMMARY_TIME,
) -> datetime:
    """Calculate the next weekly summary time for a user in their timezone.

    [Fix]: Timezone-aware scheduling for weekly summaries

    Args:
        user_timezone: User's IANA timezone string
        target_weekday: Target weekday (0=Monday, 6=Sunday)
        base_time: The time to send the summary (default 9:00 AM)

    Returns:
        datetime object representing the next scheduled summary time in UTC
    """
    tz = ZoneInfo(user_timezone)
    now = datetime.now(tz)
    current_weekday = now.weekday()

    # Calculate days until next target day
    days_until = (target_weekday - current_weekday) % 7
    if days_until == 0 and now.time() >= base_time:
        days_until = 7  # Next week if time has passed today

    # Create the scheduled date in user's timezone
    scheduled_date = (now + timedelta(days=days_until)).date()
    scheduled_datetime = datetime.combine(scheduled_date, base_time, tzinfo=tz)

    # Convert to UTC
    return scheduled_datetime.astimezone(ZoneInfo("UTC"))


def should_send_digest_now(
    user_timezone: str,
    digest_type: str = "daily",
    last_sent: Optional[datetime] = None,
) -> bool:
    """Check if a digest should be sent to a user right now.

    [Fix]: Timezone-aware digest scheduling check

    Args:
        user_timezone: User's IANA timezone string
        digest_type: Either 'daily' or 'weekly'
        last_sent: When the digest was last sent (optional)

    Returns:
        True if the digest should be sent now
    """
    tz = ZoneInfo(user_timezone)
    now_utc = datetime.now(ZoneInfo("UTC"))
    now_user_tz = now_utc.astimezone(tz)

    if digest_type == "daily":
        target_time = DAILY_DIGEST_TIME
        target_weekday = None
    else:  # weekly
        target_time = WEEKLY_SUMMARY_TIME
        target_weekday = WEEKLY_SUMMARY_DAY

    # Check if current time matches the scheduled time
    # We allow a 15-minute window to ensure we don't miss it
    time_match = abs(
        (now_user_tz.hour - target_time.hour) * 60
        + (now_user_tz.minute - target_time.minute)
    ) <= 15

    if digest_type == "weekly":
        # Must also be the correct weekday
        if now_user_tz.weekday() != target_weekday:
            return False

    # Check if we haven't sent it too recently (within 12 hours)
    if last_sent:
        time_since_last = (now_utc - last_sent).total_seconds()
        if time_since_last < 12 * 3600:  # 12 hours
            return False

    return time_match


# =============================================================================
# Scheduler Service
# =============================================================================


class SchedulerService:
    """Background scheduler service for periodic tasks.

    [Task]: T042-T046
    [From]: spec.md SC-003 - Background processing

    Runs as an async background task processing:
    - Daily digest emails
    - Weekly summary emails
    - Task due reminders
    - Notification cleanup
    """

    _instance: Optional["SchedulerService"] = None
    _running: bool = False
    _tasks: list[asyncio.Task] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "SchedulerService":
        """Get or create the singleton instance."""
        return cls()

    @classmethod
    async def start(cls) -> None:
        """Start the background scheduler.

        [Task]: T042
        [From]: spec.md SC-003 - Background processing

        Launches all background tasks as async tasks.
        """
        if cls._running:
            logger.warning("Scheduler already running")
            return

        cls._running = True
        instance = cls.get_instance()

        logger.info("Starting scheduler service")

        # Launch background tasks
        cls._tasks = [
            asyncio.create_task(instance._daily_digest_job()),
            asyncio.create_task(instance._weekly_summary_job()),
            asyncio.create_task(instance._task_reminder_job()),
            asyncio.create_task(instance._cleanup_job()),
        ]

        logger.info(f"Scheduler started with {len(cls._tasks)} background tasks")

    @classmethod
    async def stop(cls) -> None:
        """Stop the background scheduler.

        [From]: spec.md SC-003 - Graceful shutdown

        Cancels all running background tasks.
        """
        if not cls._running:
            return

        logger.info("Stopping scheduler service")
        cls._running = False

        # Cancel all tasks
        for task in cls._tasks:
            task.cancel()

        # Wait for tasks to complete (with timeout)
        if cls._tasks:
            await asyncio.wait(cls._tasks, timeout=5)

        cls._tasks.clear()
        logger.info("Scheduler stopped")

    # ==========================================================================
    # Daily Digest Job
    # ==========================================================================

    async def _daily_digest_job(self) -> None:
        """Background job for daily digest emails.

        [Task]: T042
        [From]: spec.md FR-022 - Daily digest frequency

        Runs once per day at configured time, sending digest emails
        to users who have daily frequency enabled.
        """
        logger.info("Daily digest job started")

        while self._running:
            try:
                # Calculate time until next run
                now = datetime.now()
                scheduled_time = datetime.combine(now.date(), DAILY_DIGEST_TIME)

                # If we've passed the time today, schedule for tomorrow
                if now >= scheduled_time:
                    scheduled_time += timedelta(days=1)

                wait_seconds = (scheduled_time - now).total_seconds()

                logger.info(
                    f"Next daily digest in {wait_seconds / 3600:.1f} hours "
                    f"at {scheduled_time.strftime('%H:%M')}"
                )

                # Wait until scheduled time
                await asyncio.sleep(wait_seconds)

                # Check if still running
                if not self._running:
                    break

                # Send daily digests
                await self._send_daily_digests()

            except asyncio.CancelledError:
                logger.info("Daily digest job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in daily digest job: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)

    async def _send_daily_digests(self) -> None:
        """Send daily digest emails to all users with daily frequency.

        [Task]: T043
        [From]: spec.md FR-022 - Daily digest frequency
        [Fix]: Now respects user timezone for accurate scheduling
        """
        logger.info("Sending daily digest emails")

        async with async_session_maker() as session:
            try:
                # Find users with daily frequency enabled
                # Join with users table to get timezone
                result = await session.execute(
                    select(NotificationPreference, User)
                    .join(User, NotificationPreference.user_id == User.id)
                    .where(
                        NotificationPreference.email_enabled == True,
                        NotificationPreference.frequency == EmailFrequency.DAILY,
                    )
                )

                rows = result.all()
                logger.info(f"Found {len(rows)} user preferences for daily digest")

                for pref, user in rows:
                    try:
                        # [Fix]: Check if we should send digest based on user's timezone
                        user_tz = getattr(user, "timezone", "UTC")
                        if not should_send_digest_now(user_tz, "daily"):
                            continue

                        user_id = user.id

                        # Get user's pending tasks due today or overdue
                        # [Fix]: Use user's timezone for "today" calculation
                        tz = ZoneInfo(user_tz)
                        now_tz = datetime.now(tz)
                        today_start = datetime.combine(now_tz.date(), time(0, 0), tzinfo=tz)
                        today_end = today_start + timedelta(days=1)

                        # Convert to UTC for database query
                        today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
                        today_end_utc = today_end.astimezone(ZoneInfo("UTC"))

                        task_result = await session.execute(
                            select(Task).where(
                                Task.user_id == user_id,
                                Task.completed == False,
                                Task.due_date <= today_end_utc,
                            )
                        )

                        tasks = task_result.scalars().all()

                        if not tasks:
                            logger.debug(f"No tasks for daily digest for user {user_id}")
                            continue

                        # Build task list for email
                        task_list = [
                            {
                                "title": task.title,
                                "due_date": task.due_date.strftime("%Y-%m-%d")
                                if task.due_date
                                else "No due date",
                                "completed": task.completed,
                            }
                            for task in tasks[:10]  # Limit to 10 tasks
                        ]

                        # Send digest email
                        result = await EmailService.send_daily_digest(
                            session=session,
                            user_id=user_id,
                            to=user.email,
                            tasks=task_list,
                        )

                        if result.get("success"):
                            logger.info(f"Daily digest sent to {user_id} ({user_tz})")
                        else:
                            logger.warning(
                                f"Failed to send daily digest to {user_id}: {result.get('message')}"
                            )

                        # Small delay between sends to avoid rate limits
                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.exception(f"Error sending daily digest to {user.id}: {e}")

                logger.info(f"Daily digest emails complete: {len(rows)} user preferences processed")

            except Exception as e:
                logger.exception(f"Error in _send_daily_digests: {e}")

    # ==========================================================================
    # Weekly Summary Job
    # ==========================================================================

    async def _weekly_summary_job(self) -> None:
        """Background job for weekly summary emails.

        [Task]: T044
        [From]: spec.md FR-022 - Weekly digest frequency

        Runs once per week on configured day/time.
        """
        logger.info("Weekly summary job started")

        while self._running:
            try:
                now = datetime.now()
                current_weekday = now.weekday()

                # Calculate days until next scheduled day
                days_until = (WEEKLY_SUMMARY_DAY - current_weekday) % 7
                if days_until == 0 and now.time() > WEEKLY_SUMMARY_TIME:
                    days_until = 7  # Next week if time has passed

                scheduled_time = datetime.combine(
                    now.date() + timedelta(days=days_until),
                    WEEKLY_SUMMARY_TIME,
                )

                wait_seconds = (scheduled_time - now).total_seconds()

                logger.info(
                    f"Next weekly summary in {wait_seconds / 86400:.1f} days "
                    f"on {scheduled_time.strftime('%A at %H:%M')}"
                )

                await asyncio.sleep(wait_seconds)

                if not self._running:
                    break

                await self._send_weekly_summaries()

            except asyncio.CancelledError:
                logger.info("Weekly summary job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in weekly summary job: {e}")
                await asyncio.sleep(3600)

    async def _send_weekly_summaries(self) -> None:
        """Send weekly summary emails to all users with weekly frequency.

        [Task]: T045
        [From]: spec.md FR-022 - Weekly digest frequency
        [Fix]: Now respects user timezone for accurate scheduling
        """
        logger.info("Sending weekly summary emails")

        async with async_session_maker() as session:
            try:
                # Find users with weekly frequency enabled
                # Join with users table to get timezone
                result = await session.execute(
                    select(NotificationPreference, User)
                    .join(User, NotificationPreference.user_id == User.id)
                    .where(
                        NotificationPreference.email_enabled == True,
                        NotificationPreference.frequency == EmailFrequency.WEEKLY,
                    )
                )

                rows = result.all()
                logger.info(f"Found {len(rows)} user preferences for weekly summary")

                for pref, user in rows:
                    try:
                        # [Fix]: Check if we should send digest based on user's timezone
                        user_tz = getattr(user, "timezone", "UTC")
                        if not should_send_digest_now(user_tz, "weekly"):
                            continue

                        user_id = user.id

                        # Get weekly statistics
                        task_result = await session.execute(
                            select(Task).where(Task.user_id == user_id)
                        )

                        all_tasks = task_result.scalars().all()

                        # Calculate stats using user's timezone for "today"
                        tz = ZoneInfo(user_tz)
                        now_tz = datetime.now(tz)
                        today = now_tz.date()

                        completed = sum(1 for t in all_tasks if t.completed)
                        pending = sum(
                            1
                            for t in all_tasks
                            if not t.completed
                            and t.due_date
                            and t.due_date.date() >= today
                        )
                        overdue = sum(
                            1
                            for t in all_tasks
                            if not t.completed
                            and t.due_date
                            and t.due_date.date() < today
                        )

                        stats = {
                            "completed": completed,
                            "pending": pending,
                            "overdue": overdue,
                        }

                        # Send summary email
                        result = await EmailService.send_weekly_summary(
                            session=session,
                            user_id=user_id,
                            to=user.email,
                            stats=stats,
                        )

                        if result.get("success"):
                            logger.info(f"Weekly summary sent to {user_id} ({user_tz})")
                        else:
                            logger.warning(
                                f"Failed to send weekly summary to {user_id}: {result.get('message')}"
                            )

                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.exception(f"Error sending weekly summary to {user.id}: {e}")

                logger.info(
                    f"Weekly summary emails complete: {len(rows)} user preferences processed"
                )

            except Exception as e:
                logger.exception(f"Error in _send_weekly_summaries: {e}")

    # ==========================================================================
    # Task Reminder Job
    # ==========================================================================

    async def _task_reminder_job(self) -> None:
        """Background job to check for tasks due soon and send reminders.

        [Task]: T046
        [From]: spec.md FR-002 - Task due notifications

        Runs every hour to check for tasks due within 1 hour.
        """
        logger.info("Task reminder job started")

        while self._running:
            try:
                # Wait 1 hour between checks
                await asyncio.sleep(TASK_CHECK_INTERVAL_MINUTES * 60)

                if not self._running:
                    break

                await self._check_and_send_reminders()

            except asyncio.CancelledError:
                logger.info("Task reminder job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in task reminder job: {e}")
                await asyncio.sleep(3600)

    async def _check_and_send_reminders(self) -> None:
        """Check for tasks due soon and send reminder notifications.

        [Task]: T046
        [From]: spec.md FR-002 - Task due notifications

        Sends reminders for tasks due within 1 hour.
        """
        logger.info("Checking for tasks due soon")

        async with async_session_maker() as session:
            try:
                # Find tasks due within 1 hour
                soon = datetime.now() + timedelta(hours=1)

                result = await session.execute(
                    select(Task).where(
                        Task.completed == False,
                        Task.due_date <= soon,
                    )
                )

                tasks = result.scalars().all()

                if not tasks:
                    logger.info("No tasks due soon")
                    return

                logger.info(f"Found {len(tasks)} tasks due soon")

                # Create notifications for each task
                from app.models.notification import Notification
                from app.services.notification_service import NotificationService

                for task in tasks:
                    try:
                        # Check if we already sent a reminder recently
                        existing = await session.execute(
                            select(Notification).where(
                                Notification.related_task_id == task.id,
                                Notification.type == NotificationType.TASK_DUE,
                                Notification.created_at >= datetime.now() - timedelta(hours=2),
                            )
                        )

                        if existing.scalars().first():
                            continue  # Already notified recently

                        # Create reminder notification
                        await NotificationService.create_notification(
                            session=session,
                            user_id=task.user_id,
                            type=NotificationType.TASK_DUE,
                            title=f"Task Due Soon: {task.title}",
                            message=f"Your task '{task.title}' is due soon",
                            data={
                                "task_id": task.id,
                                "task_title": task.title,
                                "due_date": task.due_date.isoformat() if task.due_date else None,
                            },
                            related_task_id=task.id,
                        )

                        logger.info(f"Reminder sent for task {task.id}")

                    except Exception as e:
                        logger.exception(f"Error sending reminder for task {task.id}: {e}")

            except Exception as e:
                logger.exception(f"Error in _check_and_send_reminders: {e}")

    # ==========================================================================
    # Cleanup Job
    # ==========================================================================

    async def _cleanup_job(self) -> None:
        """Background job to clean up old notifications.

        [From]: spec.md FR-035 - Soft delete notifications archived after 30 days

        Runs daily to permanently delete soft-deleted notifications older than 30 days.
        """
        logger.info("Cleanup job started")

        while self._running:
            try:
                # Wait 24 hours between cleanup runs
                await asyncio.sleep(CLEANUP_INTERVAL_HOURS * 3600)

                if not self._running:
                    break

                await self._cleanup_old_notifications()

            except asyncio.CancelledError:
                logger.info("Cleanup job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in cleanup job: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_notifications(self) -> None:
        """Permanently delete old soft-deleted notifications.

        [From]: spec.md FR-035 - 30-day archive
        """
        logger.info("Cleaning up old notifications")

        async with async_session_maker() as session:
            try:
                from app.models.notification import Notification
                from datetime import timedelta

                # Delete notifications soft-deleted more than 30 days ago
                cutoff = datetime.now() - timedelta(days=30)

                result = await session.execute(
                    select(Notification).where(
                        Notification.deleted_at <= cutoff,
                    )
                )

                old_notifications = result.scalars().all()

                for notification in old_notifications:
                    await session.delete(notification)

                await session.commit()

                logger.info(f"Cleaned up {len(old_notifications)} old notifications")

            except Exception as e:
                logger.exception(f"Error in _cleanup_old_notifications: {e}")


# =============================================================================
# Startup/Shutdown Functions
# =============================================================================


async def start_scheduler() -> None:
    """Start the scheduler service.

    Called during application startup.
    """
    await SchedulerService.start()


async def stop_scheduler() -> None:
    """Stop the scheduler service.

    Called during application shutdown.
    """
    await SchedulerService.stop()
