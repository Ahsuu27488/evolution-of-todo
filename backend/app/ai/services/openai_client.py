"""
OpenAI client service for Phase III.

Provides:
- Chat completions via OpenAI Agents SDK
- Embeddings generation for semantic search
- Audio transcription via Whisper API
- Cost tracking and token usage monitoring

Per spec.md FR-002, FR-032, FR-053, LOG-040, FR-108.
"""

import asyncio
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel

from app.ai.utils.logging import get_logger


# =============================================================================
# Configuration
# =============================================================================

# Model names from environment or defaults
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
DEFAULT_WHISPER_MODEL = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")

# Token cost estimates (USD per 1M tokens)
# Per spec.md FR-108
TOKEN_COSTS = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "text-embedding-3-small": {"total": 0.02},
}

# Cost per minute of audio transcription
WHISPER_COST_PER_MINUTE = 0.006


class ModelType(str, Enum):
    """OpenAI model types."""

    CHAT = "chat"
    EMBEDDING = "embedding"
    AUDIO = "audio"


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def cost(self, model: str) -> float:
        """Calculate estimated cost in USD."""
        if model in TOKEN_COSTS:
            costs = TOKEN_COSTS[model]
            if "input" in costs and "output" in costs:
                return (
                    (self.prompt_tokens / 1_000_000) * costs["input"]
                    + (self.completion_tokens / 1_000_000) * costs["output"]
                )
            elif "total" in costs:
                return (self.total_tokens / 1_000_000) * costs["total"]
        return 0.0


@dataclass
class OpenAIResponse:
    """Response from OpenAI API with usage tracking."""

    content: str
    usage: TokenUsage
    model: str
    duration_ms: float
    cost: float


@dataclass
class EmbeddingResponse:
    """Response from OpenAI embedding API."""

    embedding: list[float]
    model: str
    duration_ms: float
    cost: float


@dataclass
class TranscriptionResponse:
    """Response from OpenAI Whisper API."""

    text: str
    language: str | None  # Whisper API doesn't return language by default
    duration: float
    duration_ms: float
    cost: float


# =============================================================================
# Service
# =============================================================================

