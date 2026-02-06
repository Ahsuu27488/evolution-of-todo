"""
Runner service for OpenAI Agents SDK execution.

Handles:
- Agent execution with streaming responses
- Context management across agent lifecycle
- Message history tracking
- Tool call result tracking
- SSE event generation

Per spec.md FR-001 through FR-010, FR-018.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.context import (
    TodoContext,
    set_context,
    reset_context,
)
from app.ai.agents.todo_agent import get_todo_agent
from app.ai.mcp.tools import TaskTools
from app.ai.utils.logging import get_logger


# =============================================================================
# Logging
# =============================================================================

logger = get_logger("ai", "RunnerService")


# =============================================================================
# Event Types
# =============================================================================

class StreamEventType(str, Enum):
    """Types of SSE events for streaming."""

    MESSAGE_START = "message_start"
    TOKEN = "token"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AGENT_HANDOFF = "agent_handoff"
    MESSAGE_DONE = "message_done"
    ERROR = "error"


# =============================================================================
# Result Data Classes
# =============================================================================

@dataclass
class StreamEvent:
    """SSE event for streaming response."""

    event: StreamEventType
    data: dict[str, Any]
    id: str | None = None


@dataclass
class RunnerResult:
    """Result from agent execution."""

    final_output: str
    agent_name: str
    tool_calls: list[dict[str, Any]]
    handoffs: list[dict[str, Any]]
    duration_ms: float
    token_usage: dict[str, int] | None = None
    context: TodoContext | None = None


# =============================================================================
# Runner Service
# =============================================================================

class RunnerService:
    """
    Service for executing AI agents with streaming support.

    Per FR-001 through FR-010:
    - Streaming token-by-token responses
    - Tool call execution via MCP
    - Agent handoff tracking
    - Context preservation across handoffs

    Usage:
        service = RunnerService(session)

        async for event in service.stream_chat(user_message, context):
            yield event

        result = await service.get_result()
    """

    def __init__(
        self,
        session: AsyncSession,
        openai_api_key: str | None = None,
    ):
        """
        Initialize Runner service.

        Args:
            session: Database session for MCP tools
            openai_api_key: Optional OpenAI API key (defaults to env var)
        """
        self.session = session
        self.openai_api_key = openai_api_key

        # State
        self._result: RunnerResult | None = None
        self._events: list[StreamEvent] = []
        self._start_time: float | None = None

        self.logger = get_logger("ai", "RunnerService")

        # Check if SDK is available
        try:
            from agents import Runner
            self.Runner = Runner
            self.sdk_available = True
        except ImportError:
            self.sdk_available = False
            self.Runner = None
            self.logger.warning("OpenAI Agents SDK not installed")

    async def stream_chat(
        self,
        user_message: str,
        context: TodoContext,
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream agent response to user message.

        Per FR-001: Streaming responses via SSE for token-by-token delivery.

        Args:
            user_message: User's input message
            context: TodoContext with user_id, conversation_id, etc.
            conversation_history: Previous messages for context

        Yields:
            StreamEvent objects for SSE

        Example:
            async for event in service.stream_chat(message, context):
                if event.event == StreamEventType.TOKEN:
                    print(event.data["content"])
        """
        import time
        self._start_time = time.time()

        # Send message_start event
        yield StreamEvent(
            event=StreamEventType.MESSAGE_START,
            data={
                "conversation_id": context.conversation_id,
                "correlation_id": context.correlation_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        if not self.sdk_available:
            # Fallback for development without SDK
            async for event in self._fallback_stream(user_message, context):
                yield event
            return

        try:
            from agents import Runner, ItemHelpers
            from openai.types.responses import ResponseTextDeltaEvent

            # Get agent
            agent = get_todo_agent()
            if not agent:
                yield StreamEvent(
                    event=StreamEventType.ERROR,
                    data={"error": "Agent not available", "message": "AI service not configured"},
                )
                return

            # Build input with history
            messages = conversation_history or []

            # Inject response language instruction based on context
            # This ensures the agent responds in the correct language regardless of input detection
            if context.response_language:
                if context.response_language == "ur":
                    language_instruction = {
                        "role": "system",
                        "content": "RESPONSE LANGUAGE: You must respond in Urdu (اردو). Always reply in Urdu script, regardless of the language the user uses in their message."
                    }
                elif context.response_language == "en":
                    language_instruction = {
                        "role": "system",
                        "content": "RESPONSE LANGUAGE: You must respond in English only. Always reply in English, regardless of the language the user uses in their message."
                    }
                else:
                    # Auto mode - let agent detect
                    language_instruction = None

                if language_instruction:
                    messages.append(language_instruction)

            messages.append({"role": "user", "content": user_message})

            # Set context variable so tool functions can access user_id and session
            # The SDK passes context to Runner.run() but @function_tool decorated
            # functions don't receive it automatically. We use contextvars to bridge this.
            # Per openai-agents-guide: context variables provide async-safe implicit access.
            context_token = set_context(context)

            try:
                # Run with streaming - context is also passed for agent-level state
                result = Runner.run_streamed(agent, messages, context=context)

                # Track state
                tool_calls = []
                handoffs = []
                current_agent = agent.name

                # Stream events
                event_count = 0
                self.logger.info("Starting to stream events from agent")

                async for event in result.stream_events():
                    event_count += 1

                    # Debug: log all event types to understand the SDK's structure
                    self.logger.info(
                        "Stream event received",
                        event_type=event.type,
                        event_data_type=type(event.data).__name__ if hasattr(event, 'data') else None,
                        event_count=event_count,
                    )

                    if event.type == "raw_response_event":
                        # Token-by-token streaming
                        if isinstance(event.data, ResponseTextDeltaEvent):
                            self.logger.info(f"Yielding TOKEN event: {repr(event.data.delta)}")
                            yield StreamEvent(
                                event=StreamEventType.TOKEN,
                                data={"content": event.data.delta},
                            )

                    elif event.type == "agent_updated_stream_event":
                        # Agent handoff occurred (T109: Handoff tracking with logging)
                        new_agent = event.new_agent.name
                        if new_agent != current_agent:
                            handoff_data = {
                                "from_agent": current_agent,
                                "to_agent": new_agent,
                                "reason": f"Agent specialized handoff: {current_agent} → {new_agent}",
                                "timestamp": datetime.utcnow().isoformat() + "Z",
                            }
                            handoffs.append(handoff_data)

                            # LOG-030: Log handoff events with correlation ID
                            self.logger.info(
                                "Agent handoff occurred",
                                event_type="agent_handoff",
                                user_id=context.user_id,
                                conversation_id=context.conversation_id,
                                correlation_id=context.correlation_id,
                                from_agent=current_agent,
                                to_agent=new_agent,
                                reason=handoff_data["reason"],
                            )

                            yield StreamEvent(
                                event=StreamEventType.AGENT_HANDOFF,
                                data=handoff_data,
                            )
                            current_agent = new_agent

                    elif event.type == "run_item_stream_event":
                        # Tool calls and other items
                        if event.item.type == "tool_call_item":
                            tool_name = event.item.raw_item.name
                            tool_args = event.item.raw_item.arguments

                            # Parse JSON string to dict for storage (OpenAI SDK returns string)
                            # This prevents double-serialization issues when loading from DB
                            if isinstance(tool_args, str):
                                try:
                                    tool_args = json.loads(tool_args)
                                except json.JSONDecodeError:
                                    # If parsing fails, keep as-is
                                    pass

                            yield StreamEvent(
                                event=StreamEventType.TOOL_CALL,
                                data={
                                    "tool": tool_name,
                                    "arguments": tool_args,
                                },
                            )
                            tool_calls.append({
                                "tool": tool_name,
                                "arguments": tool_args,
                            })

                        elif event.item.type == "tool_call_output_item":
                            # Debug: log the item structure to understand available attributes
                            self.logger.info(
                                "Tool call output item received",
                                item_type=type(event.item).__name__,
                                item_dir=[x for x in dir(event.item) if not x.startswith('_')],
                            )
                            # ToolCallOutputItem has different attributes - access output directly
                            output = event.item.output if hasattr(event.item, 'output') else str(event.item)
                            yield StreamEvent(
                                event=StreamEventType.TOOL_RESULT,
                                data={
                                    "tool": "unknown",  # tool_name not available on output item
                                    "output": str(output),
                                },
                            )

                        elif event.item.type == "message_output_item":
                            # Full message completed
                            pass

                self.logger.info(f"Finished streaming events. Total events: {event_count}")

                # Finalize result
                duration_ms = (time.time() - self._start_time) * 1000

                # Debug: log the final_output and try different ways to access it
                self.logger.info(
                    "Result object inspection",
                    result_has_final_output=hasattr(result, 'final_output'),
                    result_type=type(result).__name__,
                    result_dir=[x for x in dir(result) if not x.startswith('_')][:20],
                )

                # Try to extract final_output using different methods
                final_out = ""
                if hasattr(result, 'final_output') and result.final_output:
                    final_out = str(result.final_output)
                elif hasattr(result, 'response') and result.response:
                    # Try accessing via response attribute
                    response = result.response
                    if hasattr(response, 'output') and response.output:
                        final_out = str(response.output)
                    elif hasattr(response, 'choices') and response.choices:
                        # OpenAI API format
                        final_out = str(response.choices[0].message.content) if response.choices else ""

                self.logger.info(
                    "Final output extracted",
                    final_output_length=len(final_out),
                    final_output_preview=final_out[:200] if final_out else "(empty)",
                )

                self._result = RunnerResult(
                    final_output=final_out,
                    agent_name=current_agent,
                    tool_calls=tool_calls,
                    handoffs=handoffs,
                    duration_ms=duration_ms,
                    context=context,
                )

                # Send message_done event
                yield StreamEvent(
                    event=StreamEventType.MESSAGE_DONE,
                    data={
                        "final_output": self._result.final_output,
                        "agent": current_agent,
                        "duration_ms": duration_ms,
                    },
                )

                self.logger.info(
                    "Agent execution completed",
                    event_type="agent_complete",
                    user_id=context.user_id,
                    conversation_id=context.conversation_id,
                    agent_name=current_agent,
                    duration_ms=duration_ms,
                    tool_calls_count=len(tool_calls),
                    handoffs_count=len(handoffs),
                )

            except Exception as e:
                duration_ms = (time.time() - self._start_time) * 1000
                self.logger.error(
                    "Agent execution failed",
                    event_type="agent_error",
                    user_id=context.user_id,
                    conversation_id=context.conversation_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration_ms=duration_ms,
                )

                yield StreamEvent(
                    event=StreamEventType.ERROR,
                    data={
                        "error": type(e).__name__,
                        "message": "Sorry, I encountered an error. Please try again.",
                    },
                )

                # Set error result
                self._result = RunnerResult(
                    final_output="",
                    agent_name="error",
                    tool_calls=[],
                    handoffs=[],
                    duration_ms=duration_ms,
                    context=context,
                )

            finally:
                # Always reset context variable to avoid leaking context between requests
                reset_context(context_token)

        except Exception as e:
            # Outer exception handler for SDK import or other setup errors
            self.logger.error(
                "SDK setup error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            yield StreamEvent(
                event=StreamEventType.ERROR,
                data={
                    "error": type(e).__name__,
                    "message": "AI service initialization failed. Please try again.",
                },
            )

    async def _fallback_stream(
        self,
        user_message: str,
        context: TodoContext,
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Fallback streaming when SDK is not available.

        Used for development/testing without OpenAI API access.
        """
        import time

        # Simulate processing
        await asyncio.sleep(0.1)

        response = f"I received: {user_message[:50]}..."

        # Stream tokens (simulated)
        for word in response.split():
            yield StreamEvent(
                event=StreamEventType.TOKEN,
                data={"content": word + " "},
            )
            await asyncio.sleep(0.05)

        yield StreamEvent(
            event=StreamEventType.MESSAGE_DONE,
            data={
                "final_output": response,
                "agent": "TodoAgent",
                "duration_ms": 100,
            },
        )

        self._result = RunnerResult(
            final_output=response,
            agent_name="TodoAgent",
            tool_calls=[],
            handoffs=[],
            duration_ms=100,
            context=context,
        )

    def get_result(self) -> RunnerResult | None:
        """
        Get the final result after streaming completes.

        Returns:
            RunnerResult if execution completed, None otherwise
        """
        return self._result


# =============================================================================
# Helper Functions
# =============================================================================

def convert_to_sse_format(event: StreamEvent) -> dict[str, str]:
    """
    Convert StreamEvent to SSE format for EventSourceResponse.

    Per sse-starlette pattern, data must be a JSON string.
    See: app/services/sse_service.py for working SSE implementation.

    Args:
        event: StreamEvent from RunnerService

    Returns:
        Dict compatible with sse_starlette EventSourceResponse
    """
    return {
        "event": event.event.value,
        "data": json.dumps(event.data),
    }


async def stream_with_correlation(
    service: RunnerService,
    user_message: str,
    context: TodoContext,
    conversation_history: list[dict[str, Any]] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Stream agent responses with correlation ID logging.

    Wraps RunnerService.stream_chat with SSE format conversion.

    Args:
        service: RunnerService instance
        user_message: User's input message
        context: TodoContext with correlation ID
        conversation_history: Previous messages

    Yields:
        Dict in SSE format for EventSourceResponse
    """
    async for event in service.stream_chat(user_message, context, conversation_history):
        yield convert_to_sse_format(event)
