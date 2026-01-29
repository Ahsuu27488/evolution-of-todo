#!/usr/bin/env python
"""Test script to send a production email template directly via Resend."""

import asyncio
import sys
import os
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import resend
from app.services.email_service import EmailTemplates

# Configure Resend
resend.api_key = os.getenv("RESEND_API_KEY", "")
BASE_URL = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
DEFAULT_SENDER = os.getenv(
    "EMAIL_FROM",
    "Chronos <noreply@mail.ahsandev.site>"
)

# Thread pool for running blocking Resend API calls
_email_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="resend_email")


def send_welcome_email_direct(to: str, user_name: str) -> dict:
    """Send welcome email directly via Resend without database."""
    from app.services.unsubscribe_service import UnsubscribeService

    # Generate unsubscribe token
    unsubscribe_token = UnsubscribeService.generate_unsubscribe_token(
        user_id="test_user",
        notification_type=None,
    )

    # Generate email HTML
    display_name = user_name or to.split('@')[0]
    subject = f"Welcome to Chronos, {display_name}!"
    html = EmailTemplates.welcome(to, user_name, unsubscribe_token)

    # Send via Resend
    params: resend.Emails.SendParams = {
        "from": DEFAULT_SENDER,
        "to": [to],
        "subject": subject,
        "html": html,
        "tags": [
            {"name": "type", "value": "test_welcome"},
            {"name": "env", "value": "test"},
        ],
    }

    try:
        loop = asyncio.get_event_loop()
        email = loop.run_in_executor(_email_executor, resend.Emails.send, params)
        result = asyncio.get_event_loop().run_until_complete(email)

        return {
            "success": True,
            "email_id": result.get("id"),
            "message_id": result.get("message_id"),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def main():
    test_email = "quadrogaming811@gmail.com"
    test_name = "Ahsan"

    print(f"Sending test email to: {test_email}")
    print(f"Using sender: {DEFAULT_SENDER}")
    print("=" * 50)

    if not resend.api_key:
        print("❌ RESEND_API_KEY not configured!")
        print("   Please set it in your .env file")
        return

    result = send_welcome_email_direct(test_email, test_name)

    if result.get("success"):
        print(f"✅ Email sent successfully!")
        print(f"   Email ID: {result.get('email_id')}")
        print(f"   Message ID: {result.get('message_id')}")
        print()
        print("📧 Check your inbox (and spam folder)!")
    else:
        print(f"❌ Failed to send email:")
        print(f"   Error: {result.get('error')}")


if __name__ == "__main__":
    main()