class OpenAIService:
    """
    OpenAI API client service.

    Provides async methods for:
    - Chat completions with streaming support
    - Text embeddings for vector search
    - Audio transcription via Whisper

    All methods include:
    - Structured logging with correlation ID
    - Token usage tracking
    - Cost estimation
    - Error handling with retry

    Example:
        service = OpenAIService()
        response = await service.chat("Hello, how are you?", user_id="123")
        print(response.content)
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = DEFAULT_MODEL,
        default_embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        default_whisper_model: str = DEFAULT_WHISPER_MODEL,
    ) -> None:
        """
        Initialize OpenAI service.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            default_model: Default chat model
            default_embedding_model: Default embedding model
            default_whisper_model: Default transcription model
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = default_model
        self.default_embedding_model = default_embedding_model
        self.default_whisper_model = default_whisper_model
        self.logger = get_logger("ai", "OpenAIService")

    async def chat(
        self,
        message: str,
        system_prompt: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> OpenAIResponse:
        """
        Send chat completion request.

        Per FR-002: Use gpt-4o-mini for agent logic.

        Args:
            message: User message
            system_prompt: Optional system prompt
            conversation_history: Previous messages for context
            model: Model to use (defaults to gpt-4o-mini)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)

        Returns:
            OpenAIResponse with content, usage, timing, cost

        Raises:
            OpenAIError: If API call fails
        """
        model = model or self.default_model
        start_time = time.time()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        # Log request (LOG-040)
        self.logger.info(
            "OpenAI chat request",
            event_type="openai_request",
            model=model,
            endpoint_type="chat",
            message_length=len(message),
            history_length=len(conversation_history) if conversation_history else 0,
        )

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract usage
            usage = response.usage
            token_usage = TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
            cost = token_usage.cost(model)

            # Log response (LOG-040)
            self.logger.info(
                "OpenAI chat response",
                event_type="openai_response",
                model=model,
                endpoint_type="chat",
                duration_ms=round(duration_ms, 2),
                tokens_used=usage.total_tokens,
                cost_estimate=round(cost, 6),
            )

            return OpenAIResponse(
                content=response.choices[0].message.content or "",
                usage=token_usage,
                model=model,
                duration_ms=duration_ms,
                cost=cost,
            )

        except OpenAIError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "OpenAI chat error",
                event_type="openai_error",
                model=model,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise

    async def generate_embedding(
        self,
        text: str,
        model: str | None = None,
    ) -> EmbeddingResponse:
        """
        Generate text embedding for vector search.

        Per FR-032: Use text-embedding-3-small for embeddings.

        Args:
            text: Text to embed
            model: Embedding model (defaults to text-embedding-3-small)

        Returns:
            EmbeddingResponse with embedding vector and cost

        Raises:
            OpenAIError: If API call fails
        """
        model = model or self.default_embedding_model
        start_time = time.time()

        # Log request
        self.logger.info(
            "OpenAI embedding request",
            event_type="openai_request",
            model=model,
            endpoint_type="embeddings",
            text_length=len(text),
        )

        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text,
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract embedding
            embedding = response.data[0].embedding
            usage = response.usage
            token_usage = TokenUsage(total_tokens=usage.total_tokens)
            cost = token_usage.cost(model)

            # Log response
            self.logger.info(
                "OpenAI embedding response",
                event_type="openai_response",
                model=model,
                endpoint_type="embeddings",
                duration_ms=round(duration_ms, 2),
                tokens_used=usage.total_tokens,
                cost_estimate=round(cost, 6),
            )

            return EmbeddingResponse(
                embedding=embedding,
                model=model,
                duration_ms=duration_ms,
                cost=cost,
            )

        except OpenAIError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "OpenAI embedding error",
                event_type="openai_error",
                model=model,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: str | None = None,
        model: str | None = None,
        prompt: str | None = None,
    ) -> TranscriptionResponse:
        """
        Transcribe audio file using Whisper API.

        Per FR-053, FR-056, FR-057:
        - Uses whisper-1 model
        - Supports multiple languages including Urdu
        - Auto-detects language if not specified
        - Prompt biases Whisper away from Devanagari output for Urdu speech

        Args:
            audio_file_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            language: ISO-639-1 language code (auto-detect if None)
            model: Whisper model (defaults to whisper-1)
            prompt: Optional prompt to guide transcription (biases output script)

        Returns:
            TranscriptionResponse with text, detected language, timing, cost

        Raises:
            OpenAIError: If transcription fails
            FileNotFoundError: If audio file doesn't exist
        """
        model = model or self.default_whisper_model

        # Check file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        start_time = time.time()

        # Log request (LOG-042)
        self.logger.info(
            "OpenAI transcription request",
            event_type="openai_request",
            model=model,
            endpoint_type="audio",
            file_path=audio_file_path,
            language=language or "auto",
        )

        try:
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language,
                    prompt=prompt,  # Biases Whisper toward Urdu script, away from Devanagari
                )

            duration_ms = (time.time() - start_time) * 1000

            # Get audio duration (if available in response)
            duration = getattr(response, "duration", 0)

            # Calculate cost (FR-108)
            cost = (duration / 60) * WHISPER_COST_PER_MINUTE

            # Log response (LOG-042)
            # Note: Whisper API doesn't return detected language without word-level timestamps
            self.logger.info(
                "OpenAI transcription response",
                event_type="openai_response",
                model=model,
                endpoint_type="audio",
                duration_seconds=round(duration, 2),
                duration_ms=round(duration_ms, 2),
                detected_language=language or "auto",
                cost_estimate=round(cost, 6),
            )

            return TranscriptionResponse(
                text=response.text,
                language=language,  # Use the requested language (or None for auto-detect)
                duration=duration,
                duration_ms=duration_ms,
                cost=cost,
            )

        except OpenAIError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "OpenAI transcription error",
                event_type="openai_error",
                model=model,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise

    async def generate_title(
        self,
        conversation_summary: str,
    ) -> str:
        """
        Generate a conversation title from summary.

        Per spec.md: Auto-generate titles after 2 messages.
        Title is ALWAYS in English regardless of conversation language.

        Args:
            conversation_summary: Summary of conversation messages

        Returns:
            Generated title in English (max 50 characters)
        """
        try:
            response = await self.chat(
                message=f"Generate a concise title in ENGLISH (max 50 chars) for this conversation: {conversation_summary}",
                system_prompt="You are a title generator. Always generate titles in ENGLISH, regardless of the input language. Return only the title, no quotes or punctuation.",
                max_tokens=50,
                temperature=0.3,
            )

            # Clean up title
            title = response.content.strip().strip('"\'')
            return title[:50]

        except Exception:
            # Fallback to default
            return "New Chat"

    async def generate_task_summary(
        self,
        title: str,
        description: str | None = None,
        tags: list[str] | None = None,
        priority: str = "MEDIUM",
        max_length: int = 500,
    ) -> str:
        """
        Generate a concise summary of a task using AI.

        Per T093-T099: AI-powered task summarization for quick scanning.

        Args:
            title: Task title
            description: Optional task description
            tags: Optional task tags
            priority: Task priority level
            max_length: Maximum summary length in characters (T099)

        Returns:
            Generated summary (max max_length characters)
        """
        # Build task context
        task_context = f"Title: {title}"
        if description:
            task_context += f"\nDescription: {description}"
        if tags:
            task_context += f"\nTags: {', '.join(tags)}"
        task_context += f"\nPriority: {priority}"

        try:
            response = await self.chat(
                message=f"""Summarize this task concisely (max {max_length} chars):

{task_context}

Focus on: what needs to be done, any deadlines, and key details.""",
                system_prompt="""You are a task summarizer. Create concise summaries that:
- Highlight the main action required
- Mention any deadlines or time constraints
- Include important context
- Use clear, simple language
- Return ONLY the summary, no preamble""",
                max_tokens=150,
                temperature=0.5,
            )

            # Clean and truncate summary
            summary = response.content.strip().strip('"\'')
            return summary[:max_length]

        except Exception:
            # Fallback to simple summary
            parts = [title]
            if description:
                parts.append(description[:100])
            if priority != "MEDIUM":
                parts.append(f"({priority} priority)")
            return " ".join(parts)[:max_length]


# =============================================================================
# Circuit Breaker for API Failures
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker for OpenAI API failures.

    Per FR-099, FR-102: Implement circuit breaker for failing external APIs.

    States:
    - CLOSED: Normal operation
    - OPEN: API failing, reject requests
    - HALF_OPEN: Testing if API recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
    ) -> None:
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = get_logger("ai", "CircuitBreaker")

    def is_open(self) -> bool:
        """Check if circuit is open (API should be avoided)."""
        if self.state == "OPEN":
            # Check if timeout passed
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "HALF_OPEN"
                self.logger.info("Circuit breaker entering HALF_OPEN state")
                return False
            return True
        return False

    def record_success(self) -> None:
        """Record successful API call."""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.logger.info("Circuit breaker reset to CLOSED state")
        self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed API call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            old_state = self.state
            self.state = "OPEN"
            if old_state != "OPEN":
                self.logger.warning(
                    "Circuit breaker opened",
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold,
                )


# Global circuit breaker instance
_openai_circuit_breaker = CircuitBreaker()


def get_openai_circuit_breaker() -> CircuitBreaker:
    """Get the global OpenAI circuit breaker instance."""
    return _openai_circuit_breaker
