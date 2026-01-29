"""PushService for browser push notifications via Web Push Protocol.

[Task]: T027
[From]: spec.md FR-018-FR-023, research.md Web Push section
[From]: pywebpush library documentation

[Fix]: Concurrent push sends with asyncio.gather for improved performance
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional

from pywebpush import WebPushException, webpush
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.push_subscription import (
    PushSubscription,
    PushSubscriptionCreate,
    PushSubscriptionPublic,
)
from app.models.notification import NotificationType

logger = logging.getLogger(__name__)


class PushService:
    """Service for browser push notifications.

    [Task]: T027
    [From]: spec.md FR-018-FR-023

    Handles:
    - Subscribing to push notifications
    - Unsubscribing from push notifications
    - Sending push notifications
    - Rate limiting (max 3/hour, exempt urgent)
    - Subscription cleanup on 410/404 errors
    """

    # Rate limiting: max 3 push notifications per hour per user
    # [From]: spec.md FR-022 - Rate limiting
    _rate_limit_max = 3
    _rate_limit_window = timedelta(hours=1)
    _rate_limit_tracker: dict[str, list[datetime]] = defaultdict(list)

    @staticmethod
    def _clean_old_rate_entries(user_id: str, now: datetime) -> None:
        """Remove rate limit entries older than the window."""
        cutoff = now - PushService._rate_limit_window
        PushService._rate_limit_tracker[user_id] = [
            ts for ts in PushService._rate_limit_tracker[user_id] if ts > cutoff
        ]

    @staticmethod
    def _check_rate_limit(user_id: str, notification_type: NotificationType) -> bool:
        """Check if user is within rate limit.

        [Task]: T029
        [From]: spec.md FR-022 - Max 3 push/hour, exempt urgent

        Urgent notifications (task_overdue, task_due within 1 hour) are exempt.
        """
        # Urgent notifications are exempt from rate limiting
        if notification_type in (NotificationType.TASK_OVERDUE, NotificationType.TASK_DUE):
            return True

        now = datetime.utcnow()
        PushService._clean_old_rate_entries(user_id, now)

        recent_count = len(PushService._rate_limit_tracker[user_id])
        if recent_count >= PushService._rate_limit_max:
            logger.warning(f"Rate limit exceeded for user {user_id}: {recent_count}/hour")
            return False

        PushService._rate_limit_tracker[user_id].append(now)
        return True

    @staticmethod
    async def subscribe(
        session: AsyncSession,
        user_id: str,
        subscription_data: PushSubscriptionCreate,
    ) -> PushSubscriptionPublic:
        """Subscribe to push notifications.

        [Task]: T027
        [From]: spec.md FR-018 - Subscribe to push notifications

        Stores the PushSubscription from the browser's PushManager.
        Handles multiple devices by storing each subscription separately.

        Args:
            session: Database session
            user_id: User ID to subscribe
            subscription_data: Subscription from browser

        Returns:
            Created subscription as PushSubscriptionPublic
        """
        # Check if subscription already exists for this user+endpoint
        endpoint = subscription_data.subscription.get("endpoint", "")
        existing = await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.subscription["endpoint"].astext == endpoint,
            )
        )
        existing_sub = existing.scalar_one_or_none()

        if existing_sub:
            # Update existing subscription
            existing_sub.subscription = subscription_data.subscription
            existing_sub.device_info = subscription_data.device_info
            existing_sub.last_used_at = datetime.utcnow()
            existing_sub.is_valid = True
        else:
            # Create new subscription
            new_sub = PushSubscription(
                user_id=user_id,
                subscription=subscription_data.subscription,
                device_info=subscription_data.device_info,
                created_at=datetime.utcnow(),
                last_used_at=datetime.utcnow(),
                is_valid=True,
            )
            session.add(new_sub)

        await session.commit()

        # Get the subscription to return
        if existing_sub:
            return PushSubscriptionPublic(
                id=existing_sub.id,
                user_id=existing_sub.user_id,
                device_info=existing_sub.device_info,
                created_at=existing_sub.created_at,
                last_used_at=existing_sub.last_used_at,
                is_valid=existing_sub.is_valid,
            )

        # Re-fetch for new subscription
        result = await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.subscription["endpoint"].astext == endpoint,
            )
        )
        sub = result.scalar_one()
        return PushSubscriptionPublic(
            id=sub.id,
            user_id=sub.user_id,
            device_info=sub.device_info,
            created_at=sub.created_at,
            last_used_at=sub.last_used_at,
            is_valid=sub.is_valid,
        )

    @staticmethod
    async def unsubscribe(
        session: AsyncSession,
        user_id: str,
        subscription_id: Optional[int] = None,
    ) -> bool:
        """Unsubscribe from push notifications.

        [Task]: T027
        [From]: spec.md FR-019 - Unsubscribe from push notifications

        Args:
            session: Database session
            user_id: User ID to unsubscribe
            subscription_id: Specific subscription to remove, or all if None

        Returns:
            True if subscription(s) were removed
        """
        if subscription_id:
            # Delete specific subscription (only if owned by user)
            stmt = delete(PushSubscription).where(
                PushSubscription.id == subscription_id,
                PushSubscription.user_id == user_id,
            )
            result = await session.execute(stmt)
        else:
            # Delete all subscriptions for user
            stmt = delete(PushSubscription).where(
                PushSubscription.user_id == user_id,
            )
            result = await session.execute(stmt)

        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def is_subscribed(session: AsyncSession, user_id: str) -> bool:
        """Check if user has any valid push subscriptions.

        [Task]: T027
        [From]: spec.md FR-020 - Check push subscription status

        Args:
            session: Database session
            user_id: User ID to check

        Returns:
            True if user has at least one valid subscription

        [Fix]: Use .scalars().first() instead of scalar_one_or_none() to handle
        multiple subscriptions gracefully (user may have multiple devices).
        """
        result = await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.is_valid == True,
            )
        )
        # Use .scalars().first() to handle multiple subscriptions gracefully
        # Returns first valid subscription or None, without throwing on multiple rows
        return result.scalars().first() is not None

    @staticmethod
    async def send_push(
        session: AsyncSession,
        user_id: str,
        title: str,
        body: str,
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
        notification_type: NotificationType = NotificationType.SYSTEM_UPDATE,
    ) -> dict[str, Any]:
        """Send push notification to all valid subscriptions for a user.

        [Task]: T027
        [From]: spec.md FR-021 - Send push notification
        [Fix]: Uses asyncio.gather for concurrent sends to multiple devices

        Args:
            session: Database session
            user_id: User ID to send notification to
            title: Notification title
            body: Notification body
            icon: Optional icon URL
            badge: Optional badge URL
            data: Optional data payload
            notification_type: Type for rate limiting exemption

        Returns:
            Dict with success status and details
        """
        # Check rate limit
        if not PushService._check_rate_limit(user_id, notification_type):
            return {
                "success": False,
                "error": "rate_limit_exceeded",
                "message": "Maximum 3 push notifications per hour",
            }

        # Get all valid subscriptions for user
        result = await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.is_valid == True,
            )
        )
        subscriptions = result.scalars().all()

        if not subscriptions:
            return {
                "success": False,
                "error": "no_subscription",
                "message": "No valid push subscriptions found",
            }

        # Prepare payload
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": icon or "/icon.png",
            "badge": badge or "/badge.png",
            "data": data or {},
        })

        # VAPID keys from environment
        import os

        vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", "")
        vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", "")
        vapid_subject = os.getenv("VAPID_SUBJECT", "mailto:admin@chronostodo.com")

        if not vapid_public_key or not vapid_private_key:
            logger.error("VAPID keys not configured")
            return {
                "success": False,
                "error": "config_error",
                "message": "Push notifications not configured",
            }

        # [Fix]: Send to all subscriptions concurrently using asyncio.gather
        # This is much faster than serial sends when a user has multiple devices
        async def send_to_subscription(sub: PushSubscription) -> dict[str, Any]:
            """Send push to a single subscription.

            Returns dict with success status and subscription info.
            """
            try:
                # Run webpush in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: webpush(
                        subscription_info=sub.subscription,
                        data=payload,
                        vapid_private_key=vapid_private_key,
                        vapid_claims={"sub": vapid_subject},
                        timeout=5,
                    )
                )
                # Update last_used_at
                sub.last_used_at = datetime.utcnow()
                return {
                    "subscription_id": sub.id,
                    "success": True,
                }
            except WebPushException as e:
                logger.warning(f"Push failed for subscription {sub.id}: {e}")
                # Mark invalid on 410/404
                if e.response and e.response.status_code in (410, 404):
                    sub.is_valid = False
                return {
                    "subscription_id": sub.id,
                    "success": False,
                    "error": str(e),
                    "should_invalidate": e.response and e.response.status_code in (410, 404),
                }
            except Exception as e:
                logger.exception(f"Unexpected error sending push to subscription {sub.id}: {e}")
                sub.is_valid = False
                return {
                    "subscription_id": sub.id,
                    "success": False,
                    "error": str(e),
                    "should_invalidate": True,
                }

        # Send to all subscriptions concurrently
        results = await asyncio.gather(
            *[send_to_subscription(sub) for sub in subscriptions],
            return_exceptions=True,
        )

        # Process results
        success_count = 0
        failed_subscriptions = []
        last_error = None

        for result in results:
            if isinstance(result, Exception):
                logger.exception(f"Unexpected exception in push send: {result}")
                last_error = str(result)
                continue

            if result.get("success"):
                success_count += 1
            else:
                failed_subscriptions.append(result["subscription_id"])
                last_error = result.get("error", last_error)

        await session.commit()

        # If all failed and we have an error message, include it
        if success_count == 0 and last_error:
            return {
                "success": False,
                "sent": 0,
                "total": len(subscriptions),
                "failed_subscriptions": failed_subscriptions,
                "error": "send_failed",
                "message": f"Failed to send: {last_error}",
            }

        return {
            "success": success_count > 0,
            "sent": success_count,
            "total": len(subscriptions),
            "failed_subscriptions": failed_subscriptions,
        }

    @staticmethod
    async def cleanup_user_subscriptions(session: AsyncSession, user_id: str, keep_endpoint: str | None = None) -> int:
        """Clean up old/stale subscriptions for a specific user.

        [Fix]: Removes stale subscriptions for a user, keeping only the active one.
        This prevents accumulation of stale subscriptions from multiple devices/browsers.

        Args:
            session: Database session
            user_id: User ID to clean up subscriptions for
            keep_endpoint: If provided, keep subscriptions with this endpoint

        Returns:
            Number of subscriptions removed
        """
        from sqlalchemy import and_

        # Build the where clause
        where_conditions = [PushSubscription.user_id == user_id]

        if keep_endpoint:
            # Keep the subscription with the matching endpoint, delete others
            where_conditions.append(
                PushSubscription.subscription["endpoint"].astext != keep_endpoint
            )

        stmt = delete(PushSubscription).where(and_(*where_conditions))
        result = await session.execute(stmt)
        await session.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} stale push subscriptions for user {user_id}")

        return count

    @staticmethod
    async def cleanup_invalid_subscriptions(session: AsyncSession) -> int:
        """Clean up invalid subscriptions (410/404 errors).

        [Task]: T030
        [From]: spec.md FR-023 - Subscription cleanup

        This can be run periodically to remove stale subscriptions.

        Args:
            session: Database session

        Returns:
            Number of subscriptions removed
        """
        # Delete subscriptions marked as invalid
        stmt = delete(PushSubscription).where(PushSubscription.is_valid == False)
        result = await session.execute(stmt)
        await session.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} invalid push subscriptions")

        return count
