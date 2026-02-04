"""
Chat API routes for Phase III AI Chatbot.

Provides endpoints for:
- POST /api/chat - Send chat message with streaming response
- POST /api/chat/transcribe - Transcribe audio via Whisper
- GET /api/conversations - List user's conversations
- GET /api/conversations/{id} - Get conversation with messages
- DELETE /api/conversations/{id} - Delete conversation

Per spec.md chat-api.yaml contract.
"""

import os
import uuid
import tempfile
import aiofiles
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sse_starlette.sse import EventSourceResponse
from sqlmodel import Session

from app.ai.models import (
    Conversation,
    ConversationPublic,
    ConversationCreate,
    Message,
    MessagePublic,
    MessageRole,
    AgentHandoff,
    LanguagePreference,
)
from app.ai.services import (
    RunnerService,
    StreamEventType,
    convert_to_sse_format,
    OpenAIService,
    initialize_qdrant,
)
from app.ai.agents.context import TodoContext
from app.ai.utils.logging import get_logger, bind_correlation_id, sanitize_log_data
from app.ai.utils.language import detect_language, should_respond_in_urdu
from app.ai.utils.sanitize import sanitize_user_input, should_block_input, strip_system_instructions
from app.ai.mcp.tools import TaskTools
from app.db import get_session
from app.simple_auth import get_current_user_id

# =============================================================================
# Conversation Lock Manager (T125: Concurrent message queuing)
# =============================================================================

import asyncio
from collections import defaultdict

class ConversationLockManager:
    """
    Manages per-conversation locks to ensure sequential processing.

    [Task]: T125 - Concurrent message queuing per conversation

    Prevents race conditions when multiple messages are sent quickly
    to the same conversation. Each conversation has its own queue,
    and messages are processed sequentially.
    """

    def __init__(self):
        # Map of conversation_id -> asyncio.Lock
        self._locks: dict[str, asyncio.Lock] = {}
        # Map of conversation_id -> queue of waiting tasks
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._global_lock = asyncio.Lock()

    async def acquire_lock(self, conversation_id: str) -> asyncio.Lock:
        """Acquire or create a lock for the given conversation."""
        async with self._global_lock:
            if conversation_id not in self._locks:
                self._locks[conversation_id] = asyncio.Lock()
            return self._locks[conversation_id]

    def cleanup_lock(self, conversation_id: str) -> None:
        """Clean up lock for a conversation (call after processing completes)."""
        # Keep lock around for potential reuse, but could clean if needed
        pass

# Global lock manager instance
conversation_lock_manager = ConversationLockManager()

# =============================================================================
# Router
# =============================================================================

router = APIRouter(tags=["Chat"])
logger = get_logger("api", "ChatRoutes")

# =============================================================================
# Configuration
# =============================================================================

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "5000"))
MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "25"))
MAX_AUDIO_DURATION_SECONDS = int(os.getenv("MAX_AUDIO_DURATION_SECONDS", "30"))
AUDIO_MIME_TYPES = [
    "audio/mpeg",  # MP3
    "audio/mp4",  # MP4
    "audio/mpeg",  # MPEG
    "audio/mpga",  # MPGA
    "audio/m4a",  # M4A
    "audio/wav",  # WAV
    "audio/webm",  # WEBM
]


# =============================================================================
# Schemas
# =============================================================================

class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str
    conversation_id: str | None = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Add a task to buy groceries tomorrow at 5pm",
                    "conversation_id": None,
                }
            ]
        }


class ChatEvent(BaseModel):
    """Server-Sent Event for streaming."""

    event: str
    data: dict[str, Any]
    id: str | None = None
    retry: int | None = None


class TranscriptionResponse(BaseModel):
    """Response schema for transcription endpoint."""

    text: str
    language: str
    duration: float | None = None


# =============================================================================
# Endpoints
# =============================================================================

