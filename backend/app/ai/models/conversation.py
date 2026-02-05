"""
Conversation model for AI chatbot sessions.

Represents a chat session with message history, metadata,
and user preferences.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field as PydanticField
from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class LanguagePreference(str, Enum):
    """Supported language preferences for chat."""

    ENGLISH = "en"
    URDU = "ur"
    AUTO = "auto"  # Auto-detect from input


# =============================================================================
# Database Model
# =============================================================================

class Conversation(SQLModel, table=True):
    """
    Conversation database model.

    Represents a chat session between user and AI.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: User ID from JWT 'sub' claim
        title: Conversation title (first message initially, AI-generated at message 3)
        language_preference: User's language preference (en/ur/auto)
        message_count: Number of messages in conversation
        created_at: Conversation creation timestamp
        updated_at: Last activity timestamp

    Per spec.md FR-003 through FR-006.
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True),
    )
    user_id: str = Field(
        index=True,  # For fast user conversation lookup
        description="User ID from JWT 'sub' claim",
    )
    title: str = Field(
        default="New Chat",
        max_length=255,
        description="Conversation title (auto-generated or user-set)",
    )
    language_preference: LanguagePreference = Field(
        default=LanguagePreference.AUTO,
        sa_column=Column(
            SQLEnum(LanguagePreference, values_callable=lambda x: [e.value for e in x]),
            nullable=False
        ),
        description="User's language preference for this conversation",
    )
    message_count: int = Field(
        default=0,
        description="Number of messages in this conversation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
        description="Soft delete timestamp (T120: 90-day archive)",
    )


# =============================================================================
# Pydantic Schemas
# =============================================================================

class ConversationBase(BaseModel):
    """Base conversation schema."""

    title: Optional[str] = None
    language_preference: LanguagePreference = PydanticField(
        default=LanguagePreference.AUTO,
        alias="languagePreference",
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""

    pass


class ConversationPublic(ConversationBase):
    """Schema for conversation API responses.

    Uses camelCase aliases for JSON serialization to match frontend expectations.
    Python attributes remain snake_case per PEP 8.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Allow both snake_case and camelCase input
    )

    id: UUID
    user_id: str = PydanticField(alias="userId")
    message_count: int = PydanticField(alias="messageCount")
    created_at: datetime = PydanticField(alias="createdAt")
    updated_at: datetime = PydanticField(alias="updatedAt")


class ConversationList(BaseModel):
    """Schema for list of conversations."""

    conversations: list[ConversationPublic]
    total: int
