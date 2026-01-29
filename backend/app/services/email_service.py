"""EmailService for sending transactional and digest emails via Resend.

[Task]: T037
[From]: spec.md FR-024, FR-025, FR-026
[From]: Context7 /resend/resend-python
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Optional

import resend
from resend.exceptions import (
    InvalidApiKeyError,
    MissingApiKeyError,
    RateLimitError,
    ResendError,
    ValidationError,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib

from app.models.notification import Notification, NotificationType
from app.models.email_delivery_log import (
    EmailDeliveryLog,
    EmailDeliveryStatus,
)

logger = logging.getLogger(__name__)

# Configure Resend API key
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Default sender email (must be verified in Resend dashboard)
# Set EMAIL_FROM in .env to use your verified domain (e.g., noreply@ahsandev.site)
DEFAULT_SENDER = os.getenv(
    "EMAIL_FROM",
    "Chronos Todo <onboarding@resend.dev>"  # Fallback for development
)
BASE_URL = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")

# Webhook secret for verifying Resend webhook signatures
# Set RESEND_WEBHOOK_SECRET in .env (get from Resend dashboard -> API Keys -> Webhook Signing)
WEBHOOK_SECRET = os.getenv("RESEND_WEBHOOK_SECRET", "")

# Thread pool for running blocking Resend API calls
# Resend SDK is synchronous, so we run it in a thread pool to avoid blocking the event loop
_email_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="resend_email")


# =============================================================================
# Email Templates
# =============================================================================


class EmailTemplates:
    """HTML email templates for different notification types.

    [Task]: T038
    [From]: spec.md FR-004 notification types
    """

    @staticmethod
    def base_template(
        content: str,
        preview_text: str = "",
        unsubscribe_token: str | None = None,
    ) -> str:
        """Base email template with Deep Space themed styling.

        [Task]: T046 - Add unsubscribe link to emails
        [From]: spec.md FR-023 - One-click unsubscribe

        Args:
            content: HTML content for the email body
            preview_text: Preview text for email clients
            unsubscribe_token: Optional token for unsubscribe link

        Returns:
            Complete HTML email with styles
        """
        # Build unsubscribe link if token provided
        unsubscribe_link = f"{BASE_URL}/api/notifications/email/unsubscribe?token={unsubscribe_token}" if unsubscribe_token else f"{BASE_URL}/settings/notifications"
        unsubscribe_html = f'<p style="margin: 5px 0;"><a href="{unsubscribe_link}" style="color: #71717a; text-decoration: underline;">Unsubscribe</a></p>' if unsubscribe_token else ""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chronos Todo</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0f; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <!-- Logo/Header -->
        <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid #1e1e2e;">
            <h1 style="color: #e8e8ed; margin: 0; font-size: 24px; font-weight: 600;">
                <span style="color: #5eead4;">◈</span> Chronos Todo
            </h1>
        </div>

        <!-- Content -->
        <div style="padding: 30px 0; color: #e8e8ed;">
            {content}
        </div>

        <!-- Footer -->
        <div style="padding-top: 20px; border-top: 1px solid #1e1e2e; text-align: center; font-size: 12px; color: #71717a;">
            <p style="margin: 0;">You received this email because you have notifications enabled in Chronos Todo.</p>
            <p style="margin: 10px 0;">
                <a href="{BASE_URL}/settings/notifications" style="color: #5eead4; text-decoration: none;">Manage Notification Settings</a>
            </p>
            {unsubscribe_html}
        </div>
    </div>
</body>
</html>"""

    @staticmethod
    def task_due(
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for task due reminder.

        [From]: spec.md FR-004 - TASK_DUE notification
        [Task]: T046 - Add unsubscribe token
        """
        content = f"""
            <h2 style="color: #fbbf24; margin-top: 0;">⏰ Task Due Soon</h2>
            <p style="font-size: 16px; line-height: 1.6;">Your task is due soon:</p>

            <div style="background-color: #1e1e2e; border-left: 4px solid #5eead4; padding: 20px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #e8e8ed;">{task_title}</h3>
                <p style="margin: 0; color: #a1a1aa;">Due: {due_date}</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{BASE_URL}{task_url}" style="display: inline-block; background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); color: #0a0a0f; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                    View Task
                </a>
            </div>
        """
        return EmailTemplates.base_template(content, f"Task due: {task_title}", unsubscribe_token)

    @staticmethod
    def task_overdue(
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for overdue task.

        [From]: spec.md FR-004 - TASK_OVERDUE notification
        [Task]: T046 - Add unsubscribe token
        """
        content = f"""
            <h2 style="color: #f87171; margin-top: 0;">⚠️ Task Overdue</h2>
            <p style="font-size: 16px; line-height: 1.6;">The following task is now overdue:</p>

            <div style="background-color: #1e1e2e; border-left: 4px solid #f87171; padding: 20px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #e8e8ed;">{task_title}</h3>
                <p style="margin: 0; color: #a1a1aa;">Was due: {due_date}</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{BASE_URL}{task_url}" style="display: inline-block; background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                    View Task
                </a>
            </div>
        """
        return EmailTemplates.base_template(content, f"Overdue: {task_title}", unsubscribe_token)

    @staticmethod
    def task_assigned(
        task_title: str,
        assigned_by: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for task assignment.

        [From]: spec.md FR-004 - TASK_ASSIGNED notification
        [Task]: T046 - Add unsubscribe token
        """
        content = f"""
            <h2 style="color: #5eead4; margin-top: 0;">✨ New Task Assigned</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                You have been assigned a new task by <strong>{assigned_by}</strong>:
            </p>

            <div style="background-color: #1e1e2e; border-left: 4px solid #5eead4; padding: 20px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #e8e8ed;">{task_title}</h3>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{BASE_URL}{task_url}" style="display: inline-block; background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); color: #0a0a0f; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                    View Task
                </a>
            </div>
        """
        return EmailTemplates.base_template(content, f"Assigned: {task_title}", unsubscribe_token)

    @staticmethod
    def daily_digest(tasks: list[dict[str, Any]]) -> str:
        """Email template for daily task digest.

        [From]: spec.md FR-022 - Email digest frequency
        """
        task_rows = ""
        for task in tasks[:10]:  # Limit to 10 tasks
            status_emoji = "✓" if task.get("completed") else "○"
            task_rows += f"""
                <tr style="border-bottom: 1px solid #1e1e2e;">
                    <td style="padding: 12px 8px;">{status_emoji}</td>
                    <td style="padding: 12px 8px; color: #e8e8ed;">{task.get('title', 'Untitled')}</td>
                    <td style="padding: 12px 8px; color: #a1a1aa; font-size: 14px;">{task.get('due_date', 'No due date')}</td>
                </tr>
            """

        content = f"""
            <h2 style="margin-top: 0;">📋 Your Daily Task Digest</h2>
            <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">Here's what you have due today:</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="border-bottom: 2px solid #1e1e2e; text-align: left;">
                        <th style="padding: 12px 8px; color: #71717a; font-size: 12px; text-transform: uppercase;">Status</th>
                        <th style="padding: 12px 8px; color: #71717a; font-size: 12px; text-transform: uppercase;">Task</th>
                        <th style="padding: 12px 8px; color: #71717a; font-size: 12px; text-transform: uppercase;">Due Date</th>
                    </tr>
                </thead>
                <tbody>
                    {task_rows}
                </tbody>
            </table>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{BASE_URL}/dashboard" style="display: inline-block; background: #1e1e2e; color: #e8e8ed; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600; border: 1px solid #27272a;">
                    View All Tasks
                </a>
            </div>
        """
        return EmailTemplates.base_template(content, "Your daily task digest")

    @staticmethod
    def weekly_summary(stats: dict[str, Any]) -> str:
        """Email template for weekly summary.

        [From]: spec.md FR-022 - Email digest frequency
        """
        content = f"""
            <h2 style="margin-top: 0;">📊 Your Weekly Summary</h2>
            <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">Here's how you did this week:</p>

            <div style="display: flex; gap: 20px; margin: 30px 0;">
                <div style="flex: 1; background-color: #1e1e2e; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 36px; font-weight: 700; color: #5eead4;">{stats.get('completed', 0)}</div>
                    <div style="color: #71717a; font-size: 14px; margin-top: 8px;">Completed</div>
                </div>
                <div style="flex: 1; background-color: #1e1e2e; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 36px; font-weight: 700; color: #fbbf24;">{stats.get('pending', 0)}</div>
                    <div style="color: #71717a; font-size: 14px; margin-top: 8px;">Still Pending</div>
                </div>
                <div style="flex: 1; background-color: #1e1e2e; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 36px; font-weight: 700; color: #f87171;">{stats.get('overdue', 0)}</div>
                    <div style="color: #71717a; font-size: 14px; margin-top: 8px;">Overdue</div>
                </div>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{BASE_URL}/dashboard" style="display: inline-block; background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); color: #0a0a0f; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                    View Dashboard
                </a>
            </div>
        """
        return EmailTemplates.base_template(content, "Your weekly summary")

    @staticmethod
    def welcome(
        user_email: str,
        user_name: str | None = None,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for new user welcome.

        [Task]: Welcome email for new users
        """
        display_name = user_name or user_email.split('@')[0]
        greeting = f"Hi {display_name}" if user_name else f"Welcome to Chronos Todo"

        content = f"""
            <div style="text-align: center; padding: 30px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">◈</div>
                <h2 style="margin-top: 0; color: #5eead4;">{greeting}!</h2>
                <p style="color: #a1a1aa; font-size: 18px; line-height: 1.6;">
                    You've successfully joined Chronos Todo – your personal task management companion.
                </p>
            </div>

            <div style="background-color: #1e1e2e; border-radius: 12px; padding: 30px; margin: 30px 0;">
                <h3 style="margin-top: 0; color: #e8e8ed;">Get Started with Chronos Todo</h3>
                <p style="color: #a1a1aa; line-height: 1.6;">
                    Chronos Todo helps you stay organized and productive with powerful task management features.
                </p>

                <div style="margin: 30px 0;">
                    <div style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                        <div style="background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0;">✓</div>
                        <div>
                            <h4 style="margin: 0 0 4px 0; color: #e8e8ed;">Create Tasks</h4>
                            <p style="margin: 0; color: #71717a; font-size: 14px;">Add tasks with due dates, priorities, and tags</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                        <div style="background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0;">⏰</div>
                        <div>
                            <h4 style="margin: 0 0 4px 0; color: #e8e8ed;">Set Reminders</h4>
                            <p style="margin: 0; color: #71717a; font-size: 14px;">Get email and push notifications for due tasks</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                        <div style="background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0;">📊</div>
                        <div>
                            <h4 style="margin: 0 0 4px 0; color: #e8e8ed;">Track Progress</h4>
                            <p style="margin: 0; color: #71717a; font-size: 14px;">View daily digests and weekly summaries</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start;">
                        <div style="background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0;">🔔</div>
                        <div>
                            <h4 style="margin: 0 0 4px 0; color: #e8e8ed;">Stay Notified</h4>
                            <p style="margin: 0; color: #71717a; font-size: 14px;">Real-time updates via push and email notifications</p>
                        </div>
                    </div>
                </div>
            </div>

            <div style="text-align: center; margin: 40px 0;">
                <a href="{BASE_URL}/dashboard" style="display: inline-block; background: linear-gradient(135deg, #5eead4 0%, #6366f1 100%); color: #0a0a0f; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                    Create Your First Task →
                </a>
            </div>

            <p style="text-align: center; color: #71717a; font-size: 14px;">
                Questions or feedback? <a href="mailto:support@chronostodo.com" style="color: #5eead4; text-decoration: none;">Contact Support</a>
            </p>
        """
        return EmailTemplates.base_template(content, f"Welcome to Chronos Todo, {display_name}!", unsubscribe_token)


