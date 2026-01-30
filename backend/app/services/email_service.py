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


class EmailTemplates:
    """Production HTML email templates with dark/light mode support.

    [Task]: T038
    [From]: spec.md FR-004 notification types
    [Updated]: Production-ready with responsive design and dark mode support
    """

    # Color constants matching the Deep Space theme
    # Light mode colors (default)
    LM_BG = "#f8f8fa"
    LM_CARD = "#ffffff"
    LM_TEXT = "#1e1e23"
    LM_TEXT_MUTED = "#6b7280"
    LM_BORDER = "#e5e7eb"
    LM_PRIMARY = "#00f5ff"
    LM_PRIMARY_DARK = "#0891b2"
    LM_SECONDARY = "#a855f7"
    LM_SUCCESS = "#22c55e"
    LM_WARNING = "#fbbf24"
    LM_ERROR = "#ef4444"

    # Dark mode colors
    DM_BG = "#0a0a0f"
    DM_CARD = "#14141e"
    DM_TEXT = "#f5f5fa"
    DM_TEXT_MUTED = "#9696aa"
    DM_BORDER = "rgba(255, 255, 255, 0.1)"
    DM_PRIMARY = "#00f5ff"
    DM_SECONDARY = "#a855f7"

    @staticmethod
    def base_template(
        content: str,
        preview_text: str = "",
        unsubscribe_token: str | None = None,
    ) -> str:
        """Production base email template with dark/light mode support.

        [Task]: T046 - Add unsubscribe link to emails
        [From]: spec.md FR-023 - One-click unsubscribe
        [Updated]: Dark mode via @media (prefers-color-scheme: dark)

        Args:
            content: HTML content for the email body
            preview_text: Preview text for email clients
            unsubscribe_token: Optional token for unsubscribe link

        Returns:
            Complete HTML email with responsive styles and dark mode support
        """
        # Build unsubscribe link if token provided
        unsubscribe_link = f"{BASE_URL}/api/notifications/email/unsubscribe?token={unsubscribe_token}" if unsubscribe_token else f"{BASE_URL}/settings/notifications"
        unsubscribe_html = f'<p style="margin: 8px 0 0 0;"><a href="{unsubscribe_link}" style="color: #6b7280; text-decoration: underline;">Unsubscribe from these emails</a></p>' if unsubscribe_token else ""

        return f'''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>Chronos</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        /* Reset styles */
        .email-body {{ margin: 0; padding: 0; width: 100% !important; }}
        .email-wrapper {{ width: 100%; table-layout: fixed; background-color: #f8f8fa; }}
        .email-container {{ max-width: 600px; margin: 0 auto; }}
        .email-card {{ background-color: #ffffff; border-radius: 16px; overflow: hidden; }}
        .email-header {{ text-align: center; padding: 32px 24px 24px; border-bottom: 1px solid #e5e7eb; }}
        .email-content {{ padding: 32px 24px; color: #1e1e23; }}
        .email-footer {{ padding: 24px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 13px; }}
        .email-footer a {{ color: #6b7280; text-decoration: none; }}
        .email-footer a:hover {{ text-decoration: underline; }}

        /* Logo gradient animation effect (static fallback for email) */
        .logo-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 28px; font-weight: 600; letter-spacing: -0.5px; }}
        .logo-dot {{ color: #00f5ff; }}

        /* Button styles */
        .btn-primary {{ display: inline-block; background: linear-gradient(135deg, #00f5ff 0%, #0891b2 100%); color: #0a0a0f; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; }}
        .btn-secondary {{ display: inline-block; background-color: #1e1e23; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; }}
        .btn-outline {{ display: inline-block; background-color: transparent; border: 1px solid #e5e7eb; color: #1e1e23; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; }}

        /* Card styles */
        .info-card {{ background-color: #f3f4f6; border-left: 4px solid #00f5ff; border-radius: 8px; padding: 20px; margin: 24px 0; }}
        .warning-card {{ background-color: #fef3c7; border-left: 4px solid #fbbf24; border-radius: 8px; padding: 20px; margin: 24px 0; }}
        .error-card {{ background-color: #fee2e2; border-left: 4px solid #ef4444; border-radius: 8px; padding: 20px; margin: 24px 0; }}
        .success-card {{ background-color: #d1fae5; border-left: 4px solid #22c55e; border-radius: 8px; padding: 20px; margin: 24px 0; }}

        /* Typography */
        h1 {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 24px; font-weight: 600; margin: 0 0 16px 0; color: #1e1e23; }}
        h2 {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 20px; font-weight: 600; margin: 0 0 12px 0; color: #1e1e23; }}
        h3 {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; font-weight: 600; margin: 0 0 8px 0; color: #1e1e23; }}
        p {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; line-height: 1.6; margin: 0 0 16px 0; color: #374151; }}

        /* Stats cards */
        .stats-container {{ display: flex; gap: 12px; margin: 24px 0; }}
        .stat-card {{ flex: 1; background-color: #f3f4f6; padding: 20px; border-radius: 12px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: 700; }}
        .stat-label {{ font-size: 13px; color: #6b7280; margin-top: 4px; }}

        /* Table styles */
        .email-table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
        .email-table th {{ padding: 12px 8px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; border-bottom: 2px solid #e5e7eb; }}
        .email-table td {{ padding: 12px 8px; border-bottom: 1px solid #f3f4f6; }}
        .email-table tr:last-child td {{ border-bottom: none; }}

        /* Dark mode support via media query */
        @media (prefers-color-scheme: dark) {{
            .email-wrapper {{ background-color: #0a0a0f !important; }}
            .email-card {{ background-color: #14141e !important; }}
            .email-header {{ border-bottom-color: rgba(255,255,255,0.1) !important; }}
            .email-content {{ color: #f5f5fa !important; }}
            .email-footer {{ border-top-color: rgba(255,255,255,0.1) !important; color: #6b7280 !important; }}
            .email-footer a {{ color: #6b7280 !important; }}

            h1, h2, h3 {{ color: #f5f5fa !important; }}
            p {{ color: #d1d5db !important; }}

            .btn-secondary {{ background-color: #27272a !important; border-color: rgba(255,255,255,0.1) !important; }}
            .btn-outline {{ background-color: transparent !important; border-color: rgba(255,255,255,0.2) !important; color: #f5f5fa !important; }}

            .info-card {{ background-color: rgba(0, 245, 255, 0.1) !important; border-left-color: #00f5ff !important; }}
            .warning-card {{ background-color: rgba(251, 191, 36, 0.15) !important; border-left-color: #fbbf24 !important; }}
            .error-card {{ background-color: rgba(239, 68, 68, 0.15) !important; border-left-color: #ef4444 !important; }}
            .success-card {{ background-color: rgba(34, 197, 94, 0.15) !important; border-left-color: #22c55e !important; }}

            .stats-container {{ gap: 12px; }}
            .stat-card {{ background-color: #1e1e2e !important; }}
            .stat-label {{ color: #9696aa !important; }}

            .email-table th {{ color: #9696aa !important; border-bottom-color: rgba(255,255,255,0.1) !important; }}
            .email-table td {{ border-bottom-color: rgba(255,255,255,0.05) !important; color: #f5f5fa !important; }}
        }}

        /* Responsive styles */
        @media screen and (max-width: 620px) {{
            .email-container {{ max-width: 100% !important; }}
            .email-header, .email-content, .email-footer {{ padding: 20px 16px !important; }}
            .stats-container {{ flex-direction: column; }}
            .stat-card {{ margin-bottom: 8px; }}
            .btn-primary, .btn-secondary, .btn-outline {{ display: block !important; width: 100% !important; box-sizing: border-box; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; width: 100%; background-color: #f8f8fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <!-- Preview text for inbox preview -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        {preview_text} ‎
    </div>

    <div class="email-wrapper">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="email-container" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                        <!-- Main Card -->
                        <tr>
                            <td class="email-card">
                                <!-- Logo/Header -->
                                <div class="email-header">
                                    <a href="{BASE_URL}" style="text-decoration: none;">
                                        <span class="logo-text">
                                            Chronos<span class="logo-dot">.</span>
                                        </span>
                                    </a>
                                </div>

                                <!-- Content -->
                                <div class="email-content">
                                    {content}
                                </div>

                                <!-- Footer -->
                                <div class="email-footer">
                                    <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 12px;">
                                        You received this email because you have notifications enabled in Chronos.
                                    </p>
                                    <p style="margin: 8px 0;">
                                        <a href="{BASE_URL}/settings/notifications" style="color: #6b7280;">Manage Notification Settings</a>
                                    </p>
                                    {unsubscribe_html}
                                    <p style="margin: 16px 0 0 0; color: #9ca3af; font-size: 11px;">
                                        © {datetime.now().year} Chronos. All rights reserved.
                                    </p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>'''

    @staticmethod
    def task_due(
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for task due reminder with production design.

        [From]: spec.md FR-004 - TASK_DUE notification
        [Task]: T046 - Add unsubscribe token
        [Updated]: Production design with warning card styling
        """
        content = f'''
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <tr>
                    <td style="padding-bottom: 24px;">
                        <span style="font-size: 32px;">⏰</span>
                        <h2 style="margin: 12px 0 8px 0; color: #fbbf24;">Task Due Soon</h2>
                        <p style="margin: 0; color: #374151;">Your task is coming up. Here are the details:</p>
                    </td>
                </tr>
            </table>

            <div class="warning-card">
                <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td>
                            <h3 style="margin: 0 0 8px 0; color: #1e1e23;">{task_title}</h3>
                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Due: {due_date}</p>
                        </td>
                    </tr>
                </table>
            </div>

            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}{task_url}" class="btn-primary" style="color: #0a0a0f; text-decoration: none;">
                            View Task →
                        </a>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"⏰ Task due: {task_title}", unsubscribe_token)

    @staticmethod
    def task_overdue(
        task_title: str,
        due_date: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for overdue task with production design.

        [From]: spec.md FR-004 - TASK_OVERDUE notification
        [Task]: T046 - Add unsubscribe token
        [Updated]: Production design with error card styling
        """
        content = f'''
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <tr>
                    <td style="padding-bottom: 24px;">
                        <span style="font-size: 32px;">⚠️</span>
                        <h2 style="margin: 12px 0 8px 0; color: #ef4444;">Task Overdue</h2>
                        <p style="margin: 0; color: #374151;">This task is now overdue. Please take action:</p>
                    </td>
                </tr>
            </table>

            <div class="error-card">
                <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td>
                            <h3 style="margin: 0 0 8px 0; color: #1e1e23;">{task_title}</h3>
                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Was due: {due_date}</p>
                        </td>
                    </tr>
                </table>
            </div>

            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}{task_url}" class="btn-primary" style="color: #0a0a0f; text-decoration: none;">
                            View Task →
                        </a>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"⚠️ Overdue: {task_title}", unsubscribe_token)

    @staticmethod
    def task_assigned(
        task_title: str,
        assigned_by: str,
        task_url: str,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Email template for task assignment with production design.

        [From]: spec.md FR-004 - TASK_ASSIGNED notification
        [Task]: T046 - Add unsubscribe token
        [Updated]: Production design with success/info card styling
        """
        content = f'''
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <tr>
                    <td style="padding-bottom: 24px;">
                        <span style="font-size: 32px;">✨</span>
                        <h2 style="margin: 12px 0 8px 0; color: #00f5ff;">New Task Assigned</h2>
                        <p style="margin: 0; color: #374151;">
                            <strong>{assigned_by}</strong> assigned you a new task:
                        </p>
                    </td>
                </tr>
            </table>

            <div class="info-card">
                <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td>
                            <h3 style="margin: 0; color: #1e1e23;">{task_title}</h3>
                        </td>
                    </tr>
                </table>
            </div>

            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}{task_url}" class="btn-primary" style="color: #0a0a0f; text-decoration: none;">
                            View Task →
                        </a>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"✨ Assigned: {task_title}", unsubscribe_token)

    @staticmethod
    def daily_digest(tasks: list[dict[str, Any]]) -> str:
        """Email template for daily task digest with production design.

        [From]: spec.md FR-022 - Email digest frequency
        [Updated]: Production design with styled table
        """
        task_rows = ""
        for task in tasks[:10]:  # Limit to 10 tasks
            status_emoji = "✓" if task.get("completed") else "○"
            status_color = "#22c55e" if task.get("completed") else "#6b7280"
            task_rows += f"""
                <tr>
                    <td style="padding: 12px 8px; text-align: center;">{status_emoji}</td>
                    <td style="padding: 12px 8px;">{task.get('title', 'Untitled')}</td>
                    <td style="padding: 12px 8px; color: #6b7280; font-size: 14px;">{task.get('due_date', 'No due date')}</td>
                </tr>
            """

        task_count = len(tasks)
        content = f'''
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <tr>
                    <td style="padding-bottom: 24px;">
                        <span style="font-size: 32px;">📋</span>
                        <h2 style="margin: 12px 0 8px 0;">Your Daily Task Digest</h2>
                        <p style="margin: 0; color: #374151;">You have <strong>{task_count} task{'' if task_count == 1 else 's'}</strong> for today. Here's your overview:</p>
                    </td>
                </tr>
            </table>

            <table class="email-table" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <thead>
                    <tr>
                        <th style="text-align: center; width: 40px;">Status</th>
                        <th>Task</th>
                        <th style="width: 100px;">Due Date</th>
                    </tr>
                </thead>
                <tbody>
                    {task_rows}
                </tbody>
            </table>

            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}/dashboard" class="btn-primary" style="color: #0a0a0f; text-decoration: none;">
                            View All Tasks →
                        </a>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"📋 Your daily digest - {task_count} tasks")

    @staticmethod
    def weekly_summary(stats: dict[str, Any]) -> str:
        """Email template for weekly summary with production design.

        [From]: spec.md FR-022 - Email digest frequency
        [Updated]: Production design with stat cards
        """
        completed = stats.get('completed', 0)
        pending = stats.get('pending', 0)
        overdue = stats.get('overdue', 0)

        content = f'''
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                <tr>
                    <td style="padding-bottom: 24px;">
                        <span style="font-size: 32px;">📊</span>
                        <h2 style="margin: 12px 0 8px 0;">Your Weekly Summary</h2>
                        <p style="margin: 0; color: #374151;">Here's how you did this week:</p>
                    </td>
                </tr>
            </table>

            <div class="stats-container">
                <table class="stat-card" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td align="center">
                            <div class="stat-number" style="color: #22c55e;">{completed}</div>
                            <div class="stat-label">Completed</div>
                        </td>
                    </tr>
                </table>
                <table class="stat-card" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td align="center">
                            <div class="stat-number" style="color: #fbbf24;">{pending}</div>
                            <div class="stat-label">Still Pending</div>
                        </td>
                    </tr>
                </table>
                <table class="stat-card" cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td align="center">
                            <div class="stat-number" style="color: #ef4444;">{overdue}</div>
                            <div class="stat-label">Overdue</div>
                        </td>
                    </tr>
                </table>
            </div>

            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}/dashboard" class="btn-primary" style="color: #0a0a0f; text-decoration: none;">
                            View Dashboard →
                        </a>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"📊 Your weekly summary - {completed} completed")

    @staticmethod
    def welcome(
        user_email: str,
        user_name: str | None = None,
        unsubscribe_token: str | None = None,
    ) -> str:
        """Production welcome email template with onboarding content.

        [Task]: Welcome email for new users
        [Updated]: Production design with feature showcase
        """
        display_name = user_name or user_email.split('@')[0]

        content = f'''
            <!-- Hero Section -->
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="text-align: center; padding: 20px 0;">
                <tr>
                    <td>
                        <span style="font-size: 48px;">◈</span>
                        <h1 style="margin: 16px 0 8px 0;">Welcome to Chronos<span style="color: #00f5ff;">.</span></h1>
                        <p style="margin: 0; color: #374151; font-size: 17px;">
                            Hi <strong>{display_name}</strong> — your personal task management companion awaits.
                        </p>
                    </td>
                </tr>
            </table>

            <!-- Feature Card -->
            <div class="info-card" style="background-color: #f3f4f6; border-left: none; border-radius: 12px; padding: 28px;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                    <tr>
                        <td>
                            <h3 style="margin: 0 0 12px 0; color: #1e1e23; text-align: center;">✨ Get Started with Chronos</h3>
                            <p style="margin: 0 0 24px 0; color: #6b7280; text-align: center;">
                                Organize your life with powerful task management features designed for productivity.
                            </p>

                            <!-- Feature List -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top;">
                                                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #00f5ff 0%, #0891b2 100%); border-radius: 8px; text-align: center; line-height: 36px; font-size: 18px;">✓</div>
                                                </td>
                                                <td style="vertical-align: top; padding-left: 12px;">
                                                    <h4 style="margin: 0 0 4px 0; color: #1e1e23;">Create Tasks</h4>
                                                    <p style="margin: 0; font-size: 14px; color: #6b7280;">Add tasks with due dates, priorities, and custom tags</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top;">
                                                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #00f5ff 0%, #0891b2 100%); border-radius: 8px; text-align: center; line-height: 36px; font-size: 18px;">⏰</div>
                                                </td>
                                                <td style="vertical-align: top; padding-left: 12px;">
                                                    <h4 style="margin: 0 0 4px 0; color: #1e1e23;">Smart Reminders</h4>
                                                    <p style="margin: 0; font-size: 14px; color: #6b7280;">Get email and push notifications for due tasks</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top;">
                                                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #00f5ff 0%, #0891b2 100%); border-radius: 8px; text-align: center; line-height: 36px; font-size: 18px;">📊</div>
                                                </td>
                                                <td style="vertical-align: top; padding-left: 12px;">
                                                    <h4 style="margin: 0 0 4px 0; color: #1e1e23;">Track Progress</h4>
                                                    <p style="margin: 0; font-size: 14px; color: #6b7280;">View daily digests and weekly summaries</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0 0 0;">
                                        <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation">
                                            <tr>
                                                <td style="width: 40px; vertical-align: top;">
                                                    <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #00f5ff 0%, #0891b2 100%); border-radius: 8px; text-align: center; line-height: 36px; font-size: 18px;">🔔</div>
                                                </td>
                                                <td style="vertical-align: top; padding-left: 12px;">
                                                    <h4 style="margin: 0 0 4px 0; color: #1e1e23;">Stay Notified</h4>
                                                    <p style="margin: 0; font-size: 14px; color: #6b7280;">Real-time updates via push and email notifications</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- CTA Button -->
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px;">
                <tr>
                    <td align="center">
                        <a href="{BASE_URL}/dashboard" class="btn-primary" style="color: #0a0a0f; text-decoration: none; padding: 16px 32px; font-size: 16px;">
                            Create Your First Task →
                        </a>
                    </td>
                </tr>
            </table>

            <!-- Support Link -->
            <table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin-top: 32px; text-align: center;">
                <tr>
                    <td>
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">
                            Questions or feedback? <a href="mailto:support@chronostodo.com" style="color: #00f5ff; text-decoration: none;">Contact Support</a>
                        </p>
                    </td>
                </tr>
            </table>
        '''
        return EmailTemplates.base_template(content, f"Welcome to Chronos, {display_name}!", unsubscribe_token)


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
