"""NotificationService for notification CRUD operations.

[Task]: T012
[From]: spec.md FR-001, FR-005, FR-008, contracts/api.yaml
[From]: Context7 /fastapi-guide for service patterns
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import (
    Notification,
    NotificationList,
    NotificationPreference,
    NotificationPublic,
    NotificationType,
    EmailFrequency,
)
from app.simple_auth import get_current_user_id
from app.services.sse_service import SSEService


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification CRUD operations.

    [Task]: T012
    [From]: spec.md FR-001, FR-005, FR-008, FR-009
    [From]: contracts/api.yaml §1 - In-App Notifications API

    [Fix]: Type-aware deduplication windows for better timing

    Handles:
    - Creating notifications
    - Listing notifications with pagination
    - Marking notifications as read
    - Marking all as read
    - Deleting notifications
    - Getting unread count
    """

    # [Fix]: Type-aware deduplication cache to prevent duplicate notifications
    # Different notification types have different appropriate deduplication windows
    # [From]: spec.md FR-031 - Deduplication within 5-minute window
    _dedup_cache: dict[str, datetime] = defaultdict(datetime.utcnow)

    # Deduplication windows by notification type (in minutes)
    _dedup_windows: dict[NotificationType, int] = {
        # Immediate notifications should have short deduplication
        NotificationType.TASK_DUE: 5,          # 5 minutes for task due reminders
        NotificationType.TASK_OVERDUE: 15,     # 15 minutes - allow more frequent overdue alerts
        NotificationType.TASK_ASSIGNED: 60,    # 1 hour - assignment shouldn't repeat
        NotificationType.TASK_COMPLETED: 1,    # 1 minute - completion is instant
        NotificationType.TASK_REMINDER: 30,    # 30 minutes for general reminders
        NotificationType.SYSTEM_UPDATE: 1440,  # 24 hours - system updates are rare
    }

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        data: dict,
        related_task_id: Optional[int] = None,
        sent_channels: Optional[list[str]] = None,
    ) -> NotificationPublic:
        """Create a new notification.

        [Task]: T012
        [From]: spec.md FR-004, FR-031

        Args:
            session: Database session
            user_id: User ID to create notification for
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data (task_id, etc.)
            related_task_id: Optional related task ID
            sent_channels: Channels notification was sent to

        Returns:
            Created notification as NotificationPublic
        """
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data,
            related_task_id=related_task_id,
            sent_channels=sent_channels or [],
        )

        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        # Trigger SSE event for real-time update
        await SSEService.broadcast_to_user(
            user_id,
            {
                "event": "notification_created",
                "data": NotificationPublic.model_validate(notification).model_dump(),
            },
        )

        return NotificationPublic.model_validate(notification)

    @staticmethod
    def _generate_dedup_key(user_id: str, type: NotificationType, data: dict) -> str:
        """Generate deduplication key for notification.

        [From]: spec.md FR-031 - Deduplication within 5-minute window

        Args:
            user_id: User ID
            type: Notification type
            data: Notification data

        Returns:
            Deduplication key string
        """
        # Create key from user_id, type, and relevant data fields
        relevant_data = {k: v for k, v in data.items() if k in ["task_id", "due_date"]}
        return f"{user_id}:{type.value}:{str(sorted(relevant_data.items()))}"

    @staticmethod
    async def should_deduplicate(
        user_id: str,
        type: NotificationType,
        data: dict,
    ) -> bool:
        """Check if notification should be deduplicated.

        [Fix]: Type-aware deduplication - different windows for different types
        [From]: spec.md FR-031 - Deduplication within 5-minute window

        Args:
            user_id: User ID
            type: Notification type
            data: Notification data

        Returns:
            True if notification should be skipped (duplicate), False otherwise
        """
        key = NotificationService._generate_dedup_key(user_id, type, data)
        last_sent = NotificationService._dedup_cache.get(key)

        if last_sent:
            # Get the deduplication window for this notification type
            dedup_window = NotificationService._dedup_windows.get(type, 5)
            # Check if within deduplication window
            if datetime.utcnow() - last_sent < timedelta(minutes=dedup_window):
                logger.debug(
                    f"Deduplicating {type.value} notification for user {user_id} "
                    f"(within {dedup_window} minute window)"
                )
                return True

        # Update cache
        NotificationService._dedup_cache[key] = datetime.utcnow()
        return False

    @staticmethod
    async def list_notifications(
        session: AsyncSession,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        unread_only: bool = False,
    ) -> NotificationList:
        """List notifications for a user with pagination.

        [Task]: T012
        [From]: spec.md FR-009, FR-001, contracts/api.yaml §1.1

        Args:
            session: Database session
            user_id: User ID to get notifications for
            limit: Items per page (max 100)
            offset: Pagination offset
            unread_only: Filter by unread status

        Returns:
            NotificationList with items, total, and unread_count
        """
        # Enforce max limit
        limit = min(limit, 100)

        # Build base query - exclude soft-deleted notifications
        statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.deleted_at == None,
        )

        if unread_only:
            statement = statement.where(Notification.read_status == False)

        # Get total count
        count_statement = select(sql_func.count()).select_from(
            statement.subquery()
        )
        total_result = await session.execute(count_statement)
        total = total_result.scalar() or 0

        # Get unread count
        unread_statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_status == False,
            Notification.deleted_at == None,
        )
        unread_count_statement = select(sql_func.count()).select_from(
            unread_statement.subquery()
        )
        unread_result = await session.execute(unread_count_statement)
        unread_count = unread_result.scalar() or 0

        # Apply pagination and ordering
        statement = statement.order_by(Notification.created_at.desc())
        statement = statement.limit(limit).offset(offset)

        # Execute query
        result = await session.execute(statement)
        notifications = result.scalars().all()

        items = [
            NotificationPublic.model_validate(n) for n in notifications
        ]

        return NotificationList(
            items=items,
            total=total,
            unread_count=unread_count,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    async def get_notification_or_404(
        session: AsyncSession,
        notification_id: int,
        user_id: str,
    ) -> Notification:
        """Get a notification by ID or raise 404.

        [From]: backend/CLAUDE.md - Return 404 not 403 for ownership checks

        Args:
            session: Database session
            notification_id: Notification ID
            user_id: User ID for ownership check

        Returns:
            Notification object

        Raises:
            ValueError: If notification not found or doesn't belong to user
        """
        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.deleted_at == None,
        )
        result = await session.execute(statement)
        notification = result.scalar_one_or_none()

        if not notification:
            raise ValueError(f"Notification not found")

        return notification

    @staticmethod
    async def mark_as_read(
        session: AsyncSession,
        notification_id: int,
        user_id: str,
    ) -> NotificationPublic:
        """Mark a notification as read.

        [Task]: T012
        [From]: spec.md FR-005, contracts/api.yaml §1.2

        Args:
            session: Database session
            notification_id: Notification ID to mark as read
            user_id: User ID for ownership check

        Returns:
            Updated notification as NotificationPublic
        """
        notification = await NotificationService.get_notification_or_404(
            session,
            notification_id,
            user_id,
        )

        notification.read_status = True
        await session.commit()
        await session.refresh(notification)

        # Trigger SSE event for real-time update
        await SSEService.broadcast_to_user(
            user_id,
            {
                "event": "notification_read",
                "data": {
                    "id": notification.id,
                    "read_status": True,
                },
            },
        )

        return NotificationPublic.model_validate(notification)

    @staticmethod
    async def mark_all_as_read(
        session: AsyncSession,
        user_id: str,
    ) -> int:
        """Mark all notifications as read for a user.

        [Task]: T012
        [From]: spec.md FR-008, FR-006, contracts/api.yaml §1.3

        Args:
            session: Database session
            user_id: User ID to mark all as read for

        Returns:
            Number of notifications marked as read
        """
        statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_status == False,
            Notification.deleted_at == None,
        )
        result = await session.execute(statement)
        notifications = result.scalars().all()

        updated_count = 0
        for notification in notifications:
            notification.read_status = True
            updated_count += 1

        await session.commit()

        # Trigger SSE event for real-time update
        await SSEService.broadcast_to_user(
            user_id,
            {
                "event": "notification_read_count",
                "data": {"unread_count": 0},
            },
        )

        return updated_count

    @staticmethod
    async def delete_notification(
        session: AsyncSession,
        notification_id: int,
        user_id: str,
    ) -> None:
        """Soft delete a notification.

        [Task]: T012
        [From]: spec.md FR-006, FR-035, contracts/api.yaml §1.4

        Uses soft delete (sets deleted_at) for 30-day archive per spec.

        Args:
            session: Database session
            notification_id: Notification ID to delete
            user_id: User ID for ownership check
        """
        notification = await NotificationService.get_notification_or_404(
            session,
            notification_id,
            user_id,
        )

        # Soft delete - set deleted_at timestamp
        notification.deleted_at = datetime.utcnow()
        await session.commit()

    @staticmethod
    async def get_unread_count(
        session: AsyncSession,
        user_id: str,
    ) -> int:
        """Get unread notification count for a user.

        [From]: spec.md FR-001, SC-005

        Args:
            session: Database session
            user_id: User ID to get count for

        Returns:
            Number of unread notifications
        """
        statement = select(sql_func.count()).select_from(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.read_status == False,
                Notification.deleted_at == None,
            ).subquery()
        )
        result = await session.execute(statement)
        return result.scalar() or 0

    @staticmethod
    async def get_user_preferences(
        session: AsyncSession,
        user_id: str,
    ) -> dict[NotificationType, NotificationPreference]:
        """Get all notification preferences for a user.

        [From]: spec.md FR-032, FR-033
        [Fix]: Persist default preferences for existing users

        Args:
            session: Database session
            user_id: User ID to get preferences for

        Returns:
            Dict mapping notification types to their preferences
        """
        statement = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        result = await session.execute(statement)
        preferences = result.scalars().all()

        pref_dict = {}
        for pref in preferences:
            pref_dict[pref.notification_type] = pref

        # [Fix]: Create and persist default preferences for any missing types
        # This ensures existing users get proper default preferences
        needs_commit = False
        for notif_type in NotificationType:
            if notif_type not in pref_dict:
                # Define default preferences based on notification type
                if notif_type == NotificationType.SYSTEM_UPDATE:
                    # System updates - in-app only by default
                    default_pref = NotificationPreference(
                        user_id=user_id,
                        notification_type=notif_type,
                        in_app_enabled=True,
                        push_enabled=False,
                        email_enabled=False,
                        frequency=EmailFrequency.NONE,
                    )
                else:
                    # Task-related events - email enabled by default
                    default_pref = NotificationPreference(
                        user_id=user_id,
                        notification_type=notif_type,
                        in_app_enabled=True,
                        push_enabled=(notif_type == NotificationType.TASK_OVERDUE),
                        email_enabled=True,
                        frequency=EmailFrequency.IMMEDIATE,
                    )
                session.add(default_pref)
                pref_dict[notif_type] = default_pref
                needs_commit = True

        if needs_commit:
            await session.commit()

        return pref_dict

    @staticmethod
    async def can_send_notification(
        session: AsyncSession,
        user_id: str,
        notification_type: NotificationType,
        channel: str,
    ) -> tuple[bool, Optional[str]]:
        """Check if notification can be sent based on user preferences.

        [From]: spec.md FR-032, FR-036

        Args:
            session: Database session
            user_id: User ID to check preferences for
            notification_type: Type of notification
            channel: Channel to check (in_app, push, email)

        Returns:
            Tuple of (can_send, reason)
        """
        preferences = await NotificationService.get_user_preferences(
            session,
            user_id,
        )

        pref = preferences.get(notification_type)

        if not pref:
            # No preference set, use defaults
            if channel == "in_app":
                return True, None
            return False, "No preference set for this notification type"

        # Check channel enablement
        if channel == "in_app" and not pref.in_app_enabled:
            return False, "In-app notifications disabled"
        if channel == "push" and not pref.push_enabled:
            return False, "Push notifications disabled"
        if channel == "email" and not pref.email_enabled:
            return False, "Email notifications disabled"

        # Check Do Not Disturb hours
        # DND only applies to non-urgent notifications
        urgent_types = [NotificationType.TASK_OVERDUE, NotificationType.TASK_DUE]
        is_urgent = notification_type in urgent_types

        if not is_urgent and pref.dnd_start and pref.dnd_end:
            # Parse DND times (format: "HH:MM")
            try:
                start_hour, start_minute = map(int, pref.dnd_start.split(":"))
                end_hour, end_minute = map(int, pref.dnd_end.split(":"))

                # Get current time
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute

                # Convert to minutes since midnight for easier comparison
                current_minutes = current_hour * 60 + current_minute
                start_minutes = start_hour * 60 + start_minute
                end_minutes = end_hour * 60 + end_minute

                # Check if current time is within DND window
                in_dnd = False

                if start_minutes > end_minutes:
                    # DND spans midnight (e.g., 22:00 to 08:00)
                    # Active when current >= start OR current < end
                    if current_minutes >= start_minutes or current_minutes < end_minutes:
                        in_dnd = True
                else:
                    # Normal same-day period (e.g., 13:00 to 17:00)
                    # Active when start <= current < end
                    if start_minutes <= current_minutes < end_minutes:
                        in_dnd = True

                if in_dnd:
                    return False, "Do Not Disturb hours active"

            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid DND time format: {e}")
                # Continue with notification if DND times are invalid

        return True, None

    @staticmethod
    async def update_preferences(
        session: AsyncSession,
        user_id: str,
        preferences: list[dict],
    ) -> dict[str, NotificationPreference]:
        """Update email notification preferences for a user.

        [From]: spec.md FR-026

        Args:
            session: Database session
            user_id: User ID to update preferences for
            preferences: List of preference dicts with keys:
                - notification_type: str (e.g., "task_due", "system_update")
                - enabled: bool (maps to email_enabled)
                - frequency: str ("immediate", "daily", "weekly", "none")

        Returns:
            Dict mapping notification types to their updated preferences
        """
        from app.models.notification import EmailFrequency

        updated_prefs: dict[str, NotificationPreference] = {}

        for pref_data in preferences:
            # Parse the notification type from string
            notif_type_str = pref_data.get("notification_type")
            if not notif_type_str:
                continue

            # Convert string to NotificationType enum
            try:
                notif_type = NotificationType(notif_type_str)
            except ValueError:
                logger.warning(f"Unknown notification type: {notif_type_str}")
                continue

            # Get or create preference
            statement = select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notif_type,
            )
            result = await session.execute(statement)
            pref = result.scalar_one_or_none()

            # Map frontend's `enabled` to backend's `email_enabled`
            email_enabled = pref_data.get("enabled", True)
            frequency_str = pref_data.get("frequency", "immediate")

            # Convert frequency string to EmailFrequency enum
            try:
                frequency = EmailFrequency(frequency_str)
            except ValueError:
                frequency = EmailFrequency.IMMEDIATE

            if pref:
                # Update existing preference
                pref.email_enabled = email_enabled
                pref.frequency = frequency
                pref.updated_at = datetime.utcnow()
            else:
                # Create new preference with defaults
                pref = NotificationPreference(
                    user_id=user_id,
                    notification_type=notif_type,
                    in_app_enabled=True,  # Default: in-app always on
                    push_enabled=False,   # Default: push opt-in
                    email_enabled=email_enabled,
                    frequency=frequency,
                )
                session.add(pref)

            updated_prefs[notif_type.value] = pref

        # Commit all changes
        await session.commit()

        # Refresh all preferences to get DB-generated values
        for pref in updated_prefs.values():
            await session.refresh(pref)

        return updated_prefs

    @staticmethod
    async def update_settings(
        session: AsyncSession,
        user_id: str,
        settings: dict,
    ) -> dict:
        """Update notification settings for a user.

        [From]: spec.md FR-033
        [From]: contracts/api.yaml §4.2 Update Notification Settings

        Args:
            session: Database session
            user_id: User ID to update settings for
            settings: Settings dict with keys:
                - types: Dict mapping notification types to channel settings
                - do_not_disturb: Dict with enabled, start, end

        Returns:
            Dict with updated: true and message
        """
        types_settings = settings.get("types", {})
        dnd_settings = settings.get("do_not_disturb", {})

        # Get all existing preferences for this user
        statement = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        result = await session.execute(statement)
        existing_prefs = {p.notification_type: p for p in result.scalars().all()}

        # Get all notification types
        all_types = list(NotificationType)

        # Extract DND settings
        dnd_enabled = dnd_settings.get("enabled", False)
        dnd_start = dnd_settings.get("start") if dnd_enabled else None
        dnd_end = dnd_settings.get("end") if dnd_enabled else None

        # Validate DND time format
        if dnd_start and dnd_end:
            try:
                # Validate HH:MM format
                h1, m1 = map(int, dnd_start.split(":"))
                h2, m2 = map(int, dnd_end.split(":"))
                if not (0 <= h1 <= 23 and 0 <= m1 <= 59 and 0 <= h2 <= 23 and 0 <= m2 <= 59):
                    raise ValueError("Invalid time")
            except (ValueError, AttributeError):
                return {"updated": False, "message": "Invalid DND time format. Use HH:MM"}

        # Update each notification type's preferences
        for notif_type in all_types:
            notif_type_str = notif_type.value
            type_settings = types_settings.get(notif_type_str, {})

            # Get or create preference
            pref = existing_prefs.get(notif_type)

            # Extract settings from the type_settings
            # Frontend sends: {"in_app": bool, "push": bool, "email": str}
            in_app_enabled = type_settings.get("in_app", True)
            push_enabled = type_settings.get("push", False)
            email_freq_str = type_settings.get("email", "none")

            # Parse email frequency - "none" means email disabled
            email_enabled = email_freq_str != "none"
            try:
                frequency = EmailFrequency(email_freq_str) if email_enabled else EmailFrequency.NONE
            except ValueError:
                frequency = EmailFrequency.IMMEDIATE if email_enabled else EmailFrequency.NONE

            if pref:
                # Update existing preference
                pref.in_app_enabled = in_app_enabled
                pref.push_enabled = push_enabled
                pref.email_enabled = email_enabled
                pref.frequency = frequency
                pref.dnd_start = dnd_start
                pref.dnd_end = dnd_end
                pref.updated_at = datetime.utcnow()
            else:
                # Create new preference
                pref = NotificationPreference(
                    user_id=user_id,
                    notification_type=notif_type,
                    in_app_enabled=in_app_enabled,
                    push_enabled=push_enabled,
                    email_enabled=email_enabled,
                    frequency=frequency,
                    dnd_start=dnd_start,
                    dnd_end=dnd_end,
                )
                session.add(pref)

        # Commit all changes
        await session.commit()

        return {"updated": True, "message": "Settings updated successfully"}

    @staticmethod
    async def create_notification(
        session: AsyncSession,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        data: dict,
        related_task_id: Optional[int] = None,
        sent_channels: Optional[list[str]] = None,
    ) -> NotificationPublic:
        """Create a new notification with deduplication check.

        [Task]: T051-T063
        [From]: spec.md FR-031 - Deduplication within 5-minute window

        This method checks for duplicates before creating a notification.
        Use this for all task event notifications.

        Args:
            session: Database session
            user_id: User ID to create notification for
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data (task_id, etc.)
            related_task_id: Optional related task ID
            sent_channels: Channels notification was sent to

        Returns:
            Created notification as NotificationPublic, or None if deduplicated
        """
        # Check for deduplication
        if await NotificationService.should_deduplicate(user_id, type, data):
            logger.info(f"Deduplicating notification: {type.value} for user {user_id}")
            # Return existing notification or None
            return None  # Signal that notification was deduplicated

        # Create the notification
        return await NotificationService.create(
            session=session,
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data,
            related_task_id=related_task_id,
            sent_channels=sent_channels or [],
        )

    @staticmethod
    async def dispatch(
        session: AsyncSession,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        data: dict,
        related_task_id: Optional[int] = None,
    ) -> Optional[NotificationPublic]:
        """Create and dispatch a notification to all enabled channels.

        [From]: spec.md FR-005 - Multi-channel notifications

        This method:
        1. Creates the in-app notification record
        2. Sends via SSE for real-time in-app updates
        3. Sends email if email is enabled for this notification type
        4. Sends push notification if push is enabled for this notification type

        Args:
            session: Database session
            user_id: User ID to create notification for
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data (task_id, etc.)
            related_task_id: Optional related task ID

        Returns:
            Created notification as NotificationPublic, or None if deduplicated
        """
        # Get user preferences
        preferences = await NotificationService.get_user_preferences(session, user_id)
        pref = preferences.get(type)

        # Default preferences if not set
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=type,
                in_app_enabled=True,
                push_enabled=False,
                email_enabled=False,
            )

        # Track which channels we're sending to
        sent_channels = ["in_app"]  # Always create in-app notification

        # Check if we can send email
        can_send_email, email_reason = await NotificationService.can_send_notification(
            session, user_id, type, "email"
        )

        # Send email if enabled and allowed
        if pref.email_enabled and can_send_email:
            try:
                # Import here to avoid circular dependency
                from app.services.email_service import EmailService
                from app.services.unsubscribe_service import UnsubscribeService

                unsubscribe_token = UnsubscribeService.generate_unsubscribe_token(user_id)

                # Get user's email
                from app.models import User
                user_result = await session.execute(select(User.email).where(User.id == user_id))
                user_email = user_result.scalar_one_or_none()

                if user_email:
                    # Generate email content based on notification type
                    from app.services.email_service import EmailTemplates
                    email_html = EmailTemplates.base_template(
                        f"""<div style="padding: 20px 0;">
                            <h2 style="color: #5eead4; margin-bottom: 12px;">{title}</h2>
                            <p style="color: #a1a1aa; line-height: 1.6;">{message}</p>
                        </div>""",
                        preview_text=title,
                        unsubscribe_token=unsubscribe_token,
                    )

                    # Create notification record first to get ID
                    notification = Notification(
                        user_id=user_id,
                        type=type,
                        title=title,
                        message=message,
                        data=data,
                        related_task_id=related_task_id,
                        sent_channels=[],  # Will update after sending
                    )
                    session.add(notification)
                    await session.commit()
                    await session.refresh(notification)

                    # Send email
                    await EmailService.send_email(
                        session=session,
                        notification_id=notification.id,
                        to=user_email,
                        subject=title,
                        html=email_html,
                    )
                    sent_channels.append("email")
                    logger.info(f"Email sent for notification {notification.id} (type: {type.value})")
            except Exception as e:
                logger.exception(f"Failed to send email notification: {e}")

        # Check if we can send push
        can_send_push, push_reason = await NotificationService.can_send_notification(
            session, user_id, type, "push"
        )

        # Send push if enabled and allowed
        if pref.push_enabled and can_send_push:
            try:
                from app.services.push_service import PushService

                result = await PushService.send_push(
                    session=session,
                    user_id=user_id,
                    title=title,
                    body=message,
                    icon="/icon.png",
                    data=data or {},
                    notification_type=type,
                )
                if result.get("success"):
                    sent_channels.append("push")
                    logger.info(f"Push sent for notification type: {type.value}")
            except Exception as e:
                logger.exception(f"Failed to send push notification: {e}")

        # If email was sent, we already created the notification record
        # Otherwise, create it now
        if "email" not in sent_channels:
            return await NotificationService.create(
                session=session,
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data,
                related_task_id=related_task_id,
                sent_channels=sent_channels,
            )
        else:
            # Update sent_channels for the notification we created
            from sqlalchemy import update
            await session.execute(
                update(Notification)
                .where(Notification.id == notification.id)
                .values(sent_channels=sent_channels)
            )
            await session.commit()
            return NotificationPublic.model_validate(notification)
