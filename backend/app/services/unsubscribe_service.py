"""Unsubscribe Service for email one-click unsubscribe.

[Task]: T046
[From]: spec.md FR-023 - One-click unsubscribe
[From]: RFC 8058 - Unsubscribe Post
"""

import logging
from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationPreference

logger = logging.getLogger(__name__)

# Unsubscribe token expiration (30 days)
UNSUBSCRIBE_EXPIRATION_HOURS = 24 * 30


class UnsubscribeService:
    """Service for email unsubscribe functionality.

    [Task]: T046
    [From]: spec.md FR-023

    Features:
    - JWT-based unsubscribe tokens
    - Per-type unsubscribe support
    - Token expiration (30 days)
    """

    @staticmethod
    def _get_secret() -> str:
        """Get the secret key for token signing."""
        import os

        # Use BETTER_AUTH_SECRET for consistency
        return os.getenv("BETTER_AUTH_SECRET", "")

    @staticmethod
    def generate_unsubscribe_token(
        user_id: str,
        notification_type: str | None = None,
    ) -> str:
        """Generate an unsubscribe token.

        [Task]: T046
        [From]: spec.md FR-023 - One-click unsubscribe

        Args:
            user_id: User ID to unsubscribe
            notification_type: Optional specific type to unsubscribe from.
                             If None, unsubscribes from all email notifications.

        Returns:
            JWT token for unsubscribe link
        """
        secret = UnsubscribeService._get_secret()

        payload = {
            "sub": user_id,
            "type": notification_type or "all",
            "purpose": "unsubscribe",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=UNSUBSCRIBE_EXPIRATION_HOURS),
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        return token

    @staticmethod
    def verify_unsubscribe_token(token: str) -> dict | None:
        """Verify an unsubscribe token.

        [Task]: T046
        [From]: spec.md FR-023 - Token verification

        Args:
            token: Unsubscribe token from email link

        Returns:
            Dict with user_id and notification_type if valid, None if invalid
        """
        secret = UnsubscribeService._get_secret()

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"require": ["sub", "type", "purpose"]},
            )

            # Verify this is an unsubscribe token
            if payload.get("purpose") != "unsubscribe":
                logger.warning(f"Invalid token purpose: {payload.get('purpose')}")
                return None

            return {
                "user_id": payload["sub"],
                "notification_type": payload.get("type"),
            }

        except JWTError as e:
            logger.warning(f"Invalid unsubscribe token: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error verifying unsubscribe token: {e}")
            return None

    @staticmethod
    async def unsubscribe_user(
        session: AsyncSession,
        user_id: str,
        notification_type: str | None = None,
    ) -> bool:
        """Unsubscribe a user from email notifications.

        [Task]: T046
        [From]: spec.md FR-023 - Update preferences

        Args:
            session: Database session
            user_id: User ID to unsubscribe
            notification_type: Optional specific type to unsubscribe from.
                             If None or "all", disables all email notifications.

        Returns:
            True if successful
        """
        from sqlalchemy import select, update

        if notification_type and notification_type != "all":
            # Disable specific notification type
            stmt = (
                update(NotificationPreference)
                .where(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.notification_type == notification_type,
                )
                .values(email_enabled=False)
            )
            await session.execute(stmt)
        else:
            # Disable all email notifications
            stmt = (
                update(NotificationPreference)
                .where(NotificationPreference.user_id == user_id)
                .values(email_enabled=False)
            )
            await session.execute(stmt)

        await session.commit()
        logger.info(f"Unsubscribed user {user_id} from {notification_type or 'all'} emails")
        return True
