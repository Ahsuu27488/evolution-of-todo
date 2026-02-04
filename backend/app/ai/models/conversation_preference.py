"""
Conversation Preference model for user chat settings.

Stores user-level preferences for the AI chatbot.
Per spec.md FR-049, FR-051, FR-060.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Column, Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


from .conversation import LanguagePreference


# =============================================================================
# Database Model
# =============================================================================

class ConversationPreference(SQLModel, table=True):
    """
    User chat preferences database model.

    Stores user-level preferences for the AI chatbot that persist
    across conversations.

    Per spec.md FR-049, FR-051, FR-060.

    Attributes:
        id: Unique preference record ID
        user_id: User ID from JWT 'sub' claim (unique per user)
        language: Language preference (en/ur/auto)
        voice_enabled: Whether voice input is enabled
        response_format: Preferred response format (text/voice)
        notifications_enabled: Whether chat notifications are enabled

    Note: user_id is unique (one record per user)
    """

    __tablename__ = "conversation_preferences"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(
        unique=True,  # One record per user
        index=True,
        description="User ID from JWT 'sub' claim",
    )
    language: LanguagePreference = Field(
        default=LanguagePreference.AUTO,
        sa_column=Column(
            SQLEnum(LanguagePreference, values_callable=lambda x: [e.value for e in x]),
            nullable=False
        ),
        description="Language preference (en/ur/auto)",
    )
    voice_enabled: bool = Field(
        default=True,
        description="Whether voice input is enabled",
    )
    response_format: str = Field(
        default="text",
        max_length=20,
        description="Preferred response format (text/voice)",
    )
    notifications_enabled: bool = Field(
        default=True,
        description="Whether chat notifications are enabled",
    )


# =============================================================================
# Pydantic Schemas
# =============================================================================

class ConversationPreferenceBase(BaseModel):
    """Base preference schema."""

    language: LanguagePreference = LanguagePreference.AUTO
    voice_enabled: bool = True
    response_format: str = "text"
    notifications_enabled: bool = True


class ConversationPreferenceCreate(ConversationPreferenceBase):
    """Schema for creating user preferences."""

    pass


class ConversationPreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""

    language: LanguagePreference | None = None
    voice_enabled: bool | None = None
    response_format: str | None = None
    notifications_enabled: bool | None = None


class ConversationPreferencePublic(ConversationPreferenceBase):
    """Schema for preference API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
