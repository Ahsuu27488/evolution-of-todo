"""Scheduler Service for Digest Emails and Background Jobs.

[Task]: T042-T046, T120
[From]: spec.md FR-022 - Digest email frequencies
[From]: spec.md SC-003 - Background processing

[Fix]: User timezone support + reduced reminder interval

Features:
- Daily digest emails (configurable time, default 8 AM) - RESPECTS USER TIMEZONE
- Weekly summary emails (configurable day/time, default Monday 9 AM) - RESPECTS USER TIMEZONE
- Task due reminder checks (every 15 minutes, reduced from hourly)
- Conversation archival (90-day soft delete for old conversations) - T120
- Async background task processing
"""

import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
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

# Check interval for digest emails (hourly) - [Fix]: Approach A for global timezone support
DIGEST_CHECK_INTERVAL_MINUTES = 60  # Check every hour for users whose digest time is now


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

    [Fix]: Timezone-aware digest scheduling check for hourly wake pattern.
    [From]: Approach A - Digest checker wakes every hour and calls this for each user.

    This function is called every hour by the digest checker. It checks if
    the user's local time is within the digest window (default 8 AM for daily,
    Monday 9 AM for weekly). The 15-minute window ensures we don't miss the
    scheduled time due to slight variations in when the job wakes.

    Args:
        user_timezone: User's IANA timezone string
        digest_type: Either 'daily' or 'weekly'
        last_sent: When the digest was last sent (UTC timestamp) - prevents duplicates

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
    # This prevents duplicates when hot-reload creates multiple instances
    if last_sent:
        time_since_last = (now_utc - last_sent).total_seconds()
        if time_since_last < 12 * 3600:  # 12 hours
            logger.debug(
                f"Skipping {digest_type} digest for {user_timezone}: "
                f"sent {time_since_last / 3600:.1f}h ago"
            )
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

    async def _sleep_with_cooperative_cancellation(self, seconds: float) -> bool:
        """Sleep in short intervals to allow checking _running flag.

        [Fix]: Allows graceful shutdown during long waits.
        Instead of one long asyncio.sleep() that can't be interrupted,
        we sleep in chunks and check _running flag each time.

        Args:
            seconds: Total seconds to sleep

        Returns:
            True if slept fully, False if stopped early due to _running=False
        """
        remaining = seconds
        while remaining > 0 and self._running:
            sleep_time = min(remaining, 60)  # Sleep max 60 seconds at a time
            try:
                await asyncio.sleep(sleep_time)
            except asyncio.CancelledError:
                logger.debug("Sleep cancelled during cooperative cancellation")
                raise
            remaining -= sleep_time

        return self._running

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
        # [Fix]: Unified digest checker replaces separate daily/weekly jobs
        cls._tasks = [
            asyncio.create_task(instance._digest_checker_job()),  # Replaces 2 jobs
            asyncio.create_task(instance._task_reminder_job()),
            asyncio.create_task(instance._cleanup_job()),
        ]

        logger.info(f"Scheduler started with {len(cls._tasks)} background tasks")

    @classmethod
    async def stop(cls) -> None:
        """Stop the background scheduler.

        [From]: spec.md SC-003 - Graceful shutdown
        [Fix]: Properly handle task cancellation with cooperative shutdown.

        Changes:
        1. Set _running=False BEFORE cancelling to signal tasks to exit gracefully
        2. Use asyncio.wait with return_when=ALL_COMPLETED for proper cleanup
        3. Increased timeout from 5 to 10 seconds
        4. Handle any pending tasks after timeout
        """
        if not cls._running:
            logger.debug("Scheduler not running, nothing to stop")
            return

        logger.info("Stopping scheduler service")

        # Signal all tasks to stop FIRST - this allows cooperative cancellation
        cls._running = False

        if not cls._tasks:
            logger.info("No tasks to stop")
            return

        # Cancel all tasks
        for task in cls._tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete with longer timeout
        # Use gather with return_exceptions to collect CancelledErrors
        try:
            done, pending = await asyncio.wait(
                cls._tasks,
                timeout=10,  # Increased from 5 to 10 seconds
                return_when=asyncio.ALL_COMPLETED
            )

            # Cancel any pending tasks (shouldn't happen, but safety)
            for task in pending:
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

        except Exception as e:
            logger.warning(f"Error while waiting for tasks to stop: {e}")

        cls._tasks.clear()
        logger.info("Scheduler stopped")

    # ==========================================================================
    # Digest Checker Job (Unified Daily/Weekly)
    # ==========================================================================

    async def _digest_checker_job(self) -> None:
        """Unified digest job that checks hourly for users whose digest time is now.

        [Fix]: Replaces separate daily/weekly jobs with timezone-aware checker.
        [From]: Approach A - Wake every hour, check for matching users

        Instead of waking at a specific UTC time (which doesn't work globally),
        this job wakes every hour and checks if any users have their digest time
        in the current hour window.

        Algorithm:
        1. Wake every hour (on the hour)
        2. Query all users with daily/weekly digest enabled
        3. For each user, check if their local time is within 15 minutes of their scheduled time
        4. Send digests to matching users
        5. Track last_sent per user to prevent duplicates within 12 hours
        """
        logger.info("Digest checker job started")

        # Track last sent times per user per digest type
        # Format: {f"{user_id}:{digest_type}": datetime}
        last_sent_cache: dict[str, datetime] = {}

        while self._running:
            try:
                # Calculate time until next hour boundary
                now = datetime.now(ZoneInfo("UTC"))
                next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                wait_seconds = (next_hour - now).total_seconds()

                logger.info(
                    f"Next digest check in {wait_seconds / 60:.1f} minutes "
                    f"at {next_hour.strftime('%H:%M')} UTC"
                )

                # Sleep until next hour (with cooperative cancellation)
                if not await self._sleep_with_cooperative_cancellation(wait_seconds):
                    break

                if not self._running:
                    break

                # Check for users who need digests now
                await self._send_pending_digests(last_sent_cache)

            except asyncio.CancelledError:
                logger.info("Digest checker job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in digest checker job: {e}")
                # Wait 15 minutes before retrying on error
                if not await self._sleep_with_cooperative_cancellation(15 * 60):
                    break

    # ==========================================================================
    # Daily Digest Job (DEPRECATED - replaced by _digest_checker_job)
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
                now = datetime.now(timezone.utc)
                scheduled_time = datetime.combine(now.date(), DAILY_DIGEST_TIME, tzinfo=timezone.utc)

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

    async def _send_daily_digest_to_user(
        self,
        session: AsyncSession,
        user_id: str,
        user: User,
        user_tz: str,
    ) -> bool:
        """Send daily digest to a specific user.

        [Fix]: Extracted from _send_daily_digests for per-user processing.

        Args:
            session: Database session
            user_id: User ID
            user: User object with email
            user_tz: User's timezone string

        Returns:
            True if email was sent, False if user had no pending tasks
        """
        tz = ZoneInfo(user_tz)
        now_tz = datetime.now(tz)
        today_start = datetime.combine(now_tz.date(), time(0, 0), tzinfo=tz)
        today_end = today_start + timedelta(days=1)

        # Convert to UTC for database query
        today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
        today_end_utc = today_end.astimezone(ZoneInfo("UTC"))

        # Get user's pending tasks
        task_result = await session.execute(
            select(Task).where(
                Task.user_id == user_id,
                Task.completed == False,
                Task.due_date <= today_end_utc,
            )
        )

        tasks = task_result.scalars().all()

        if not tasks:
            logger.debug(f"No tasks for daily digest for user {user_id} ({user_tz})")
            return False

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
            logger.info(
                f"Daily digest sent to {user_id} ({user_tz}) at {now_tz.strftime('%H:%M')} local time"
            )
        else:
            logger.warning(
                f"Failed to send daily digest to {user_id}: {result.get('message')}"
            )

        return result.get("success", False)

    async def _send_weekly_summary_to_user(
        self,
        session: AsyncSession,
        user_id: str,
        user: User,
        user_tz: str,
    ) -> bool:
        """Send weekly summary to a specific user.

        [Fix]: Extracted from _send_weekly_summaries for per-user processing.

        Args:
            session: Database session
            user_id: User ID
            user: User object with email
            user_tz: User's timezone string

        Returns:
            True if email was sent successfully
        """
        # Get all tasks for stats
        task_result = await session.execute(
            select(Task).where(Task.user_id == user_id)
        )

        all_tasks = task_result.scalars().all()

        # Calculate stats using user's timezone
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
            logger.info(
                f"Weekly summary sent to {user_id} ({user_tz}) at {now_tz.strftime('%H:%M')} local time"
            )
        else:
            logger.warning(
                f"Failed to send weekly summary to {user_id}: {result.get('message')}"
            )

        return result.get("success", False)

    async def _send_pending_digests(
        self,
        last_sent_cache: dict[str, datetime],
    ) -> None:
        """Send digest emails to users whose scheduled time is now.

        [Fix]: Timezone-aware digest sending with duplicate prevention.
        This method is called hourly by the digest checker job.

        Args:
            last_sent_cache: Cache tracking last sent times per user per digest type
                              Format: {f"{user_id}:{digest_type}": datetime}
        """
        logger.info("Checking for pending digests to send")

        async with async_session_maker() as session:
            try:
                # Get all users with email digests enabled (daily or weekly)
                result = await session.execute(
                    select(NotificationPreference, User)
                    .join(User, NotificationPreference.user_id == User.id)
                    .where(
                        NotificationPreference.email_enabled == True,
                        NotificationPreference.frequency.in_([
                            EmailFrequency.DAILY,
                            EmailFrequency.WEEKLY,
                        ]),
                    )
                )

                rows = result.all()
                logger.info(f"Found {len(rows)} users with digest enabled")

                now_utc = datetime.now(ZoneInfo("UTC"))

                for pref, user in rows:
                    try:
                        user_id = user.id
                        user_tz = getattr(user, "timezone", "UTC")
                        digest_type = "daily" if pref.frequency == EmailFrequency.DAILY else "weekly"

                        # Check cache key for duplicate prevention
                        cache_key = f"{user_id}:{digest_type}"
                        last_sent = last_sent_cache.get(cache_key)

                        # Check if we should send digest NOW (timezone-aware)
                        if not should_send_digest_now(user_tz, digest_type, last_sent):
                            continue

                        # Send the appropriate digest
                        if digest_type == "daily":
                            await self._send_daily_digest_to_user(session, user_id, user, user_tz)
                        else:
                            await self._send_weekly_summary_to_user(session, user_id, user, user_tz)

                        # Update cache
                        last_sent_cache[cache_key] = now_utc

                        # Small delay between sends
                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.exception(f"Error sending digest to user {user.id}: {e}")
                        await session.rollback()

                logger.info("Digest check complete")

            except Exception as e:
                logger.exception(f"Error in _send_pending_digests: {e}")
                await session.rollback()

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
                        await session.rollback()

                logger.info(f"Daily digest emails complete: {len(rows)} user preferences processed")

            except Exception as e:
                logger.exception(f"Error in _send_daily_digests: {e}")
                await session.rollback()

    # ==========================================================================
    # Weekly Summary Job (DEPRECATED - replaced by _digest_checker_job)
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
                now = datetime.now(timezone.utc)
                current_weekday = now.weekday()

                # Calculate days until next scheduled day
                days_until = (WEEKLY_SUMMARY_DAY - current_weekday) % 7
                if days_until == 0 and now.time() > WEEKLY_SUMMARY_TIME:
                    days_until = 7  # Next week if time has passed

                scheduled_time = datetime.combine(
                    now.date() + timedelta(days=days_until),
                    WEEKLY_SUMMARY_TIME,
                    tzinfo=timezone.utc,
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
                        await session.rollback()

                logger.info(
                    f"Weekly summary emails complete: {len(rows)} user preferences processed"
                )

            except Exception as e:
                logger.exception(f"Error in _send_weekly_summaries: {e}")
                await session.rollback()

    # ==========================================================================
    # Task Reminder Job
    # ==========================================================================

    async def _task_reminder_job(self) -> None:
        """Background job to check for tasks due soon and send reminders.

        [Task]: T046
        [From]: spec.md FR-002 - Task due notifications
        [Fix]: Added cooperative cancellation for graceful shutdown.

        Runs every hour to check for tasks due within 1 hour.
        """
        logger.info("Task reminder job started")

        while self._running:
            try:
                # Wait between checks (with cooperative cancellation)
                if not await self._sleep_with_cooperative_cancellation(
                    TASK_CHECK_INTERVAL_MINUTES * 60
                ):
                    break

                if not self._running:
                    break

                await self._check_and_send_reminders()

            except asyncio.CancelledError:
                logger.info("Task reminder job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in task reminder job: {e}")
                # Wait before retrying on error
                if not await self._sleep_with_cooperative_cancellation(3600):
                    break

    async def _check_and_send_reminders(self) -> None:
        """Check for tasks due soon and send reminder notifications.

        [Task]: T046
        [From]: spec.md FR-002 - Task due notifications

        Sends reminders for tasks due within 1 hour.
        [Fix]: Now validates user exists to prevent foreign key violations.
        """
        logger.info("Checking for tasks due soon")

        async with async_session_maker() as session:
            try:
                # Find tasks due within 1 hour, joining with users to ensure validity
                # [Fix]: Join with User table to prevent orphaned data foreign key errors
                soon = datetime.now(timezone.utc) + timedelta(hours=1)

                result = await session.execute(
                    select(Task).join(User, Task.user_id == User.id).where(
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
                                Notification.created_at >= datetime.now(timezone.utc) - timedelta(hours=2),
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
                        # [Fix]: Rollback session on error to prevent transaction issues
                        logger.exception(f"Error sending reminder for task {task.id}: {e}")
                        await session.rollback()

            except Exception as e:
                # [Fix]: Rollback session on error and continue scheduler operation
                logger.exception(f"Error in _check_and_send_reminders: {e}")
                await session.rollback()

    # ==========================================================================
    # Cleanup Job
    # ==========================================================================

    async def _cleanup_job(self) -> None:
        """Background job to clean up old notifications.

        [From]: spec.md FR-035 - Soft delete notifications archived after 30 days
        [Fix]: Added cooperative cancellation for graceful shutdown.

        Runs daily to permanently delete soft-deleted notifications older than 30 days.
        """
        logger.info("Cleanup job started")

        while self._running:
            try:
                # Wait between cleanup runs (with cooperative cancellation)
                if not await self._sleep_with_cooperative_cancellation(
                    CLEANUP_INTERVAL_HOURS * 3600
                ):
                    break

                if not self._running:
                    break

                await self._cleanup_old_notifications()
                await self._archive_old_conversations()

            except asyncio.CancelledError:
                logger.info("Cleanup job cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in cleanup job: {e}")
                # Wait before retrying on error
                if not await self._sleep_with_cooperative_cancellation(3600):
                    break

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
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)

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
                await session.rollback()

    async def _archive_old_conversations(self) -> None:
        """Archive conversations older than 90 days.

        [Task]: T120 - Conversation archive job (90 days)

        Soft deletes conversations that haven't been updated in 90 days.
        This preserves the data while hiding it from the main UI.
        Messages cascade delete when conversation is soft-deleted.
        """
        logger.info("Archiving old conversations")

        async with async_session_maker() as session:
            try:
                from app.ai.models.conversation import Conversation

                # Soft delete conversations not updated in 90 days
                cutoff = datetime.now(timezone.utc) - timedelta(days=90)

                result = await session.execute(
                    select(Conversation).where(
                        Conversation.updated_at <= cutoff,
                        Conversation.deleted_at.is_(None),  # Not already deleted
                    )
                )

                old_conversations = result.scalars().all()

                for conversation in old_conversations:
                    conversation.deleted_at = datetime.now(timezone.utc)

                await session.commit()

                logger.info(f"Archived {len(old_conversations)} old conversations")

            except Exception as e:
                logger.exception(f"Error in _archive_old_conversations: {e}")
                await session.rollback()


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