@router.post("")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Send chat message and receive streaming response.

    Per spec.md FR-001 through FR-010:
    - Streaming responses via SSE for token-by-token delivery
    - Creates or resumes conversation
    - AI can invoke MCP tools for task operations
    - All events logged with correlation ID

    Args:
        request: Chat request with message and optional conversation_id
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Streaming SSE response with chat events

    Example:
        POST /api/chat
        {
            "message": "Add a task to buy groceries",
            "conversation_id": null
        }

        Response (SSE):
        event: message_start
        data: {"conversation_id": "...", "message_id": "..."}

        event: token
        data: {"content": "I"}

        event: token
        data: {"content": "'ll"}

        event: message_done
        data: {"final_output": "I'll add that task for you."}
    """
    # Generate correlation ID for this request
    correlation_id = bind_correlation_id()["correlation_id"]

    logger.info(
        "Chat request received",
        event_type="request_start",
        endpoint="/api/chat",
        user_id=user_id,
        conversation_id=request.conversation_id,
        message_length=len(request.message),
    )

    # Validate message length
    if len(request.message) > MAX_MESSAGE_LENGTH:
        logger.warning(
            "Message too long",
            user_id=user_id,
            message_length=len(request.message),
            max_length=MAX_MESSAGE_LENGTH,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message too long. Maximum is {MAX_MESSAGE_LENGTH} characters.",
        )

    # T126: Sanitize user input to prevent prompt injection (FR-094)
    sanitization_result = sanitize_user_input(request.message, max_length=MAX_MESSAGE_LENGTH)

    # Block input if it appears to be a prompt injection attack
    if should_block_input(sanitization_result):
        logger.warning(
            "Input blocked due to prompt injection detection",
            user_id=user_id,
            severity=sanitization_result["injection_detection"]["severity"],
            score=sanitization_result["injection_detection"]["score"],
            patterns=sanitization_result["injection_detection"]["patterns"],
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your message appears to contain suspicious content. Please rephrase your request.",
        )

    # Use sanitized message for processing
    sanitized_message = sanitization_result["text"]

    # Get or create conversation
    if request.conversation_id:
        # Resume existing conversation
        statement = select(Conversation).where(
            Conversation.id == uuid.UUID(request.conversation_id),
            Conversation.user_id == user_id,
        )
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        correlation_id=correlation_id,
        role=MessageRole.USER,
        content=sanitized_message,  # Use sanitized message
    )
    session.add(user_message)
    await session.commit()

    # Detect language
    language_detection = detect_language(sanitized_message)  # Use sanitized message
    logger.debug(
        "Language detected",
        language=language_detection.language.value,
        confidence=language_detection.confidence,
    )

    async def event_generator():
        """Generate SSE events for chat response."""

        # Acquire conversation lock for sequential processing (T125)
        conv_lock = await conversation_lock_manager.acquire_lock(str(conversation.id))

        async with conv_lock:
            # Create TodoContext for agent execution
            context = TodoContext(
                user_id=user_id,
                conversation_id=str(conversation.id),
                correlation_id=correlation_id,
                language_preference=conversation.language_preference,
                session=session,
            )

            # Get conversation history for context
            # Exclude the current user message (already saved to DB)
            # to avoid duplicate when runner_service appends it
            from sqlalchemy import select
            msg_statement = (
                select(Message)
                .where(
                    Message.conversation_id == conversation.id,
                    Message.id != user_message.id,  # Exclude current message
                )
                .order_by(Message.created_at.asc())
                .limit(50)  # Last 50 messages for context
            )
            msg_result = await session.execute(msg_statement)
            history_messages = msg_result.scalars().all()

            # Build conversation history in OpenAI format
            # Include tool_calls for assistant messages to maintain context
            conversation_history = []
            for m in history_messages:
                msg_dict = {"role": m.role, "content": m.content}
                # Include tool_calls for assistant messages (important for context)
                if m.role == MessageRole.ASSISTANT and m.tool_calls:
                    msg_dict["tool_calls"] = m.tool_calls
                conversation_history.append(msg_dict)

            # Create Runner service
            runner_service = RunnerService(
                session=session,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

            # Track accumulated response for storage
            accumulated_response = []
            tool_calls_list = []
            handoffs_list = []

            try:
                # Stream agent response
                async for event in runner_service.stream_chat(
                    user_message=sanitized_message,  # Use sanitized message
                    context=context,
                    conversation_history=conversation_history,
                ):
                    # Convert to SSE format and yield
                    sse_event = convert_to_sse_format(event)

                    # Track data for storage
                    if event.event == StreamEventType.TOKEN:
                        accumulated_response.append(event.data.get("content", ""))
                    elif event.event == StreamEventType.TOOL_CALL:
                        tool_calls_list.append(event.data)
                    elif event.event == StreamEventType.AGENT_HANDOFF:
                        handoffs_list.append(event.data)

                    yield sse_event

                # Get final result
                result = runner_service.get_result()
                final_output = result.final_output if result else ""

                # T126: Strip any potential system instruction leaks from AI response
                final_output = strip_system_instructions(final_output)

                # Create assistant message
                if final_output:
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        correlation_id=correlation_id,
                        role=MessageRole.ASSISTANT,
                        content=final_output,
                        tool_calls=tool_calls_list if tool_calls_list else None,
                    )
                    session.add(assistant_message)

                    # Update conversation
                    conversation.message_count += 2
                    conversation.updated_at = datetime.utcnow()
                    await session.commit()

                    # Log handoffs if any (T109, T110: Handoff tracking and storage)
                    if handoffs_list:
                        for handoff in handoffs_list:
                            # Capture context snapshot for debugging (LOG-033)
                            context_snapshot = {
                                "user_id": user_id,
                                "conversation_id": str(conversation.id),
                                "correlation_id": correlation_id,
                                "timestamp": datetime.utcnow().isoformat(),
                                "message_count": conversation.message_count,
                            }
                            handoff_record = AgentHandoff(
                                conversation_id=conversation.id,
                                from_agent=handoff.get("from_agent", ""),
                                to_agent=handoff.get("to_agent", ""),
                                reason=handoff.get("reason", "Agent handoff during conversation"),
                                context_snapshot=context_snapshot,
                                success=True,
                            )
                            session.add(handoff_record)
                        await session.commit()

                    logger.info(
                        "Chat response completed",
                        event_type="request_end",
                        user_id=user_id,
                        conversation_id=str(conversation.id),
                        agent_name=result.agent_name if result else "unknown",
                        tool_calls_count=len(tool_calls_list),
                        handoffs_count=len(handoffs_list),
                    )

            except Exception as e:
                # T112: Handoff error handling - store failed handoffs for audit
                if handoffs_list:
                    for handoff in handoffs_list:
                        try:
                            context_snapshot = {
                                "user_id": user_id,
                                "conversation_id": str(conversation.id),
                                "correlation_id": correlation_id,
                                "timestamp": datetime.utcnow().isoformat(),
                                "error": str(e),
                            }
                            failed_handoff = AgentHandoff(
                                conversation_id=conversation.id,
                                from_agent=handoff.get("from_agent", ""),
                                to_agent=handoff.get("to_agent", ""),
                                reason=handoff.get("reason", "Agent handoff failed"),
                                context_snapshot=context_snapshot,
                                success=False,
                                error_message=f"{type(e).__name__}: {str(e)}",
                            )
                            session.add(failed_handoff)
                        except Exception:
                            pass  # Don't fail error handling due to handoff storage
                    try:
                        await session.commit()
                    except Exception:
                        pass  # Handoff storage is best-effort

                logger.error(
                    "Chat streaming error",
                    event_type="stream_error",
                    user_id=user_id,
                    conversation_id=str(conversation.id),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    handoffs_count=len(handoffs_list),
                )

                # Send error event
                yield {
                    "event": "error",
                    "data": {
                        "error": type(e).__name__,
                        "message": "Sorry, I encountered an error. Please try again.",
                    },
                }

    return EventSourceResponse(event_generator())


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str | None = None,
    user_id: str = Depends(get_current_user_id),
) -> TranscriptionResponse:
    """
    Transcribe audio file using OpenAI Whisper API.

    Per spec.md FR-052 through FR-061:
    - Supports mp3, mp4, mpeg, mpga, m4a, wav, webm formats
    - Max file size: 25 MB
    - Auto-detects language
    - Returns transcribed text as UTF-8 (supports Urdu)

    Args:
        file: Audio file
        language: Optional ISO-639-1 language code
        user_id: Authenticated user ID

    Returns:
        TranscriptionResponse with text, language, duration

    Example:
        POST /api/chat/transcribe
        Content-Type: multipart/form-data

        {
            "text": "Add a task to buy groceries",
            "language": "en",
            "duration": 3.2
        }
    """
    correlation_id = bind_correlation_id()[0]

    logger.info(
        "Transcription request received",
        event_type="request_start",
        endpoint="/api/chat/transcribe",
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
    )

    # Validate file type
    if file.content_type not in AUDIO_MIME_TYPES:
        logger.warning(
            "Unsupported audio format",
            user_id=user_id,
            content_type=file.content_type,
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Audio format not supported. Please use MP3, M4A, or WAV.",
        )

    # Read file content
    content = await file.read()

    # Check file size (convert MB to bytes)
    max_size = MAX_AUDIO_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        logger.warning(
            "Audio file too large",
            user_id=user_id,
            file_size=len(content),
            max_size=max_size,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file is too large. Maximum is {MAX_AUDIO_SIZE_MB} MB.",
        )

    # Create temporary file for Whisper API
    try:
        # Save uploaded file to temporary file
        async with aiofiles.tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=f".{file.filename.split('.')[-1] if '.' in file.filename else 'webm'}",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            await temp_file.write(content)

        logger.info(
            "Transcribing audio file",
            user_id=user_id,
            temp_file_path=temp_path,
            file_size=len(content),
            language=language or "auto",
        )

        # Call OpenAI Whisper API via OpenAIService
        openai_service = OpenAIService()
        transcription = await openai_service.transcribe_audio(
            audio_file_path=temp_path,
            language=language,  # None for auto-detection
        )

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass

        logger.info(
            "Transcription completed",
            user_id=user_id,
            detected_language=transcription.language,
            duration=transcription.duration,
            text_length=len(transcription.text),
        )

        return TranscriptionResponse(
            text=transcription.text,
            language=transcription.language,
            duration=transcription.duration,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        logger.error(
            "Transcription failed",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio. Please try again or use text input.",
        )


@router.get("/conversations")
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    List conversations for the authenticated user.

    Args:
        limit: Maximum results (default 50, max 100)
        offset: Pagination offset
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Dict with conversations list and total count

    Example:
        GET /api/chat/conversations?limit=10&offset=0

        {
            "conversations": [...],
            "total": 42
        }
    """
    # Limit validation
    limit = min(limit, 100)

    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(statement)
    conversations = result.scalars().all()

    # Get total count
    count_statement = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
    count_result = await session.execute(count_statement)
    total = count_result.scalar()

    return {
        "conversations": [
            ConversationPublic(
                id=c.id,
                user_id=c.user_id,
                title=c.title,
                language_preference=c.language_preference,
                message_count=c.message_count,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ],
        "total": total,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Get conversation with paginated messages.

    Args:
        conversation_id: Conversation UUID
        limit: Maximum messages to return (default 50, max 100)
        offset: Pagination offset for messages
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Dict with conversation, messages, and pagination metadata

    Example:
        GET /api/chat/conversations/123e4567-e89b-12d3-a456-426614174000?limit=20&offset=0

        {
            "conversation": {...},
            "messages": [...],
            "pagination": {
                "limit": 20,
                "offset": 0,
                "total": 45,
                "has_more": true
            }
        }
    """
    # Enforce max limit (T118: pagination support)
    limit = min(limit, 100)

    # Validate conversation_id is a valid UUID
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID format: {conversation_id}",
        )

    # Get conversation
    conv_statement = select(Conversation).where(
        Conversation.id == conversation_uuid,
        Conversation.user_id == user_id,
    )
    conv_result = await session.execute(conv_statement)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get total message count
    from sqlalchemy import func
    count_statement = (
        select(func.count())
        .where(Message.conversation_id == conversation.id)
    )
    total_result = await session.execute(count_statement)
    total_messages = total_result.scalar_one()

    # Get paginated messages (oldest first for proper scrolling)
    msg_statement = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    msg_result = await session.execute(msg_statement)
    messages = msg_result.scalars().all()

    return {
        "conversation": ConversationPublic.model_validate(conversation),
        "messages": [
            MessagePublic(
                id=m.id,
                conversation_id=m.conversation_id,
                correlation_id=m.correlation_id,
                role=m.role,
                content=m.content,
                tool_calls=m.tool_calls or [],
                created_at=m.created_at,
            )
            for m in messages
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_messages,
            "has_more": offset + limit < total_messages,
        },
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation UUID
        user_id: Authenticated user ID
        session: Database session

    Returns:
        204 No Content on success

    Example:
        DELETE /api/chat/conversations/123e4567-e89b-12d3-a456-426614174000
    """
    # Validate conversation_id is a valid UUID
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID format: {conversation_id}",
        )

    # Get conversation (verifies ownership)
    conv_statement = select(Conversation).where(
        Conversation.id == conversation_uuid,
        Conversation.user_id == user_id,
    )
    conv_result = await session.execute(conv_statement)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Delete (messages will cascade)
    await session.delete(conversation)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
