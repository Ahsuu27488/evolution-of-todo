"""Notification API routes.

[Task]: T014-T016, T028, T041
[From]: spec.md FR-001, FR-005, FR-008, FR-009, FR-011, FR-018-FR-023, FR-025
[From]: contracts/api.yaml §1 - In-App Notifications API, §2 - Push Notifications API, §3 - Email Webhooks
[From]: Context7 /fastapi-guide for route patterns

[Fix]: Added test email deduplication and rate limiting
"""

import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.sql import and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.models.notification import (
    NotificationList,
    NotificationPreferenceCreate,
    NotificationPreferencePublic,
    NotificationPublic,
    NotificationType,
)
from app.models.push_subscription import PushSubscriptionCreate, PushSubscriptionPublic
from app.models.email_delivery_log import EmailDeliveryLog, EmailDeliveryStatus
from app.services.notification_service import NotificationService
from app.services.push_service import PushService
from app.services.sse_service import SSEService
from app.services.email_service import EmailService, EmailTemplates
from app.simple_auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# =============================================================================
# Rate Limiting for Test Emails
# =============================================================================

# Track last test email sent per user to prevent rapid duplicate sends
# [Fix]: Prevent duplicate test emails from multiple rapid clicks
_test_email_last_sent: dict[str, datetime] = {}
_test_email_lock: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
TEST_EMAIL_COOLDOWN_SECONDS = 30  # Minimum 30 seconds between test emails


# =============================================================================
# Notification CRUD Endpoints
# =============================================================================


