"""
Language detection utilities for multi-language support.

This module provides language detection for Urdu and English,
as specified in FR-041 through FR-050.

Detection method (FR-042):
- If >30% of characters are in Unicode Arabic block (U+0600-U+06FF), classify as Urdu
- Code-switching detection: Mixed text classified by dominant script
- Supports both Urdu script (اردو) and Roman Urdu (Urdu written with Latin script)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class LanguageCode(str, Enum):
    """ISO-639-1 language codes supported by the system."""

    ENGLISH = "en"
    URDU = "ur"
    AUTO = "auto"  # Auto-detect


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""

    language: LanguageCode
    confidence: float  # 0.0 to 1.0
    has_code_switching: bool
    dominant_script: Literal["latin", "arabic", "mixed"]


# Unicode ranges for language detection
ARABIC_UNICODE_RANGE = (0x0600, 0x06FF)
ARABIC_EXTENDED_RANGE = (0x0750, 0x077F)
ARABIC_PRESENTATION_RANGE = (0xFB50, 0xFDFF)
ARABIC_PRESENTATION_EXTENDED_RANGE = (0xFE70, 0xFEFF)

# Urdu-specific character ranges (includes additional characters)
URDU_RANGES = [
    ARABIC_UNICODE_RANGE,
    ARABIC_EXTENDED_RANGE,
    ARABIC_PRESENTATION_RANGE,
    ARABIC_PRESENTATION_EXTENDED_RANGE,
]

# Common Urdu words for improved detection
COMMON_URDU_WORDS = {
    # Urdu script words
    "میں", "کو", "سے", "کا", "کی", "کے", "ہے", "ہوں", "گا", "گی", "لئے",
    "کرنا", "کر", "دیں", "دو", "دے", "لے", "ہے", "تھا", "تھی",
    # Roman Urdu (written with Latin script)
    "ke", "ka", "ki", "ko", "se", "mein", "hai", "hain", "ho",
    "kar", "karein", "do", "dena", "lena", "hai", "tha", "thi",
    "bhai", "beti", "beta", "ammi", "abbu", "baji", "bhai",
}


def _is_arabic_char(char: str) -> bool:
    """Check if character is in Arabic/Urdu Unicode range."""
    code_point = ord(char)
    for start, end in URDU_RANGES:
        if start <= code_point <= end:
            return True
    return False


def detect_language(text: str) -> LanguageDetectionResult:
    """
    Detect the language of input text.

    Per FR-042: If >30% of characters are in Arabic Unicode block, classify as Urdu.

    Args:
        text: Input text to analyze

    Returns:
        LanguageDetectionResult with detected language, confidence, and script info

    Examples:
        >>> detect_language("Add a task")
        LanguageDetectionResult(language=LanguageCode.ENGLISH, confidence=1.0, ...)

        >>> detect_language("مجھے ایک ٹاسک شامل کرو")
        LanguageDetectionResult(language=LanguageCode.URDU, confidence=0.95, ...)

        >>> detect_language("Add a task for آج")
        LanguageDetectionResult(language=LanguageCode.ENGLISH, confidence=0.7, has_code_switching=True, ...)
    """
    if not text:
        return LanguageDetectionResult(
            language=LanguageCode.ENGLISH,
            confidence=0.0,
            has_code_switching=False,
            dominant_script="latin",
        )

    # Count characters by script
    total_chars = 0
    arabic_chars = 0
    latin_chars = 0
    other_chars = 0

    # Count words
    words = re.findall(r"\w+", text.lower())
    urdu_words = 0
    total_words = len(words)

    for word in words:
        if word in COMMON_URDU_WORDS:
            urdu_words += 1

    for char in text:
        # Skip whitespace, punctuation, numbers
        if char.isspace() or char in "0123456789.,!?;:'\"@#$%^&*()_+-=[]{}|/<>~`":
            continue

        total_chars += 1

        if _is_arabic_char(char):
            arabic_chars += 1
        elif char.isalpha():
            latin_chars += 1
        else:
            other_chars += 1

    # If no significant characters, default to English
    if total_chars == 0:
        return LanguageDetectionResult(
            language=LanguageCode.ENGLISH,
            confidence=0.0,
            has_code_switching=False,
            dominant_script="latin",
        )

    # Calculate script ratios
    arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
    latin_ratio = latin_chars / total_chars if total_chars > 0 else 0

    # Determine dominant script
    if arabic_ratio > 0.7:
        dominant_script = "arabic"
    elif latin_ratio > 0.7:
        dominant_script = "latin"
    else:
        dominant_script = "mixed"

    # Check for code-switching (both scripts present significantly)
    has_code_switching = arabic_ratio > 0.2 and latin_ratio > 0.2

    # Detect language per FR-042 (>30% Arabic = Urdu)
    if arabic_ratio > 0.3:
        # Urdu detected
        confidence = min(0.95, arabic_ratio + 0.2)  # Boost confidence for high Arabic ratio
        if has_code_switching:
            confidence = confidence * 0.8  # Reduce confidence for mixed script

        return LanguageDetectionResult(
            language=LanguageCode.URDU,
            confidence=round(confidence, 2),
            has_code_switching=has_code_switching,
            dominant_script=dominant_script,
        )

    # Check for Roman Urdu using word detection
    if total_words > 0:
        roman_urdu_ratio = urdu_words / total_words
        if roman_urdu_ratio > 0.3:
            return LanguageDetectionResult(
                language=LanguageCode.URDU,
                confidence=round(roman_urdu_ratio + 0.4, 2),
                has_code_switching=has_code_switching,
                dominant_script="latin",
            )

    # Default to English
    confidence = latin_ratio if not has_code_switching else latin_ratio * 0.8

    return LanguageDetectionResult(
        language=LanguageCode.ENGLISH,
        confidence=round(confidence, 2),
        has_code_switching=has_code_switching,
        dominant_script=dominant_script,
    )


def should_respond_in_urdu(user_message: str, user_preference: LanguageCode) -> bool:
    """
    Determine if AI should respond in Urdu based on message and preference.

    Per FR-043: Respond in the same language as user input.

    Args:
        user_message: User's input message
        user_preference: User's language preference setting

    Returns:
        True if response should be in Urdu, False for English

    Examples:
        >>> should_respond_in_urdu("مجھے کام کے لیے فون کرنا ہے", LanguageCode.AUTO)
        True

        >>> should_respond_in_urdu("Add a task", LanguageCode.URDU)
        False  # User preference doesn't override input language

        >>> should_respond_in_urdu("Add a task", LanguageCode.AUTO)
        False
    """
    # Check if message is in Urdu
    detection = detect_language(user_message)

    # AUTO: follow detected language
    if user_preference == LanguageCode.AUTO:
        return detection.language == LanguageCode.URDU

    # Explicit preference: follow preference
    return user_preference == LanguageCode.URDU


def get_response_language(
    user_message: str, user_preference: LanguageCode
) -> LanguageCode:
    """
    Get the language for AI response based on message and preference.

    Args:
        user_message: User's input message
        user_preference: User's language preference setting

    Returns:
        LanguageCode for the response (en or ur)
    """
    if should_respond_in_urdu(user_message, user_preference):
        return LanguageCode.URDU
    return LanguageCode.ENGLISH


def is_urdu_text(text: str) -> bool:
    """
    Quick check if text contains Urdu script.

    Args:
        text: Text to check

    Returns:
        True if text contains Urdu script characters

    Examples:
        >>> is_urdu_text("Add a task")
        False

        >>> is_urdu_text("مجھے ایک ٹاسک شامل کرو")
        True

        >>> is_urdu_text("Add a task for آج")
        True  # Contains Urdu characters
    """
    if not text:
        return False
    return any(_is_arabic_char(char) for char in text)


def get_text_direction(text: str) -> Literal["ltr", "rtl"]:
    """
    Determine text direction for rendering.

    Per FR-048: Urdu text requires RTL rendering.

    Args:
        text: Text to analyze

    Returns:
        "rtl" for Urdu/Arabic text, "ltr" for English

    Examples:
        >>> get_text_direction("Add a task")
        'ltr'

        >>> get_text_direction("مجھے ایک ٹاسک شامل کرو")
        'rtl'
    """
    detection = detect_language(text)
    if detection.language == LanguageCode.URDU and detection.dominant_script in (
        "arabic",
        "mixed",
    ):
        return "rtl"
    return "ltr"


# =============================================================================
# Deprecated - langdetect fallback
# =============================================================================

def detect_language_with_fallback(text: str) -> LanguageCode:
    """
    Fallback language detection using langdetect library.

    This is only used if the primary detection is uncertain.
    Note: langdetect is optional and may not be accurate for Urdu.

    Args:
        text: Input text

    Returns:
        Detected language code
    """
    try:
        from langdetect import detect, DetectorFactory

        # Set seed for reproducibility
        DetectorFactory.seed = 0

        detected = detect(text)
        if detected == "ur":
            return LanguageCode.URDU
        elif detected == "en":
            return LanguageCode.ENGLISH
        else:
            # Default to English for unsupported languages
            return LanguageCode.ENGLISH
    except Exception:
        # On any error, default to English
        return LanguageCode.ENGLISH
