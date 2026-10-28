"""EmailService for sending transactional and digest emails via Resend.

[Task]: T037
[From]: spec.md FR-024, FR-025, FR-026
[From]: Context7 /resend/resend-python
[From]: Context7 /websites/resend - Svix webhook verification
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html import escape as html_escape
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
from svix.webhooks import Webhook as SvixWebhook

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
    "Chronos <noreply@mail.ahsandev.site>"  # Production fallback
)
BASE_URL = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")

# Webhook secret for verifying Resend webhook signatures
# Resend uses Svix for webhooks - get this from Resend dashboard -> Webhooks
# Format: whsec_xxxxxxxxxxxxxxxx
WEBHOOK_SECRET = os.getenv("RESEND_WEBHOOK_SECRET", "")

# Thread pool for running blocking Resend API calls
# Resend SDK is synchronous, so we run it in a thread pool to avoid blocking the event loop
_email_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="resend_email")


# =============================================================================
# Email Templates
# =============================================================================


def friendly_due(value: Any) -> str:
    """ISO due date from notification data -> "Thu 29 Oct, 17:00" (falls back to the raw value)."""
    if not value:
        return "No due date"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return str(value)
    return f"{parsed.strftime('%a')} {parsed.day} {parsed.strftime('%b, %H:%M')}"


class EmailTemplates:
    """HTML email templates on the Chronos "night observatory" palette (D-007).

    Email clients ignore CSS variables, flexbox and most <style> rules, so this is table layout
    with inline styles and hex colours (hex equivalents of the OKLCH tokens in
    frontend/app/globals.css). Light ("day sky") is the default; clients that honour
    prefers-color-scheme get the ink theme from the <style> block. One accent (sun gold) for the
    button; status shows as a small coloured label, never as a full-colour card. No emoji, no
    gradients. Every user-provided string goes through _e() (HTML-escaped).

    [Task]: T038
    [From]: spec.md FR-004 notification types
    """

    # Day sky (light) palette
    BG = "#F3F5FA"
    CARD = "#FFFFFF"
    INK = "#1A2238"
    MUTED = "#5B6478"
    BORDER = "#E3E7F0"
    SUBTLE = "#F5F7FB"
    GOLD = "#F2B84B"  # button fill in both themes, ink text on it
    GOLD_TEXT = "#9A5B05"  # gold as text on white (contrast 5:1)

    # Ink (dark) palette, applied by the prefers-color-scheme block
    DM_BG = "#0E1424"
    DM_CARD = "#161D31"
    DM_INK = "#E9ECF5"
    DM_MUTED = "#9AA3BA"
    DM_BORDER = "#262E47"
    DM_SUBTLE = "#1C2439"

    # Status labels: (light text, light fill, dark text, dark fill)
    TONES = {
        "due": ("#9A5B05", "#FDF1DC", "#F2B84B", "#2C2A26"),
        "overdue": ("#B3261E", "#FCE8E6", "#F08C82", "#33232A"),
        "new": ("#2F5DA8", "#E7EEFA", "#9FC3FF", "#1E2A47"),
        "done": ("#25784A", "#E3F4EA", "#7FD3A0", "#1B2E2A"),
    }

    FONT = "'Hanken Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

    @staticmethod
    def _e(value: Any) -> str:
        """Escape text for HTML (task titles and names are user input)."""
        return html_escape(str(value), quote=True)

    @classmethod
    def _label(cls, tone: str, text: str) -> str:
        fg, bg, _, _ = cls.TONES[tone]
        return (
            f'<span class="tone-{tone}" style="display:inline-block; padding:4px 10px; border-radius:999px; '
            f'background-color:{bg}; color:{fg}; font-family:{cls.FONT}; font-size:12px; font-weight:600; line-height:16px;">{text}</span>'
        )

    @classmethod
    def _button(cls, href: str, text: str) -> str:
        return f'''<table cellpadding="0" cellspacing="0" border="0" role="presentation" class="btn-table" style="margin-top:28px;">
                <tr>
                    <td class="btn-cell" align="center" bgcolor="{cls.GOLD}" style="border-radius:999px;">
                        <a href="{href}" class="btn" style="display:inline-block; padding:13px 26px; border-radius:999px; background-color:{cls.GOLD}; color:#141A2E; font-family:{cls.FONT}; font-size:15px; font-weight:600; text-decoration:none;">{text}</a>
                    </td>
                </tr>
            </table>'''

    @classmethod
    def _task_block(cls, tone: str, label: str, title: str, meta: str) -> str:
        """The task itself: label, title, one line of detail, on a quiet inset panel."""
        return f'''<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top:20px;">
                <tr>
                    <td class="panel" style="padding:18px 20px; border-radius:14px; background-color:{cls.SUBTLE}; border:1px solid {cls.BORDER};">
                        {cls._label(tone, label)}
                        <p class="ink" style="margin:12px 0 4px 0; font-family:{cls.FONT}; font-size:17px; line-height:24px; font-weight:600; color:{cls.INK};">{cls._e(title)}</p>
                        <p class="muted" style="margin:0; font-family:{cls.FONT}; font-size:14px; line-height:20px; color:{cls.MUTED};">{meta}</p>
                    </td>
                </tr>
            </table>'''

    @classmethod
    def _heading(cls, title: str, intro: str) -> str:
        return f'''<h1 class="ink" style="margin:0 0 8px 0; font-family:{cls.FONT}; font-size:24px; line-height:30px; font-weight:600; letter-spacing:-0.3px; color:{cls.INK};">{title}</h1>
            <p class="muted" style="margin:0; font-family:{cls.FONT}; font-size:15px; line-height:23px; color:{cls.MUTED};">{intro}</p>'''

    @classmethod
    def base_template(
        cls,
        content: str,
        preview_text: str = "",
        unsubscribe_token: str | None = None,
    ) -> str:
        """Shell shared by every email: header with the orrery mark, card, footer.

        [Task]: T046 - Add unsubscribe link to emails
        [From]: spec.md FR-023 - One-click unsubscribe
        """
        settings_link = f"{BASE_URL}/settings/notifications"
        unsubscribe_html = ""
        if unsubscribe_token:
            unsubscribe_link = f"{BASE_URL}/api/notifications/email/unsubscribe?token={unsubscribe_token}"
            unsubscribe_html = (
                f' &nbsp;·&nbsp; <a href="{unsubscribe_link}" class="muted" '
                f'style="color:{cls.MUTED}; text-decoration:underline;">Unsubscribe</a>'
            )

        tone_css = "\n".join(
            f"            .tone-{name} {{ color: {dfg} !important; background-color: {dbg} !important; }}\n"
            f"            .num-{name} {{ color: {dfg} !important; }}"
            for name, (_, _, dfg, dbg) in cls.TONES.items()
        )

        return f'''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>Chronos</title>
    <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600&display=swap" rel="stylesheet">
    <!--[if mso]>
    <noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
    <![endif]-->
    <style>
        body {{ margin: 0; padding: 0; -webkit-text-size-adjust: 100%; }}
        a {{ color: {cls.GOLD_TEXT}; }}
        @media only screen and (max-width: 600px) {{
            .container {{ width: 100% !important; }}
            .card-pad {{ padding: 28px 20px !important; }}
            .stat {{ display: block !important; width: 100% !important; margin-bottom: 8px; }}
            .btn-table, .btn-cell, .btn {{ width: 100% !important; display: block !important; text-align: center !important; box-sizing: border-box; }}
        }}
        @media (prefers-color-scheme: dark) {{
            .page {{ background-color: {cls.DM_BG} !important; }}
            .card {{ background-color: {cls.DM_CARD} !important; border-color: {cls.DM_BORDER} !important; }}
            .panel {{ background-color: {cls.DM_SUBTLE} !important; border-color: {cls.DM_BORDER} !important; }}
            .rule {{ border-color: {cls.DM_BORDER} !important; }}
            .ink {{ color: {cls.DM_INK} !important; }}
            .muted {{ color: {cls.DM_MUTED} !important; }}
            .gold {{ color: {cls.GOLD} !important; }}
{tone_css}
        }}
    </style>
</head>
<body class="page" style="margin:0; padding:0; width:100%; background-color:{cls.BG};">
    <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">{cls._e(preview_text)}&#8199;&#65279;&#847;&#8199;&#65279;&#847;</div>
    <table class="page" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="background-color:{cls.BG};">
        <tr>
            <td align="center" style="padding:32px 12px;">
                <table class="container" cellpadding="0" cellspacing="0" border="0" width="560" role="presentation" style="width:560px; max-width:560px;">
                    <tr>
                        <td style="padding:0 4px 20px 4px;">
                            <a href="{BASE_URL}" style="text-decoration:none;">
                                <img src="{BASE_URL}/icon-192.png" width="28" height="28" alt="" style="vertical-align:middle; border:0; border-radius:7px;">
                                <span class="ink" style="vertical-align:middle; margin-left:8px; font-family:{cls.FONT}; font-size:18px; font-weight:600; letter-spacing:-0.2px; color:{cls.INK};">Chronos</span>
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td class="card card-pad" style="padding:36px 36px 32px 36px; background-color:{cls.CARD}; border:1px solid {cls.BORDER}; border-radius:20px;">
                            {content}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:24px 8px 0 8px; font-family:{cls.FONT}; font-size:12px; line-height:19px;">
                            <p class="muted" style="margin:0; color:{cls.MUTED};">You&rsquo;re getting this because email notifications are on for your Chronos account.</p>
                            <p class="muted" style="margin:6px 0 0 0; color:{cls.MUTED};">
                                <a href="{settings_link}" class="muted" style="color:{cls.MUTED}; text-decoration:underline;">Notification settings</a>{unsubscribe_html}
                            </p>
                            <p class="muted" style="margin:14px 0 0 0; color:{cls.MUTED};">&copy; {datetime.now().year} Chronos</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''

    @classmethod
    def message(cls, title: str, body: str, unsubscribe_token: str | None = None) -> str:
        """Fallback for notification types without their own template."""
        content = cls._heading(cls._e(title), cls._e(body)) + cls._button(f"{BASE_URL}/dashboard", "Open Chronos")
        return cls.base_template(content, title, unsubscribe_token)

    @classmethod
    def task_due(
        cls,
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Reminder that a task is coming up. [From]: spec.md FR-004 - TASK_DUE"""
        content = (
            cls._heading("This one is coming up", "A task on your list is due soon.")
            + cls._task_block("due", "Due soon", task_title, f"Due {cls._e(due_date)}")
            + cls._button(f"{BASE_URL}{task_url}", "Open task")
        )
        return cls.base_template(content, f"Due {due_date}: {task_title}", unsubscribe_token)

    @classmethod
    def task_overdue(
        cls,
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """A task passed its due time. [From]: spec.md FR-004 - TASK_OVERDUE"""
        content = (
            cls._heading("This task slipped past its time", "Finish it, move the date, or let it go.")
            + cls._task_block("overdue", "Overdue", task_title, f"Was due {cls._e(due_date)}")
            + cls._button(f"{BASE_URL}{task_url}", "Open task")
        )
        return cls.base_template(content, f"Overdue since {due_date}: {task_title}", unsubscribe_token)

    @classmethod
    def task_assigned(
        cls,
        task_title: str,
        assigned_by: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """A task was added for you. [From]: spec.md FR-004 - TASK_ASSIGNED"""
        content = (
            cls._heading("A new task for you", f"{cls._e(assigned_by)} added it to your list.")
            + cls._task_block("new", "New", task_title, f"From {cls._e(assigned_by)}")
            + cls._button(f"{BASE_URL}{task_url}", "Open task")
        )
        return cls.base_template(content, f"New task from {assigned_by}: {task_title}", unsubscribe_token)

    @classmethod
    def daily_digest(cls, tasks: list[dict[str, Any]]) -> str:
        """Morning list of today's tasks. [From]: spec.md FR-022"""
        shown = tasks[:10]
        open_count = sum(1 for t in tasks if not t.get("completed"))
        rows = ""
        for i, task in enumerate(shown):
            done = bool(task.get("completed"))
            border = "" if i == len(shown) - 1 else f"border-bottom:1px solid {cls.BORDER};"
            mark = (
                f'<span class="tone-done" style="display:inline-block; width:18px; height:18px; border-radius:6px; background-color:{cls.TONES["done"][1]}; color:{cls.TONES["done"][0]}; font-size:12px; line-height:18px; text-align:center; font-weight:700;">&#10003;</span>'
                if done
                else f'<span style="display:inline-block; width:14px; height:14px; border-radius:5px; border:2px solid #B7BED0;"></span>'
            )
            title_style = f"color:{cls.MUTED}; text-decoration:line-through;" if done else f"color:{cls.INK};"
            due = cls._e(task.get("due_date") or "No due date")
            rows += f'''<tr>
                    <td class="rule" width="30" valign="top" style="padding:13px 0; {border}">{mark}</td>
                    <td class="rule" valign="top" style="padding:12px 8px; {border}"><span class="{'muted' if done else 'ink'}" style="font-family:{cls.FONT}; font-size:15px; line-height:21px; {title_style}">{cls._e(task.get('title', 'Untitled'))}</span></td>
                    <td class="rule muted" align="right" valign="top" style="padding:12px 0; {border} font-family:{cls.FONT}; font-size:13px; line-height:21px; color:{cls.MUTED}; white-space:nowrap;">{due}</td>
                </tr>'''

        more = (
            f'<p class="muted" style="margin:12px 0 0 0; font-family:{cls.FONT}; font-size:13px; color:{cls.MUTED};">And {len(tasks) - len(shown)} more in Chronos.</p>'
            if len(tasks) > len(shown)
            else ""
        )
        intro = (
            f"You have {open_count} open task{'' if open_count == 1 else 's'} today."
            if open_count
            else "Nothing open today. Enjoy the clear sky."
        )
        content = (
            cls._heading("Today&rsquo;s orbit", intro)
            + f'''<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top:20px;">{rows}</table>'''
            + more
            + cls._button(f"{BASE_URL}/dashboard", "Open my tasks")
        )
        return cls.base_template(content, intro)

    @classmethod
    def weekly_summary(cls, stats: dict[str, Any]) -> str:
        """End-of-week numbers. [From]: spec.md FR-022"""
        completed = int(stats.get("completed", 0))
        pending = int(stats.get("pending", 0))
        overdue = int(stats.get("overdue", 0))

        def stat(value: int, label: str, tone: str | None) -> str:
            color = cls.TONES[tone][0] if tone else cls.INK
            klass = f"num-{tone}" if tone else "ink"
            return f'''<td class="stat" width="33%" valign="top" style="padding:0 4px;">
                        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                            <tr><td class="panel" style="padding:16px; border-radius:14px; background-color:{cls.SUBTLE}; border:1px solid {cls.BORDER};">
                                <p class="{klass}" style="margin:0; font-family:{cls.FONT}; font-size:28px; line-height:32px; font-weight:600; color:{color}; background-color:transparent;">{value}</p>
                                <p class="muted" style="margin:4px 0 0 0; font-family:{cls.FONT}; font-size:13px; color:{cls.MUTED};">{label}</p>
                            </td></tr>
                        </table>
                    </td>'''

        total = completed + pending
        intro = (
            f"You finished {completed} of {total} task{'' if total == 1 else 's'} this week."
            if total
            else "A quiet week: no tasks were due."
        )
        content = (
            cls._heading("Your week in orbit", intro)
            + f'''<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin:20px -4px 0 -4px;">
                <tr>
                    {stat(completed, "Done", "done")}
                    {stat(pending, "Still open", None)}
                    {stat(overdue, "Overdue", "overdue" if overdue else None)}
                </tr>
            </table>'''
            + cls._button(f"{BASE_URL}/dashboard", "Plan next week")
        )
        return cls.base_template(content, intro)

    @classmethod
    def welcome(
        cls,
        user_email: str,
        user_name: str | None = None,
        unsubscribe_token: str | None = None,
    ) -> str:
        """First email after sign-up: what Chronos does and the first step."""
        display_name = cls._e(user_name or user_email.split("@")[0])
        steps = [
            ("Add a task", "Give it a due date and it takes its place on your orbits: today, this week or later."),
            ("Talk to Kairos", "Press Ctrl+K and say what you need. Kairos adds, moves and finishes tasks for you."),
            ("Get reminded", "Turn on push or email reminders in notification settings."),
        ]
        step_rows = ""
        for n, (title, text) in enumerate(steps, start=1):
            step_rows += f'''<tr>
                    <td width="40" valign="top" style="padding:10px 0;">
                        <span style="display:inline-block; width:28px; height:28px; border-radius:999px; background-color:{cls.GOLD}; color:#141A2E; font-family:{cls.FONT}; font-size:13px; font-weight:700; line-height:28px; text-align:center;">{n}</span>
                    </td>
                    <td valign="top" style="padding:10px 0;">
                        <p class="ink" style="margin:0; font-family:{cls.FONT}; font-size:15px; line-height:22px; font-weight:600; color:{cls.INK};">{title}</p>
                        <p class="muted" style="margin:2px 0 0 0; font-family:{cls.FONT}; font-size:14px; line-height:21px; color:{cls.MUTED};">{text}</p>
                    </td>
                </tr>'''

        content = (
            cls._heading(
                f"Welcome to Chronos, {display_name}",
                "Chronos keeps your tasks in orbit around today, and Kairos, its assistant, helps you plan them.",
            )
            + f'''<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top:16px;">{step_rows}</table>'''
            + cls._button(f"{BASE_URL}/dashboard", "Add your first task")
        )
        return cls.base_template(content, "Three steps to get your tasks in orbit", unsubscribe_token)


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
        task_title = data.get("task_title", "Untitled task")
        due_date = friendly_due(data.get("due_date"))
        task_id = data.get("task_id", notification.related_task_id)
        task_url = f"/dashboard?task={task_id}" if task_id else "/dashboard"

        if notification.type == NotificationType.TASK_DUE:
            subject = f"Due soon: {task_title}"
            html = EmailTemplates.task_due(task_title, due_date, task_url, unsubscribe_token)
        elif notification.type == NotificationType.TASK_OVERDUE:
            subject = f"Overdue: {task_title}"
            html = EmailTemplates.task_overdue(task_title, due_date, task_url, unsubscribe_token)
        elif notification.type == NotificationType.TASK_ASSIGNED:
            assigned_by = data.get("assigned_by", "Someone")
            subject = f"New task: {task_title}"
            html = EmailTemplates.task_assigned(task_title, assigned_by, task_url, unsubscribe_token)
        else:
            # Default template
            subject = notification.title
            html = EmailTemplates.message(notification.title, notification.message or "", unsubscribe_token)

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
            title="Daily digest",
            message=f"Your daily digest with {len(tasks)} tasks",
            data={"task_count": len(tasks), "digest_type": "daily"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        subject = f"Your tasks for {datetime.now().strftime('%A %d %B').replace(' 0', ' ')}"
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
            title="Weekly summary",
            message=f"Your weekly summary: {stats.get('completed', 0)} completed",
            data={"stats": stats, "digest_type": "weekly"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        subject = f"Your week in Chronos, to {datetime.now().strftime('%d %B').lstrip('0')}"
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
            title="Welcome to Chronos",
            message="Add your first task, or ask Kairos to plan your day.",
            data={"email_type": "welcome"},
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        display_name = user_name or to.split('@')[0]
        subject = f"Welcome to Chronos, {display_name}"
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
    def verify_webhook_signature(
        payload: str,
        svix_id: str,
        svix_timestamp: str,
        svix_signature: str,
    ) -> bool:
        """Verify Resend webhook signature using Svix.

        [From]: Resend webhook documentation with Svix
        https://resend.com/docs/dashboard/webhooks/verify-webhooks-requests

        Resend now uses Svix for webhook signature verification.
        Svix sends three headers that must be verified together:
        - svix-id: Unique identifier for this webhook delivery
        - svix-timestamp: Unix timestamp of when the webhook was sent
        - svix-signature: The actual signature to verify

        Args:
            payload: Raw request body as string (not bytes!)
            svix_id: Value from svix-id header
            svix_timestamp: Value from svix-timestamp header
            svix_signature: Value from svix-signature header

        Returns:
            True if signature is valid, False otherwise
        """
        if not WEBHOOK_SECRET:
            # If no webhook secret is configured, skip verification (development mode)
            logger.warning("WEBHOOK_SECRET not configured - skipping webhook signature verification")
            return True

        if not all([svix_id, svix_timestamp, svix_signature]):
            logger.warning(
                f"Missing Svix headers - svix-id: {bool(svix_id)}, "
                f"svix-timestamp: {bool(svix_timestamp)}, "
                f"svix-signature: {bool(svix_signature)}"
            )
            return False

        try:
            # Initialize Svix Webhook with the secret
            wh = SvixWebhook(WEBHOOK_SECRET)

            # Verify the webhook signature
            # Svix expects headers as a dict
            headers = {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            }

            # This will raise an exception if verification fails
            wh.verify(payload, headers)

            logger.info("Webhook signature verified successfully")
            return True

        except Exception as e:
            logger.warning(f"Webhook signature verification failed: {e}")
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