@router.get("", response_model=NotificationList)
async def list_notifications(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    unread_only: bool = Query(False, description="Filter by unread status"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> NotificationList:
    """List notifications for the current user.

    [Task]: T014
    [From]: spec.md FR-001, FR-009
    [From]: contracts/api.yaml §1.1 List Notifications

    Returns paginated list of notifications with unread count.

    Args:
        request: FastAPI Request
        limit: Items per page (max 100)
        offset: Pagination offset
        unread_only: Filter by unread status
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        NotificationList with items, total, and unread_count
    """
    try:
        return await NotificationService.list_notifications(
            session,
            user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )
    except Exception as e:
        logger.exception(f"Error listing notifications for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read", response_model=NotificationPublic)
async def mark_notification_as_read(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> NotificationPublic:
    """Mark a notification as read.

    [Task]: T014
    [From]: spec.md FR-005
    [From]: contracts/api.yaml §1.2 Mark Notification as Read

    Args:
        notification_id: Notification ID to mark as read
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Updated notification

    Raises:
        404: If notification not found
    """
    try:
        return await NotificationService.mark_as_read(
            session,
            notification_id,
            user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error marking notification {notification_id} as read")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read", response_model=dict[str, int])
async def mark_all_notifications_as_read(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict[str, int]:
    """Mark all notifications as read for the current user.

    [Task]: T014
    [From]: spec.md FR-008
    [From]: contracts/api.yaml §1.3 Mark All as Read

    Args:
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with updated_count
    """
    try:
        updated_count = await NotificationService.mark_all_as_read(session, user_id)
        return {"updated_count": updated_count}
    except Exception as e:
        logger.exception(f"Error marking all notifications as read for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Delete (soft-delete) a notification.

    [Task]: T014
    [From]: spec.md FR-006, FR-035
    [From]: contracts/api.yaml §1.4 Delete Notification

    Uses soft delete - notification is archived after 30 days per spec.

    Args:
        notification_id: Notification ID to delete
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        {"deleted": true}
    """
    try:
        await NotificationService.delete_notification(
            session,
            notification_id,
            user_id,
        )
        return {"deleted": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error deleting notification {notification_id}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SSE Streaming Endpoint
# =============================================================================


@router.get("/stream")
async def notification_stream(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Server-Sent Events stream for real-time notifications.

    [Task]: T015
    [From]: spec.md SC-001, SC-005
    [From]: contracts/api.yaml §1.5 Notification Stream (SSE)
    [From]: Context7 /sysid/sse-starlette

    Provides real-time updates for:
    - New notifications
    - Read status changes
    - Unread count updates

    Args:
        request: FastAPI Request for disconnect detection
        user_id: Current user ID from JWT

    Returns:
        EventSourceResponse for SSE streaming
    """
    return await SSEService.event_stream(user_id, request)


# =============================================================================
# Notification Settings Endpoints
# =============================================================================


@router.get("/settings", response_model=dict)
async def get_notification_settings(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get notification settings for the current user.

    [Task]: T016
    [From]: spec.md FR-033
    [From]: contracts/api.yaml §4.1 Get Notification Settings

    Returns channel settings, type settings, and DND configuration.

    Args:
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with channels, types, and do_not_disturb settings
    """
    try:
        preferences = await NotificationService.get_user_preferences(session, user_id)

        # Get user email from users table
        from app.models import User
        user_result = await session.execute(
            select(User.email).where(User.id == user_id)
        )
        user_email = user_result.scalar_one_or_none()

        # Check if user has valid push subscriptions
        from app.models.push_subscription import PushSubscription
        push_result = await session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.is_valid == True,
            )
        )
        has_push = push_result.scalar_one_or_none() is not None

        # Build response per contract
        channels = {
            "in_app": {"enabled": True},  # Always enabled
            "push": {"enabled": has_push, "status": "granted" if has_push else "not_requested"},
            "email": {"enabled": bool(user_email), "address": user_email},
        }

        types = {}
        for notif_type, pref in preferences.items():
            types[notif_type.value] = {
                "in_app": pref.in_app_enabled,
                "push": pref.push_enabled,
                "email": pref.frequency.value if pref.email_enabled else "none",
            }

        # Get first preference for DND (assumed same for all types)
        first_pref = next(iter(preferences.values()), None)
        dnd = {
            "enabled": bool(first_pref and first_pref.dnd_start),
            "start": first_pref.dnd_start if first_pref else "22:00",
            "end": first_pref.dnd_end if first_pref else "08:00",
        }

        return {
            "channels": channels,
            "types": types,
            "do_not_disturb": dnd,
        }
    except Exception as e:
        logger.exception(f"Error getting notification settings for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings", response_model=dict)
async def update_notification_settings(
    settings: dict,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Update notification settings for the current user.

    [Task]: T016
    [From]: spec.md FR-033
    [From]: contracts/api.yaml §4.2 Update Notification Settings

    Args:
        settings: Settings update payload with keys:
            - types: Dict mapping notification types to channel settings
            - do_not_disturb: Dict with enabled, start, end
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with updated status and message

    Example payload:
    {
        "types": {
            "task_due": {"in_app": true, "push": false, "email": "immediate"},
            "task_overdue": {"in_app": true, "push": true, "email": "immediate"}
        },
        "do_not_disturb": {"enabled": true, "start": "22:00", "end": "08:00"}
    }
    """
    try:
        result = await NotificationService.update_settings(
            session=session,
            user_id=user_id,
            settings=settings,
        )
        return result
    except Exception as e:
        logger.exception(f"Error updating notification settings for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Email Preferences Endpoints
# =============================================================================


@router.get("/email/preferences")
async def get_email_preferences(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get email notification preferences.

    [Task]: T016
    [From]: spec.md FR-026, FR-033
    [From]: contracts/api.yaml §3.1 Get Email Preferences

    Args:
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Email preferences with per-type settings
    """
    preferences = await NotificationService.get_user_preferences(session, user_id)

    preferences_list = []
    for notif_type, pref in preferences.items():
        preferences_list.append({
            "notification_type": notif_type.value,
            "enabled": pref.email_enabled,
            "frequency": pref.frequency.value,
        })

    # Get user email from users table
    user_result = await session.execute(select(User.email).where(User.id == user_id))
    email_address = user_result.scalar_one_or_none()

    # Check for bounced emails - look for recent failed deliveries
    # Note: EmailDeliveryLog uses email address (not user_id) to track deliveries
    bounced = False
    if email_address:
        from datetime import timedelta
        bounce_cutoff = datetime.utcnow() - timedelta(days=7)
        bounced_result = await session.execute(
            select(EmailDeliveryLog)
            .where(
                and_(
                    EmailDeliveryLog.email == email_address,
                    EmailDeliveryLog.status == EmailDeliveryStatus.BOUNCED,
                    EmailDeliveryLog.sent_at >= bounce_cutoff
                )
            )
            .order_by(EmailDeliveryLog.sent_at.desc())
            .limit(1)
        )
        bounced_log = bounced_result.scalar_one_or_none()
        bounced = bounced_log is not None

    return {
        "preferences": preferences_list,
        "email_address": email_address,
        "bounced": bounced,
    }


@router.put("/email/preferences")
async def update_email_preferences(
    data: dict,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Update email notification preferences.

    [Task]: T016
    [From]: spec.md FR-026
    [From]: contracts/api.yaml §3.2 Update Email Preferences

    Args:
        data: Preferences update payload with "preferences" array
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with updated: true
    """
    preferences = data.get("preferences", [])
    if not preferences:
        raise HTTPException(
            status_code=422,
            detail="preferences array is required",
        )

    # Update preferences in database
    await NotificationService.update_preferences(
        session=session,
        user_id=user_id,
        preferences=preferences,
    )

    return {"updated": True}


# =============================================================================
# Push Notification Endpoints
# =============================================================================


@router.post("/push/subscribe", response_model=PushSubscriptionPublic)
async def subscribe_push(
    subscription_data: PushSubscriptionCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> PushSubscriptionPublic:
    """Subscribe to browser push notifications.

    [Task]: T028
    [From]: spec.md FR-018 - Subscribe to push notifications
    [From]: contracts/api.yaml §2.1 Subscribe to Push

    Stores the PushSubscription JSON from the browser's PushManager.
    Supports multiple devices per user.

    [Fix]: Cleans up stale subscriptions before adding new one to prevent
    accumulation of old subscriptions from previous sessions.

    Args:
        subscription_data: Subscription data from browser
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Created/updated subscription
    """
    try:
        # Clean up stale subscriptions before adding new one
        endpoint = subscription_data.subscription.get("endpoint", "")
        await PushService.cleanup_user_subscriptions(session, user_id, keep_endpoint=endpoint)

        return await PushService.subscribe(
            session,
            user_id,
            subscription_data,
        )
    except Exception as e:
        logger.exception(f"Error subscribing user {user_id} to push")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/push/unsubscribe")
async def unsubscribe_push(
    subscription_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Unsubscribe from browser push notifications.

    [Task]: T028
    [From]: spec.md FR-019 - Unsubscribe from push notifications
    [From]: contracts/api.yaml §2.2 Unsubscribe from Push

    Args:
        subscription_id: Specific subscription to remove, or all if None
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with unsubscribed: true/false
    """
    try:
        success = await PushService.unsubscribe(
            session,
            user_id,
            subscription_id,
        )
        return {"unsubscribed": success}
    except Exception as e:
        logger.exception(f"Error unsubscribing user {user_id} from push")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/push/status")
async def get_push_status(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get push notification permission status.

    [Task]: T028
    [From]: spec.md FR-013
    [From]: contracts/api.yaml §2.3 Get Push Permission Status

    Args:
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with status and subscription_count
    """
    try:
        is_subscribed = await PushService.is_subscribed(session, user_id)
        return {
            "status": "subscribed" if is_subscribed else "not_subscribed",
            "subscription_count": 1 if is_subscribed else 0,
        }
    except Exception as e:
        logger.exception(f"Error getting push status for user {user_id}")
        return {
            "status": "error",
            "subscription_count": 0,
        }


@router.post("/push/test")
async def test_push_notification(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Send a test push notification.

    [Task]: T028 - Debug helper
    [From]: spec.md FR-021 - Send push notification

    Sends a test notification to verify push notification setup.
    Useful for debugging subscription and VAPID configuration.

    Args:
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with send result
    """
    try:
        result = await PushService.send_push(
            session=session,
            user_id=user_id,
            title="🔔 Test Notification",
            body="Push notifications are working! If you see this, everything is configured correctly.",
            icon="/icon.png",
            data={"type": "test", "timestamp": str(datetime.utcnow())},
            notification_type=NotificationType.SYSTEM_UPDATE,
        )
        logger.info(f"Test push notification result for user {user_id}: {result}")
        return result
    except Exception as e:
        logger.exception(f"Error sending test push to user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/test")
async def test_email_notification(
    email: str | None = None,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Send a test email notification.

    [Task]: T037 - Debug helper
    [From]: spec.md FR-024 - Send email notification
    [Fix]: Added rate limiting and deduplication to prevent duplicate sends

    Sends a test email to verify email configuration.
    Optionally accepts an email parameter for testing.

    Args:
        email: Optional email address to send test to (for testing)
        session: Database session
        user_id: Current user ID from JWT

    Returns:
        Dictionary with send result
    """
    # [Fix]: Rate limiting - check if user recently sent a test email
    now = datetime.utcnow()
    last_sent = _test_email_last_sent.get(user_id)

    if last_sent and (now - last_sent).total_seconds() < TEST_EMAIL_COOLDOWN_SECONDS:
        remaining = int(TEST_EMAIL_COOLDOWN_SECONDS - (now - last_sent).total_seconds())
        return {
            "success": False,
            "error": "rate_limited",
            "message": f"Please wait {remaining} seconds before sending another test email.",
        }

    # [Fix]: Use per-user lock to prevent concurrent requests
    user_lock = _test_email_lock[user_id]

    async with user_lock:
        # Double-check after acquiring lock
        now = datetime.utcnow()
        last_sent = _test_email_last_sent.get(user_id)
        if last_sent and (now - last_sent).total_seconds() < TEST_EMAIL_COOLDOWN_SECONDS:
            remaining = int(TEST_EMAIL_COOLDOWN_SECONDS - (now - last_sent).total_seconds())
            return {
                "success": False,
                "error": "rate_limited",
                "message": f"Please wait {remaining} seconds before sending another test email.",
            }

        try:
            # Get user email for the test (or use provided email param)
            to_email = email
            if not to_email:
                # Get email from user table
                user_result = await session.execute(select(User.email).where(User.id == user_id))
                to_email = user_result.scalar_one_or_none()

            if not to_email:
                return {
                    "success": False,
                    "error": "no_email",
                    "message": "No email address configured. Please add an email to your account.",
                }

            # Import here to avoid circular dependency
            from app.models.notification import Notification

            # Create a test notification
            notification = Notification(
                user_id=user_id,
                type=NotificationType.SYSTEM_UPDATE,
                title="🔔 Test Email from Chronos Todo",
                message="This is a test email to verify that email notifications are working correctly. If you received this, your email configuration is all set up!",
            )
            session.add(notification)
            await session.commit()
            await session.refresh(notification)

            # Generate unsubscribe token
            from app.services.unsubscribe_service import UnsubscribeService

            unsubscribe_token = UnsubscribeService.generate_unsubscribe_token(user_id)

            # Send test email directly
            result = await EmailService.send_email(
                session=session,
                notification_id=notification.id,
                to=to_email,
                subject="🔔 Test Email from Chronos Todo",
                html=EmailTemplates.base_template(
                    f"""<div style="text-align: center; padding: 40px 0;">
                        <div style="font-size: 48px; margin-bottom: 20px;">🔔</div>
                        <h2 style="color: #5eead4; margin-bottom: 16px;">Test Email Successful!</h2>
                        <p style="color: #a1a1aa; margin-bottom: 24px;">
                            This is a test email from Chronos Todo. If you received this,
                            your email notification system is working correctly!
                        </p>
                        <p style="color: #71717a; font-size: 14px;">
                            You can now enable email notifications for different events
                            in your notification settings.
                        </p>
                    </div>""",
                    preview_text="Test email from Chronos Todo",
                    unsubscribe_token=unsubscribe_token,
                ),
            )

            # [Fix]: Update last sent time on success
            if result.get("success"):
                _test_email_last_sent[user_id] = now

            logger.info(f"Test email result for user {user_id} to {to_email}: {result}")
            return result
        except Exception as e:
            error_str = str(e)
            logger.exception(f"Error sending test email to user {user_id}")

            # Check for Resend testing limitation error
            if "testing emails" in error_str and "own email address" in error_str:
                return {
                    "success": False,
                    "error": "resend_test_limitation",
                    "message": "Resend test mode only allows sending to your Resend account email (ahsanraj2748@gmail.com). "
                              "Please verify a domain at resend.com/domains to send to other addresses, "
                              "or sign up with your Resend account email.",
                }

            raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Unsubscribe Endpoint
# =============================================================================


@router.get("/email/unsubscribe")
async def unsubscribe_email(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Unsubscribe from email notifications via one-click link.

    [Task]: T046
    [From]: spec.md FR-023 - One-click unsubscribe
    [From]: RFC 8058 - Unsubscribe Post

    Args:
        token: Unsubscribe token from email link
        session: Database session

    Returns:
        HTML confirmation page
    """
    from app.services.unsubscribe_service import UnsubscribeService
    from fastapi.responses import HTMLResponse

    base_url = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")

    # Verify token
    token_data = UnsubscribeService.verify_unsubscribe_token(token)

    if not token_data:
        # Invalid token - return error HTML
        error_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe Failed - Chronos Todo</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e8e8ed;
        }}
        .container {{
            max-width: 500px;
            padding: 40px;
            text-align: center;
        }}
        .icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 40px;
        }}
        h1 {{ margin-bottom: 16px; font-size: 24px; }}
        p {{ color: #a1a1aa; line-height: 1.6; margin-bottom: 24px; }}
        a {{
            display: inline-block;
            background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%);
            color: #0a0a0f;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">✕</div>
        <h1>Unsubscribe Failed</h1>
        <p>The unsubscribe link is invalid or has expired. Please try again or contact support for assistance.</p>
        <a href="{base_url}/settings/notifications">Manage Notification Settings</a>
    </div>
</body>
</html>"""
        return HTMLResponse(content=error_html, status_code=400)

    # Process unsubscribe
    user_id = token_data["user_id"]
    notification_type = token_data.get("notification_type")

    await UnsubscribeService.unsubscribe_user(session, user_id, notification_type)

    # Build notification description
    if not notification_type or notification_type == "all":
        notif_desc = "all notifications"
    else:
        notif_desc = f"{notification_type.replace('_', ' ').title()} notifications"

    # Success - return confirmation HTML
    success_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribed - Chronos Todo</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e8e8ed;
        }}
        .container {{
            max-width: 500px;
            padding: 40px;
            text-align: center;
        }}
        .icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 40px;
        }}
        h1 {{ margin-bottom: 16px; font-size: 24px; }}
        p {{ color: #a1a1aa; line-height: 1.6; margin-bottom: 24px; }}
        a {{
            display: inline-block;
            background: #1e1e2e;
            color: #e8e8ed;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            border: 1px solid #27272a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">✓</div>
        <h1>You're Unsubscribed</h1>
        <p>You have been successfully unsubscribed from {notif_desc}.</p>
        <a href="{base_url}/settings/notifications">Manage Notification Settings</a>
    </div>
</body>
</html>"""
    return HTMLResponse(content=success_html)


# =============================================================================
# Email Webhook Endpoint (Resend)
# =============================================================================


@router.post("/webhooks/resend")
async def resend_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Handle Resend email webhook events.

    [Task]: T041
    [From]: spec.md FR-025 - Bounce handling
    [From]: Context7 /websites/resend - Svix webhook verification

    Processes webhook events from Resend:
    - email.sent: Initial send confirmation
    - email.delivered: Successfully delivered
    - email.bounced: Bounced (disable email for user per FR-025)
    - email.opened: User opened email
    - email.clicked: User clicked link in email

    Webhook signature verification (Svix):
    - Resend uses Svix for webhook signature verification
    - Requires three headers: svix-id, svix-timestamp, svix-signature
    - Automatically rejects timestamps older than 5 minutes (Svix built-in)
    - Requires RESEND_WEBHOOK_SECRET to be set (optional in development)

    Args:
        request: FastAPI Request object (for raw body and Svix headers)
        session: Database session

    Returns:
        Confirmation of processing
    """
    try:
        # Get raw body for signature verification (as string for Svix)
        body_bytes = await request.body()
        body = body_bytes.decode()

        # Get Svix headers (Resend now uses Svix for webhooks)
        svix_id = request.headers.get("svix-id", "")
        svix_timestamp = request.headers.get("svix-timestamp", "")
        svix_signature = request.headers.get("svix-signature", "")

        # Verify webhook signature using Svix format
        if not EmailService.verify_webhook_signature(
            payload=body,
            svix_id=svix_id,
            svix_timestamp=svix_timestamp,
            svix_signature=svix_signature,
        ):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse JSON body after verification
        import json
        event = json.loads(body)

        result = await EmailService.handle_webhook(session, event)
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Invalid webhook JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing Resend webhook: {e}")
        return {"status": "error", "message": str(e)}