# =============================================================================
# Email Service
# =============================================================================


class EmailService:
    """Service for sending emails via Resend API.

    [Task]: T037
    [From]: spec.md FR-024 - Send email notifications
    [From]: Context7 /resend/resend-python

    Features:
    - Transactional emails (task due, overdue, assigned)
    - Digest emails (daily, weekly)
    - Webhook tracking for delivery status
    - Bounce handling (disable email per FR-025)
    """

    @staticmethod
    async def send_email(
        session: AsyncSession,
        notification_id: int,
        to: str,
        subject: str,
        html: str,
        unsubscribe_token: str | None = None,
    ) -> dict[str, Any]:
        """Send an email via Resend API.

        [Task]: T037
        [From]: Context7 /resend/resend-python - Send Single Email

        Args:
            session: Database session
            notification_id: Notification ID for tracking
            to: Recipient email address
            subject: Email subject line
            html: Email HTML content

        Returns:
            Dict with success status and email_id or error
        """
        # Create initial delivery log
        log = EmailDeliveryLog(
            notification_id=notification_id,
            email=to,
            status=EmailDeliveryStatus.SENT,
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)

        if not resend.api_key:
            logger.error("RESEND_API_KEY not configured")
            log.status = EmailDeliveryStatus.BOUNCED
            log.error_message = "API key not configured"
            log.error_code = "CONFIG_ERROR"
            await session.commit()
            return {
                "success": False,
                "error": "api_key_missing",
                "message": "Email service not configured",
            }

        params: resend.Emails.SendParams = {
            "from": DEFAULT_SENDER,
            "to": [to],
            "subject": subject,
            "html": html,
            "tags": [
                {"name": "notification_id", "value": str(notification_id)},
                {"name": "category", "value": "todo_notification"},
            ],
        }

        try:
            # Send email via Resend - run in thread pool to avoid blocking event loop
            # Resend SDK is synchronous, so we use asyncio.to_thread() to run it in a background thread
            loop = asyncio.get_event_loop()
            email = await loop.run_in_executor(_email_executor, resend.Emails.send, params)

            # Store Resend's email ID for webhook matching
            resend_id = email.get("id")
            log.resend_email_id = resend_id
            log.sent_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Email sent successfully: {resend_id} to {to}")
            return {
                "success": True,
                "email_id": resend_id,
                "message_id": email.get("message_id"),
            }

        except MissingApiKeyError as e:
            logger.error(f"Resend API key missing: {e.message}")
            log.status = EmailDeliveryStatus.BOUNCED
            log.error_message = e.message
            log.error_code = "MISSING_API_KEY"
            await session.commit()
            return {"success": False, "error": "missing_api_key", "message": e.message}

        except InvalidApiKeyError as e:
            logger.error(f"Invalid Resend API key: {e.message}")
            log.status = EmailDeliveryStatus.BOUNCED
            log.error_message = e.message
            log.error_code = "INVALID_API_KEY"
            await session.commit()
            return {"success": False, "error": "invalid_api_key", "message": e.message}

        except ValidationError as e:
            logger.error(f"Email validation failed: {e.message}")
            log.status = EmailDeliveryStatus.BOUNCED
            log.error_message = e.message
            log.error_code = str(e.code)
            await session.commit()
            return {"success": False, "error": "validation_error", "message": e.message}

        except RateLimitError as e:
            logger.warning(f"Resend rate limit exceeded: {e.message}")
            log.error_message = f"Rate limited: {e.message}"
            log.error_code = "RATE_LIMITED"
            await session.commit()
            return {"success": False, "error": "rate_limit_exceeded", "message": e.message}

        except ResendError as e:
            logger.error(f"Resend API error: {e.message}")
            log.error_message = e.message
            log.error_code = str(getattr(e, "code", "UNKNOWN"))
            await session.commit()
            return {"success": False, "error": "api_error", "message": e.message}

        except Exception as e:
            logger.exception(f"Unexpected error sending email: {e}")
            log.error_message = str(e)
            log.error_code = "UNKNOWN"
            await session.commit()
            return {"success": False, "error": "unknown", "message": str(e)}

    @staticmethod
    async def send_notification_email(
        session: AsyncSession,
        notification: Notification,
        to: str,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Send email for a notification.

        [Task]: T037
        [From]: spec.md FR-004 - Notification types
        [Task]: T046 - Include unsubscribe token

        Routes to appropriate template based on notification type.

        Args:
            session: Database session
            notification: Notification object with type and data
            to: Recipient email address
            user_id: User ID for unsubscribe token generation

        Returns:
            Dict with success status
        """
        # Generate unsubscribe token
        # [Task]: T046 - One-click unsubscribe per FR-023
        unsubscribe_token = None
        if user_id:
            from app.services.unsubscribe_service import UnsubscribeService

            unsubscribe_token = UnsubscribeService.generate_unsubscribe_token(
                user_id=user_id,
                notification_type=notification.type.value if notification.type else None,
            )

        # Get template and subject based on notification type
        data = notification.data or {}
        task_title = data.get("task_title", "Untitled Task")
        due_date = data.get("due_date", "No due date")
        task_id = data.get("task_id", notification.related_task_id)
        task_url = f"/dashboard?task={task_id}" if task_id else "/dashboard"

        if notification.type == NotificationType.TASK_DUE:
            subject = f"⏰ Task Due: {task_title}"
            html = EmailTemplates.task_due(task_title, due_date, task_url, unsubscribe_token)
        elif notification.type == NotificationType.TASK_OVERDUE:
            subject = f"⚠️ Overdue: {task_title}"
            html = EmailTemplates.task_overdue(task_title, due_date, task_url, unsubscribe_token)
        elif notification.type == NotificationType.TASK_ASSIGNED:
            assigned_by = data.get("assigned_by", "Someone")
            subject = f"✨ New Task: {task_title}"
            html = EmailTemplates.task_assigned(task_title, assigned_by, task_url, unsubscribe_token)
        else:
            # Default template
            subject = f"Chronos Todo: {notification.title}"
            html = EmailTemplates.base_template(
                f"<p>{notification.message}</p>",
                notification.title,
                unsubscribe_token,
            )

        # Send the email
        return await EmailService.send_email(
            session=session,
            notification_id=notification.id,
            to=to,
            subject=subject,
            html=html,
            unsubscribe_token=unsubscribe_token,
        )

    @staticmethod
    async def send_daily_digest(
        session: AsyncSession,
        user_id: str,
        to: str,
        tasks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Send daily digest email.

        [Task]: T039
        [From]: spec.md FR-022 - Daily digest frequency

        Args:
            session: Database session
            user_id: User ID
            to: Recipient email
            tasks: List of tasks for the digest

        Returns:
            Dict with success status
        """
        # First create a notification for the digest
        from app.models.notification import Notification

        notification = Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM_UPDATE,
            title="Daily Digest",
            message=f"Your daily digest with {len(tasks)} tasks",
            data={"task_count": len(tasks), "digest_type": "daily"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        subject = f"📋 Your Daily Task Digest - {datetime.now().strftime('%B %d')}"
        html = EmailTemplates.daily_digest(tasks)

        return await EmailService.send_email(
            session=session,
            notification_id=notification.id,
            to=to,
            subject=subject,
            html=html,
        )

    @staticmethod
    async def send_weekly_summary(
        session: AsyncSession,
        user_id: str,
        to: str,
        stats: dict[str, Any],
    ) -> dict[str, Any]:
        """Send weekly summary email.

        [Task]: T039
        [From]: spec.md FR-022 - Weekly digest frequency

        Args:
            session: Database session
            user_id: User ID
            to: Recipient email
            stats: Weekly statistics (completed, pending, overdue)

        Returns:
            Dict with success status
        """
        # First create a notification for the summary
        from app.models.notification import Notification

        notification = Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM_UPDATE,
            title="Weekly Summary",
            message=f"Your weekly summary: {stats.get('completed', 0)} completed",
            data={"stats": stats, "digest_type": "weekly"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        subject = f"📊 Your Weekly Summary - {datetime.now().strftime('%B %d')}"
        html = EmailTemplates.weekly_summary(stats)

        return await EmailService.send_email(
            session=session,
            notification_id=notification.id,
            to=to,
            subject=subject,
            html=html,
        )

    @staticmethod
    async def send_welcome_email(
        session: AsyncSession,
        user_id: str,
        to: str,
        user_name: str | None = None,
    ) -> dict[str, Any]:
        """Send welcome email to newly registered user.

        [Task]: Welcome email for new users

        Args:
            session: Database session
            user_id: User ID
            to: Recipient email
            user_name: Optional user's display name

        Returns:
            Dict with success status
        """
        # Create a notification for the welcome email
        from app.models.notification import Notification
        from app.services.unsubscribe_service import UnsubscribeService

        unsubscribe_token = UnsubscribeService.generate_unsubscribe_token(user_id)

        notification = Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM_UPDATE,
            title="Welcome to Chronos Todo!",
            message="Thank you for joining us. Get started by creating your first task!",
            data={"email_type": "welcome"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        display_name = user_name or to.split('@')[0]
        subject = f"Welcome to Chronos Todo, {display_name}!"
        html = EmailTemplates.welcome(to, user_name, unsubscribe_token)

        result = await EmailService.send_email(
            session=session,
            notification_id=notification.id,
            to=to,
            subject=subject,
            html=html,
            unsubscribe_token=unsubscribe_token,
        )

        if result.get("success"):
            logger.info(f"Welcome email sent to {to}")
        else:
            logger.warning(f"Failed to send welcome email to {to}: {result.get('message')}")

        return result

    @staticmethod
    async def disable_email_for_user(
        session: AsyncSession,
        email: str,
    ) -> None:
        """Disable email notifications for a bounced email.

        [Task]: T040
        [From]: spec.md FR-025 - Disable email on bounce

        Args:
            session: Database session
            email: Bounced email address
        """
        # Find user by email and disable all email preferences
        from app.models.notification import NotificationPreference
        from app.models import User

        # Find user by email address from users table
        user_result = await session.execute(
            select(User.id).where(User.email == email)
        )
        user_id = user_result.scalar_one_or_none()

        if not user_id:
            logger.warning(f"No user found for bounced email: {email}")
            return

        # Disable all email preferences for this user
        result = await session.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )

        for pref in result.scalars().all():
            pref.email_enabled = False

        await session.commit()
        logger.info(f"Disabled email for user {user_id} due to bounce at {email}")

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verify Resend webhook signature for security.

        [From]: Resend webhook documentation
        https://resend.com/docs/api-reference/webhooks/create#webhook-signatures

        Resend signs webhook requests with HMAC using the webhook secret.
        The signature is in the format: t={timestamp},v1={signature}

        Args:
            payload: Raw request body as bytes
            signature: Value from resend-signature header

        Returns:
            True if signature is valid, False otherwise
        """
        if not WEBHOOK_SECRET:
            # If no webhook secret is configured, skip verification (development mode)
            logger.warning("WEBHOOK_SECRET not configured - skipping webhook signature verification")
            return True

        if not signature:
            logger.warning("Missing resend-signature header")
            return False

        try:
            # Parse signature: format is "t={timestamp},v1={signature}"
            parts = signature.split(",")
            timestamp_part = None
            signature_part = None

            for part in parts:
                if part.startswith("t="):
                    timestamp_part = part.split("=")[1]
                elif part.startswith("v1="):
                    signature_part = part.split("=")[1]

            if not timestamp_part or not signature_part:
                logger.warning(f"Invalid signature format: {signature}")
                return False

            # Check timestamp - reject if older than 5 minutes to prevent replay attacks
            import time
            current_time = int(time.time())
            webhook_time = int(timestamp_part)
            if current_time - webhook_time > 300:  # 5 minutes
                logger.warning(f"Webhook timestamp too old: {webhook_time}")
                return False

            # Verify HMAC signature
            expected_signature = hmac.new(
                WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # Constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, signature_part)

            if not is_valid:
                logger.warning("Invalid webhook signature")

            return is_valid

        except Exception as e:
            logger.exception(f"Error verifying webhook signature: {e}")
            return False

    @staticmethod
    async def handle_webhook(
        session: AsyncSession,
        event: dict[str, Any],
    ) -> dict[str, str]:
        """Handle Resend webhook events.

        [Task]: T041
        [From]: spec.md FR-025 - Bounce handling
        [From]: Context7 /resend/resend-python - Webhooks

        Args:
            session: Database session
            event: Webhook event payload from Resend

        Returns:
            Dict with status message
        """
        event_type = event.get("type", "")
        event_data = event.get("data", {})

        if event_type == "email.delivered":
            # Update delivery log by Resend email ID
            resend_id = event_data.get("email_id")
            await session.execute(
                update(EmailDeliveryLog)
                .where(EmailDeliveryLog.resend_email_id == resend_id)
                .values(
                    status=EmailDeliveryStatus.DELIVERED,
                    delivered_at=datetime.utcnow(),
                )
            )
            await session.commit()
            logger.info(f"Email delivered: {resend_id}")

        elif event_type == "email.opened":
            resend_id = event_data.get("email_id")
            await session.execute(
                update(EmailDeliveryLog)
                .where(EmailDeliveryLog.resend_email_id == resend_id)
                .values(
                    status=EmailDeliveryStatus.OPENED,
                    opened_at=datetime.utcnow(),
                )
            )
            await session.commit()
            logger.info(f"Email opened: {resend_id}")

        elif event_type == "email.clicked":
            resend_id = event_data.get("email_id")
            await session.execute(
                update(EmailDeliveryLog)
                .where(EmailDeliveryLog.resend_email_id == resend_id)
                .values(
                    status=EmailDeliveryStatus.CLICKED,
                    clicked_at=datetime.utcnow(),
                )
            )
            await session.commit()
            logger.info(f"Email clicked: {resend_id}")

        elif event_type == "email.bounced":
            # Handle bounce - disable email per FR-025
            email = event_data.get("to", [{}])[0].get("email", "")
            reason = event_data.get("reason", "Unknown")

            # Update delivery log by Resend email ID
            resend_id = event_data.get("email_id")
            await session.execute(
                update(EmailDeliveryLog)
                .where(EmailDeliveryLog.resend_email_id == resend_id)
                .values(
                    status=EmailDeliveryStatus.BOUNCED,
                    error_message=reason,
                    error_code="BOUNCED",
                )
            )

            # Disable email for this user
            await EmailService.disable_email_for_user(session, email)
            await session.commit()
            logger.warning(f"Email bounced for {email}: {reason}")

        return {"status": "processed"}
