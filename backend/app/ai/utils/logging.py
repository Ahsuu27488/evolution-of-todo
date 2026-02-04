"""
Structured logging with correlation ID support for Phase III.

This module provides:
- JSON-structured logging via structlog
- Correlation ID propagation across async boundaries
- Context-aware logging with user_id, service, component
- Request lifecycle tracking (start, end, duration)

Per FR-LOG-001 through FR-LOG-084 in spec.md.
"""

import contextvars
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

import structlog
from structlog.types import EventDict, Processor

# =============================================================================
# Context Variables for Async Propagation
# =============================================================================

# Correlation ID context - propagates across async boundaries
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id",
    default=None,
)

# User ID context - populated from JWT
user_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_id",
    default=None,
)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class LogConfig:
    """Structured logging configuration."""

    level: str = "INFO"  # DEBUG, INFO, WARN, ERROR
    json_output: bool = True  # JSON format for parsing
    include_timestamp: bool = True
    include_caller_info: bool = False  # For DEBUG only
    log_level: int = logging.INFO


# Global configuration
_config: LogConfig = LogConfig()


def configure_logging(level: str = "INFO", json_output: bool = True) -> None:
    """
    Configure structlog for the application.

    Args:
        level: Minimum log level (DEBUG, INFO, WARN, ERROR)
        json_output: Whether to output JSON (True) or plain text (False)
    """
    global _config
    _config.level = level.upper()
    _config.json_output = json_output

    # Map level string to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    _config.log_level = level_map.get(_config.level, logging.INFO)

    # Configure structlog processors
    processors: list[Processor] = [
        # Add context variables
        _add_correlation_id,
        _add_user_id,
        # Add timestamp if configured
        _add_timestamp if _config.include_timestamp else lambda x, y: x,
        # Add standard library log level
        _add_log_level,
        # Format the output
        _json_renderer if _config.json_output else _text_renderer,
    ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(_config.log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# =============================================================================
# Processors
# =============================================================================

def _add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID from context or generate new one."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def _add_user_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add user ID from context if available."""
    user_id = user_id_ctx.get(None)
    if user_id:
        event_dict["user_id"] = user_id
    return event_dict


def _add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO-8601 timestamp in UTC."""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def _add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add standard log level."""
    event_dict["level"] = method_name.lower()
    return event_dict


def _json_renderer(logger: Any, method_name: str, event_dict: EventDict) -> str:
    """Render log entry as JSON."""
    # Remove internal keys
    event_dict.pop("_record", None)
    event_dict.pop("_logger", None)
    return json.dumps(event_dict, default=str)


def _text_renderer(logger: Any, method_name: str, event_dict: EventDict) -> str:
    """Render log entry as human-readable text."""
    timestamp = event_dict.pop("timestamp", "")
    level = event_dict.pop("level", "info")
    correlation_id = event_dict.pop("correlation_id", "")
    message = event_dict.pop("event", "")

    parts = [f"[{level}"]
    if timestamp:
        parts.append(f"{timestamp}")
    if correlation_id:
        parts.append(f"cid={correlation_id[:8]}")
    parts.append(f"] {message}")

    # Add remaining context
    if event_dict:
        parts.append(f" {json.dumps(event_dict)}")

    return "".join(parts)


# =============================================================================
# Public API
# =============================================================================

def get_logger(service: str, component: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        service: Service name (chat, mcp, agents, search, embeddings, voice)
        component: Optional module or class name

    Returns:
        Configured structlog bound logger

    Example:
        logger = get_logger("chat", "ChatService")
        logger.info("Processing message", message_id=msg_id)
    """
    logger = structlog.get_logger()
    logger = logger.bind(service=service)
    if component:
        logger = logger.bind(component=component)
    return logger


def generate_correlation_id() -> str:
    """
    Generate a new UUID v4 correlation ID.

    Returns:
        UUID v4 string

    Example:
        "550e8400-e29b-41d4-a716-446655440000"
    """
    return str(uuid.uuid4())


def get_correlation_id() -> str | None:
    """
    Get the current correlation ID from context.

    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id_ctx.get(None)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID in the current context.

    Args:
        correlation_id: Correlation ID to set

    Example:
        set_correlation_id(generate_correlation_id())
    """
    correlation_id_ctx.set(correlation_id)


def set_user_id(user_id: str) -> None:
    """
    Set the user ID in the current context.

    Args:
        user_id: User ID from JWT 'sub' claim
    """
    user_id_ctx.set(user_id)


def bind_correlation_id(correlation_id: str | None = None) -> dict[str, Any]:
    """
    Bind a correlation ID to the current context.

    Args:
        correlation_id: Optional correlation ID (generates if not provided)

    Returns:
        Context dict with correlation_id

    Example:
        ctx = bind_correlation_id()
        logger.info("Request started", **ctx)
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    return {"correlation_id": correlation_id}


# =============================================================================
# Decorators for Request Tracing
# =============================================================================

@dataclass
class LogContext:
    """
    Context manager for request lifecycle logging.

    Automatically logs request start/end with timing and handles errors.

    Example:
        with LogContext(logger, "process_message", message_id=msg_id) as ctx:
            result = process_message(msg_id)
            ctx.add_result(result=result)
    """

    logger: structlog.stdlib.BoundLogger
    operation: str
    correlation_id: str | None = None
    user_id: str | None = None
    start_time: float = field(default_factory=time.time)
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize context and log start event."""
        if self.correlation_id:
            set_correlation_id(self.correlation_id)
        if self.user_id:
            set_user_id(self.user_id)

        # Log start event
        log_data = {"event_type": "request_start", "operation": self.operation}
        if self.data:
            log_data.update(self.data)
        self.logger.info("Request started", **log_data)

    def add_data(self, **kwargs: Any) -> None:
        """Add data to be logged on completion."""
        self.data.update(kwargs)

    def __enter__(self) -> "LogContext":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager and log completion."""
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is not None:
            # Log error
            self.logger.error(
                "Request failed",
                event_type="request_error",
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                error={
                    "type": exc_type.__name__ if exc_type else "Unknown",
                    "message": str(exc_val) if exc_val else "",
                },
                **self.data,
            )
        else:
            # Log success
            self.logger.info(
                "Request completed",
                event_type="request_end",
                operation=self.operation,
                duration_ms=round(duration_ms, 2),
                **self.data,
            )


def log_operation(operation: str | None = None) -> Callable:
    """
    Decorator to automatically log function entry/exit with timing.

    Args:
        operation: Operation name (defaults to function name)

    Example:
        @log_operation("process_message")
        async def process_message(message_id: str) -> Message:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger("chat", func.__name__)
            op_name = operation or func.__name__

            with LogContext(logger, op_name):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(
                        f"{op_name} failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                    raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger("chat", func.__name__)
            op_name = operation or func.__name__

            with LogContext(logger, op_name):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(
                        f"{op_name} failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                    raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# =============================================================================
# Utility Functions
# =============================================================================

def sanitize_log_data(data: dict[str, Any], sensitive_keys: set[str] | None = None) -> dict[str, Any]:
    """
    Sanitize log data by removing sensitive values.

    Per LOG-010: Never log JWT tokens, API keys, passwords, PII.

    Args:
        data: Data to sanitize
        sensitive_keys: Keys to redact (default set includes common sensitive keys)

    Returns:
        Sanitized data with sensitive values redacted
    """
    if sensitive_keys is None:
        sensitive_keys = {
            "password",
            "token",
            "jwt",
            "api_key",
            "apikey",
            "api_key",
            "secret",
            "authorization",
            "bearer",
            "credit_card",
            "ssn",
            "social_security",
        }

    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_log_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def format_metrics(
    duration_ms: float,
    tokens_used: int | None = None,
    db_queries: int | None = None,
    **extra_metrics: Any,
) -> dict[str, Any]:
    """
    Format metrics for log entry.

    Args:
        duration_ms: Operation duration in milliseconds
        tokens_used: OpenAI tokens consumed (if applicable)
        db_queries: Number of database queries (if applicable)
        **extra_metrics: Additional metrics

    Returns:
        Formatted metrics dict
    """
    metrics: dict[str, Any] = {
        "duration_ms": round(duration_ms, 2),
    }
    if tokens_used is not None:
        metrics["tokens_used"] = tokens_used
    if db_queries is not None:
        metrics["db_queries"] = db_queries
    metrics.update(extra_metrics)
    return metrics


# =============================================================================
# Module Initialization
# =============================================================================

# Configure default logging on import
configure_logging()
