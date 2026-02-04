"""
AI utilities package.

Provides utilities for structured logging, correlation ID management,
language detection, NLP task extraction, and other cross-cutting concerns for Phase III.
"""

from .logging import (
    get_logger,
    bind_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    LogContext,
)
from .language import (
    detect_language,
    LanguageCode,
    LanguageDetectionResult,
    should_respond_in_urdu,
    get_text_direction,
)
from .nlp import (
    extract_task_from_message,
    extract_priority,
    extract_due_date,
    extract_tags,
    format_task_confirmation,
    detect_intent,
    UserIntent,
    ExtractedTask,
    Priority,
)

__all__ = [
    # Logging
    "get_logger",
    "bind_correlation_id",
    "generate_correlation_id",
    "get_correlation_id",
    "LogContext",
    # Language
    "detect_language",
    "LanguageCode",
    "LanguageDetectionResult",
    "should_respond_in_urdu",
    "get_text_direction",
    # NLP
    "extract_task_from_message",
    "extract_priority",
    "extract_due_date",
    "extract_tags",
    "format_task_confirmation",
    "detect_intent",
    "UserIntent",
    "ExtractedTask",
    "Priority",
]
