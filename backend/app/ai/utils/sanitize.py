"""
Input sanitization utilities for AI chatbot.

Per spec.md FR-094: Sanitize user input to prevent prompt injection.

This module provides functions to detect and mitigate common
prompt injection patterns while preserving legitimate user input.
"""

import re
import logging
from typing import Any

from app.ai.utils.logging import get_logger

logger = get_logger("ai", "InputSanitization")


# =============================================================================
# Prompt Injection Patterns
# =============================================================================

# Common prompt injection patterns to detect
PROMPT_INJECTION_PATTERNS = [
    # Direct instruction overrides
    r"(?i)ignore\s+(all\s+)?(previous|the|above)?\s*instruction",
    r"(?i)disregard\s+(all\s+)?(previous|the|above)?\s*instruction",
    r"(?i)forget\s+(everything|all\s+previous|the\s+above)",

    # System role manipulation
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)act\s+as\s+(a|an)",
    r"(?i)pretend\s+to\s+be",
    r"(?i)roleplay\s+as",
    r"(?i)from\s+now\s+on\s+you\s+are",

    # Output format manipulation
    r"(?i)output\s+(as\s+)?(json|xml|yaml|code|markdown|html)",
    r"(?i)print\s+(the\s+)?(above|previous)",
    r"(?i)repeat\s+(everything|all\s+the\s+text)",
    r"(?i)echo\s+(back\s+)?(everything|the\s+input)",
    r"(?i)return\s+(the\s+)?(prompt|instructions)",

    # Extraction attempts
    r"(?i)show\s+(me\s+)?your\s+(instructions|prompt|system\s+message)",
    r"(?i)what\s+are\s+your\s+(instructions|rules|guidelines)",
    r"(?i)reveal\s+(your\s+)?(instructions|system\s+prompt)",
    r"(?i)tell\s+me\s+how\s+you\s+(work|were\s+made|programmed)",

    # Few-shot manipulation
    r"(?i)example\s*:\s*\n*(?:user|assistant|human)\s*:",
    r"(?i)follow\s+this\s+(pattern|format|example)",

    # Delimiter injection
    r"(?i)###\s*(instruction|system|user)",
    r"(?i)---\s*(instruction|system|user)",
    r"(?i)\"\"\"\s*(instruction|system|user)",
]

# Compile patterns for efficiency
_COMPILED_PATTERNS = [re.compile(pattern) for pattern in PROMPT_INJECTION_PATTERNS]


# =============================================================================
# Sanitization Functions
# =============================================================================

def detect_prompt_injection(text: str) -> dict[str, Any]:
    """
    Detect potential prompt injection attempts in user input.

    Args:
        text: User input text to analyze

    Returns:
        Dict with detection results:
        - detected: bool - Whether injection patterns were found
        - patterns: list[str] - Names of patterns that matched
        - severity: "low" | "medium" | "high" - Estimated severity
        - score: float - Confidence score (0-1)
    """
    if not text:
        return {"detected": False, "patterns": [], "severity": "low", "score": 0.0}

    text_lower = text.lower()
    matches = []

    for i, pattern in enumerate(_COMPILED_PATTERNS):
        if pattern.search(text):
            matches.append(f"pattern_{i}")

    # Calculate severity based on match count and text characteristics
    severity = "low"
    score = 0.0

    if matches:
        # Base score on number of matches
        score = min(len(matches) * 0.3, 1.0)

        # Increase score for multiple injection attempts
        if len(matches) >= 3:
            severity = "high"
            score = min(score + 0.2, 1.0)
        elif len(matches) >= 2:
            severity = "medium"
            score = min(score + 0.1, 1.0)

        # Check for advanced techniques
        if any(word in text_lower for word in ["base64", "rot13", "hex", "ascii"]):
            score = min(score + 0.2, 1.0)

    return {
        "detected": len(matches) > 0,
        "patterns": matches,
        "severity": severity,
        "score": score,
    }


def sanitize_user_input(text: str, max_length: int = 5000) -> dict[str, Any]:
    """
    Sanitize user input for the AI chatbot.

    Per spec.md FR-094: System MUST sanitize user input to prevent prompt injection.

    This function:
    1. Trims excessive whitespace
    2. Removes/reduces repeated characters
    3. Detects prompt injection patterns
    4. Enforces maximum length
    5. Returns cleaned text with detection metadata

    Args:
        text: Raw user input
        max_length: Maximum allowed length (default 5000)

    Returns:
        Dict with:
        - text: str - Sanitized text
        - original_length: int - Original text length
        - sanitized_length: int - Sanitized text length
        - truncated: bool - Whether text was truncated
        - injection_detection: dict - Result from detect_prompt_injection()
    """
    if not text:
        return {
            "text": "",
            "original_length": 0,
            "sanitized_length": 0,
            "truncated": False,
            "injection_detection": detect_prompt_injection(""),
        }

    original_length = len(text)

    # Trim leading/trailing whitespace
    text = text.strip()

    # Normalize internal whitespace (reduce multiple spaces/newlines to single space)
    text = re.sub(r"\s+", " ", text)

    # Remove excessive repeated characters (e.g., "!!!!!!!" -> "!!!")
    text = re.sub(r"(.)\1{10,}", r"\1\1\1", text)

    # Truncate if too long
    truncated = False
    if len(text) > max_length:
        text = text[:max_length]
        truncated = True

    # Detect injection patterns
    injection_detection = detect_prompt_injection(text)

    # Log suspicious inputs
    if injection_detection["detected"]:
        logger.warning(
            "Prompt injection detected",
            severity=injection_detection["severity"],
            score=injection_detection["score"],
            patterns_found=len(injection_detection["patterns"]),
            text_length=len(text),
        )

    return {
        "text": text,
        "original_length": original_length,
        "sanitized_length": len(text),
        "truncated": truncated,
        "injection_detection": injection_detection,
    }


def should_block_input(sanitization_result: dict[str, Any], threshold: float = 0.7) -> bool:
    """
    Determine if input should be blocked based on sanitization result.

    Args:
        sanitization_result: Result from sanitize_user_input()
        threshold: Confidence score threshold (default 0.7)

    Returns:
        True if input should be blocked, False otherwise
    """
    injection = sanitization_result.get("injection_detection", {})

    # Block if high severity detected
    if injection.get("severity") == "high":
        return True

    # Block if score exceeds threshold
    if injection.get("score", 0) >= threshold:
        return True

    return False


def strip_system_instructions(text: str) -> str:
    """
    Strip potential system instruction leaks from output.

    This is used on assistant responses to prevent accidental
    system prompt leakage through prompt injection.

    Args:
        text: Assistant response text

    Returns:
        Text with potential system instruction markers removed
    """
    # Remove common system prompt markers
    patterns = [
        r"(?i)###\s*system\s*prompt\s*###.*?(?=###|$)",
        r"(?i)---\s*system\s*---.*?(?=---|$)",
        r"(?i)\"\"\"\s*system\s*\"\"\".*?(?=\"\"\"|$)",
        r"(?i)\[system\s*prompt\].*?(?=\[|$)",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "[REDACTED]", text, flags=re.DOTALL)

    return text
