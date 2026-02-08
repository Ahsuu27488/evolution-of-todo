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

import json
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
    MessageType,
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
from app.ai.agents.context import (
    TodoContext,
    create_context_with_user_profile,
)
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
    language_preference: LanguagePreference | None = None  # Per-message language mode
    message_type: MessageType | None = None  # Type of message (text/voice) for UI display

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Add a task to buy groceries tomorrow at 5pm",
                    "conversation_id": None,
                    "language_preference": "auto",
                    "message_type": "text",
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
    language: str | None = None  # Whisper API doesn't return language by default
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
        message_type=request.message_type or MessageType.TEXT,  # Store message type for UI display
    )
    session.add(user_message)

    # Update conversation message_count immediately after saving user message
    # This ensures message_count is accurate even if streaming fails later
    conversation.message_count += 1
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    # Auto-generate conversation title
    # - Message 1: Generate AI-powered title immediately (always in English)
    try:
        if conversation.message_count == 1 and conversation.title == "New Chat":
            # First message - generate AI-powered title immediately
            # Build conversation summary from the user's first message
            conversation_summary = f"User: {sanitized_message[:100]}"

            # Generate title using OpenAI
            openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
            generated_title = await openai_service.generate_title(conversation_summary)

            # Update conversation with generated title
            conversation.title = generated_title
            await session.commit()

            logger.info(
                "Generated AI title for first message",
                conversation_id=str(conversation.id),
                title=generated_title,
                message_count=conversation.message_count,
            )
    except Exception as e:
        # Title generation is best-effort - log but don't fail the request
        logger.warning(
            "Failed to generate conversation title",
            conversation_id=str(conversation.id),
            error=str(e),
        )

    # Detect language from input message
    language_detection = detect_language(sanitized_message)  # Use sanitized message
    logger.debug(
        "Language detected from input",
        language=language_detection.language.value,
        confidence=language_detection.confidence,
    )

    # Determine response language based on mode and detection
    # - auto: respond in detected language (English → English, Urdu → Urdu)
    # - en: always respond in English, regardless of input
    # - ur: always respond in Urdu, regardless of input
    request_mode = request.language_preference or conversation.language_preference

    if request_mode == LanguagePreference.AUTO:
        # Auto mode: respond in detected language
        response_language = language_detection.language
    elif request_mode == LanguagePreference.EN:
        # English mode: always respond in English
        response_language = language_detection.language  # Keep detection for logging
    elif request_mode == LanguagePreference.UR:
        # Urdu mode: always respond in Urdu
        response_language = language_detection.language  # Keep detection for logging
    else:
        # Fallback to detected language
        response_language = language_detection.language

    logger.info(
        "Language mode determined",
        request_mode=request_mode.value if request_mode else "auto",
        detected_language=language_detection.language.value,
        response_language=response_language.value,
    )

    async def event_generator():
        """Generate SSE events for chat response."""

        # Acquire conversation lock for sequential processing (T125)
        conv_lock = await conversation_lock_manager.acquire_lock(str(conversation.id))

        async with conv_lock:
            # Create TodoContext for agent execution with user profile
            # Include current date so agent knows what "today" is (fixes "tomorrow" parsing)
            # Include user profile for personalized responses (using user's name)
            context = await create_context_with_user_profile(
                user_id=user_id,
                conversation_id=str(conversation.id),
                correlation_id=correlation_id,
                session=session,
                language_preference=request_mode.value if request_mode else conversation.language_preference.value,
                timezone=getattr(conversation, "timezone", "UTC"),
                current_date=datetime.utcnow().date(),  # Agent needs to know current date
            )

            # Set response language based on detection
            context.response_language = response_language.value

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
            # IMPORTANT: OpenAI's API only supports these roles: 'user', 'assistant', 'system', 'developer'
            # It does NOT support 'tool' role - tool messages are for frontend display only

            # First, add a system message with current date context
            # This fixes the bug where "tomorrow" parses to the model's birth date (e.g., 6-7-24)
            today = datetime.utcnow().date()
            system_content = f"Today's date is {today.strftime('%A, %B %d, %Y')}. "
            system_content += "Use this date as reference when parsing relative dates like 'tomorrow', 'next week', etc."

            # Add user profile context for personalized responses
            if context.user_display_name or context.user_first_name:
                user_name = context.user_display_name or context.user_first_name
                system_content += f"\n\nThe user's name is {user_name}. Use their name naturally in greetings and responses to make the conversation more personal and friendly."
                system_content += f"\nLanguage preference: {context.language_preference}."
                system_content += f"\nTimezone: {context.timezone}."

            system_message = {
                "role": "system",
                "content": system_content,
            }

            conversation_history = [system_message]

            for m in history_messages:
                # Only include user and assistant messages in conversation history
                # Skip tool role messages - they cause OpenAI API 400 errors
                if m.role in (MessageRole.USER, MessageRole.ASSISTANT):
                    msg_dict = {"role": m.role.value, "content": m.content}
                    # Note: Don't include tool_calls - OpenAI's Responses API (used by Agents SDK)
                    # doesn't support the legacy tool_calls format.
                    conversation_history.append(msg_dict)
                # TOOL messages are skipped - they're for frontend context only

            # Create Runner service
            runner_service = RunnerService(
                session=session,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

            # Track accumulated response for storage
            accumulated_response = []
            tool_calls_list = []
            tool_results_list = []  # Track tool results for conversation context
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
                    elif event.event == StreamEventType.TOOL_RESULT:
                        # Track tool results for conversation context (fixes agent memory)
                        tool_results_list.append(event.data)
                    elif event.event == StreamEventType.AGENT_HANDOFF:
                        handoffs_list.append(event.data)

                    yield sse_event

                # Get final result
                result = runner_service.get_result()
                final_output = result.final_output if result else ""

                # T126: Strip any potential system instruction leaks from AI response
                final_output = strip_system_instructions(final_output)

                # Create assistant message
                # Always save a response, even if empty (error case) - prevents dangling user messages
                response_to_save = final_output if final_output else "I'm sorry, I wasn't able to generate a response. Please try again."

                assistant_message = Message(
                    conversation_id=conversation.id,
                    correlation_id=correlation_id,
                    role=MessageRole.ASSISTANT,
                    content=response_to_save,
                    tool_calls=tool_calls_list if tool_calls_list else None,
                )
                # DEBUG: Log what's being stored
                logger.info(
                    f"[DEBUG] Saving assistant message: "
                    f"tool_calls_count={len(tool_calls_list) if tool_calls_list else 0}, "
                    f"tool_calls_data={tool_calls_list}"
                )
                session.add(assistant_message)

                # Update conversation (increment by 1 since user message was already counted)
                conversation.message_count += 1
                conversation.updated_at = datetime.utcnow()
                await session.commit()

                # Save tool results as messages for conversation context (fixes agent memory)
                # Tool results maintain context between requests so agent knows what happened
                if tool_results_list:
                    for tool_result in tool_results_list:
                        # Format tool result as JSON string for storage
                        result_content = json.dumps({
                            "tool": tool_result.get("tool", "unknown"),
                            "output": tool_result.get("output", ""),
                        })
                        tool_message = Message(
                            conversation_id=conversation.id,
                            correlation_id=correlation_id,
                            role=MessageRole.TOOL,  # New TOOL role for conversation context
                            content=result_content,
                        )
                        session.add(tool_message)
                        conversation.message_count += 1
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

                # Send error event with conversation_id so frontend can still track the conversation
                # This fixes the bug where errors cause new conversations to be created on each message
                yield {
                    "event": "error",
                    "data": {
                        "conversation_id": str(conversation.id),  # Always include so frontend can resume
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
    correlation_id = bind_correlation_id()["correlation_id"]

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

        # Transcription language handling:
        # - If language is specified, use it (en/ur)
        # - If not specified, let Whisper auto-detect (None)
        # This allows transcription to be independent of chat language mode
        transcription_language = language  # None = auto-detect

        # Language-specific prompts for Whisper
        # ONLY apply Urdu bias when language is explicitly Urdu to avoid
        # mis-transcribing English speech as Urdu/Hindi
        if transcription_language == "ur":
            # Urdu bias: Include Urdu script so Whisper knows to output Urdu
            # for Urdu speech, not Hindi/Devanagari (they sound identical)
            whisper_prompt = "اردو میں بولیں۔ آج کا دن اچھا ہے۔ Task. Add. Complete."
        elif transcription_language == "en":
            # English prompt: Helps with English spelling and formatting
            whisper_prompt = "The following is a transcription of an English audio recording. Task, add, complete, delete, update."
        else:
            # Auto-detect mode: No prompt bias - let Whisper decide naturally
            # This prevents English from being mis-identified as Urdu/Hindi
            whisper_prompt = None

        logger.info(
            "Transcribing audio file",
            user_id=user_id,
            temp_file_path=temp_path,
            file_size=len(content),
            language=transcription_language or "auto",
            prompt_used=bool(whisper_prompt),
        )

        # Call OpenAI Whisper API via OpenAIService
        openai_service = OpenAIService()
        transcription = await openai_service.transcribe_audio(
            audio_file_path=temp_path,
            language=transcription_language,
            prompt=whisper_prompt,
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
            ConversationPublic.model_validate(c)  # Uses camelCase aliases
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

    # Serialize conversation with camelCase aliases
    try:
        conversation_public = ConversationPublic.model_validate(conversation)
    except Exception as e:
        logger.error(f"Failed to validate conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serialize conversation: {str(e)}",
        )

    # Serialize messages with camelCase aliases
    messages_public = []
    for m in messages:
        try:
            # DEBUG: Log raw message data before validation
            logger.info(
                f"[DEBUG] Processing message: id={m.id}, role={m.role}, "
                f"content_length={len(m.content) if m.content else 0}, "
                f"tool_calls={type(m.tool_calls)}, tool_calls_value={m.tool_calls}"
            )
            # Convert SQLModel to dict first to trigger model_validator
            # Use snake_case keys to match model field names, then let Pydantic handle alias conversion
            message_dict = {
                "id": m.id,
                "conversation_id": str(m.conversation_id),
                "correlation_id": m.correlation_id,
                "role": m.role.value,
                "content": m.content,
                "message_type": m.message_type.value if hasattr(m, "message_type") else "text",  # Include message type
                "tool_calls": m.tool_calls if m.tool_calls else [],  # Use snake_case to trigger validator
                "created_at": m.created_at,
            }
            validated = MessagePublic.model_validate(message_dict)
            messages_public.append(validated)
            logger.info(f"[DEBUG] Successfully validated message {m.id}")
        except Exception as e:
            logger.error(
                f"[DEBUG] Failed to validate message {m.id}: {type(e).__name__}: {e}. "
                f"Message data: role={m.role.value}, content={m.content[:100] if m.content else 'None'}...",
                exc_info=True
            )
            # Skip problematic message rather than failing entire request
            continue

    # DEBUG: Log summary and sample message structure
    if messages_public:
        sample_msg = messages_public[0].model_dump(mode="json", by_alias=True)
        logger.info(
            f"[DEBUG] get_conversation summary: "
            f"conversation_id={conversation_id}, "
            f"total_messages_in_db={total_messages}, "
            f"messages_returned={len(messages_public)}, "
            f"sample_message_keys={list(sample_msg.keys())}, "
            f"has_createdAt={'createdAt' in sample_msg}, "
            f"has_created_at={'created_at' in sample_msg}"
        )

    # Explicitly serialize with by_alias=True to ensure camelCase keys
    return {
        "conversation": conversation_public.model_dump(mode="json", by_alias=True),
        "messages": [m.model_dump(mode="json", by_alias=True) for m in messages_public],
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
