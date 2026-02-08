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
    dominant_script: Literal["latin", "arabic", "devanagari", "mixed"]


# Unicode ranges for language detection
ARABIC_UNICODE_RANGE = (0x0600, 0x06FF)
ARABIC_EXTENDED_RANGE = (0x0750, 0x077F)
ARABIC_PRESENTATION_RANGE = (0xFB50, 0xFDFF)
ARABIC_PRESENTATION_EXTENDED_RANGE = (0xFE70, 0xFEFF)

# Devanagari Unicode range (Hindi, Marathi, Sanskrit, etc.)
DEVANAGARI_UNICODE_RANGE = (0x0900, 0x097F)

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


def _is_devanagari_char(char: str) -> bool:
    """Check if character is in Devanagari Unicode range (Hindi, etc.)."""
    code_point = ord(char)
    start, end = DEVANAGARI_UNICODE_RANGE
    return start <= code_point <= end


def detect_language(text: str) -> LanguageDetectionResult:
    """
    Detect the language of input text.

    Per FR-042: If >30% of characters are in Arabic Unicode block, classify as Urdu.
    Per requirement: Hindi (Devanagari) input maps to Urdu response language.

    Args:
        text: Input text to analyze

    Returns:
        LanguageDetectionResult with detected language, confidence, and script info

    Examples:
        >>> detect_language("Add a task")
        LanguageDetectionResult(language=LanguageCode.ENGLISH, confidence=1.0, ...)

        >>> detect_language("مجھے ایک ٹاسک شامل کرو")
        LanguageDetectionResult(language=LanguageCode.URDU, confidence=0.95, ...)

        >>> detect_language("एक टास्क जोड़ें")  # Hindi
        LanguageDetectionResult(language=LanguageCode.URDU, confidence=0.9, ...)  # Maps to Urdu

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
    devanagari_chars = 0
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
        elif _is_devanagari_char(char):
            devanagari_chars += 1
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
    devanagari_ratio = devanagari_chars / total_chars if total_chars > 0 else 0

    # Determine dominant script
    if arabic_ratio > 0.7:
        dominant_script = "arabic"
    elif devanagari_ratio > 0.7:
        dominant_script = "devanagari"
    elif latin_ratio > 0.7:
        dominant_script = "latin"
    else:
        dominant_script = "mixed"

    # Check for code-switching (both scripts present significantly)
    has_code_switching = (arabic_ratio > 0.2 and latin_ratio > 0.2) or \
                         (devanagari_ratio > 0.2 and latin_ratio > 0.2)

    # Detect Hindi/Devanagari - map to Urdu response
    # Per requirement: Hindi input gets Urdu response
    if devanagari_ratio > 0.15:  # More than 15% Devanagari = Hindi
        confidence = min(0.95, devanagari_ratio + 0.3)
        if has_code_switching:
            confidence = confidence * 0.85

        return LanguageDetectionResult(
            language=LanguageCode.URDU,  # Map Hindi to Urdu for response
            confidence=round(confidence, 2),
            has_code_switching=has_code_switching,
            dominant_script=dominant_script,
        )

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
# Cross-Language Semantic Search Support
# =============================================================================

# Common Urdu-to-English word mappings for transliteration
# This helps when users mix Urdu and English in queries like "Dinner wala task"
URDU_TO_ENGLISH_MAPPING = {
    # Common words (Urdu script -> Roman Urdu -> English)
    "کام": "kaam",  # work
    "کام کا": "kaam ka",
    "کھانا": "khana",  # food
    "کھانے کا": "khanay ka",
    "خریداری": "khareedy",  # shopping
    "دنر": "dinner",  # dinner
    "ناشتہ": "nashta",  # breakfast
    "دوپہر کا کھانا": "dopehar ka khana",  # lunch
    "ملاقات": "mulaqaat",  # meeting
    "جلس": "jals",  # meeting/gathering
    "کلاس": "class",  # class
    "مطالعات": "mutaleat",  # study
    "پڑھائی": "parhai",  # study
    "فون": "phone",  # phone/call
    "کال": "call",  # call
    "دکان": "dukan",  # shop/store
    "مارکیٹ": "market",  # market
    "گاڑی": "gari",  # car/vehicle
    "سفر": "safar",  # travel/trip
    "دوا": "dawa",  # medicine
    "ڈاکٹر": "doctor",  # doctor
    "ہسپتال": "hospital",  # hospital
    "مقصد": "maqsad",  # purpose/task
    "ٹاسک": "task",  # task
    "کام": "kaam",  # work
    "مکمل": "mukammal",  # complete/finish
    "ختم": "khatam",  # finish/end
    "شروع": "shuroo",  # start
    "بنائیں": "banain",  # make/create
    "شامل": "shamil",  # include/add
    "ہٹائیں": "hatayen",  # remove/delete
    "حذف": "hazf",  # delete
    "اپ ڈیٹ": "update",  # update
    "تبدیل": "tabdeel",  # change
    "جائز": "jaiz",  # review
    "چیک": "check",  # check
}

# Common Roman Urdu words to English
ROMAN_URDU_TO_ENGLISH = {
    "kaam": "work",
    "khana": "food",
    "khareedy": "shopping",
    "dinner": "dinner",
    "nashta": "breakfast",
    "lunch": "lunch",
    "mulaqaat": "meeting",
    "jals": "meeting",
    "class": "class",
    "mutaleat": "study",
    "parhai": "study",
    "phone": "call",
    "call": "call",
    "dukan": "shop",
    "market": "market",
    "gari": "car",
    "safar": "travel",
    "dawa": "medicine",
    "doctor": "doctor",
    "hospital": "hospital",
    "maqsad": "task",
    "task": "task",
    "mukammal": "complete",
    "khatam": "finish",
    "shuroo": "start",
    "banain": "create",
    "shamil": "add",
    "hatayen": "remove",
    "hazf": "delete",
    "update": "update",
    "tabdeel": "change",
    "jaiz": "review",
    "check": "check",
    "kar": "do",
    "karna": "do",
    "kr": "do",  # Short for karna in Roman Urdu
    "wala": "of",  # "Dinner wala" = "Dinner of" = related to dinner
}


def preprocess_query_for_semantic_search(query: str) -> list[str]:
    """
    Preprocess a query for cross-language semantic search.

    When users mix Urdu and English (e.g., "Dinner wala task complete krdo"),
    semantic search may fail because:
    1. The query contains mixed scripts
    2. The task titles might be in English while query has Urdu words

    This function generates multiple query variants to improve matching:
    1. Original query (preserve exact wording)
    2. Query with Urdu words transliterated to English
    3. Query with Roman Urdu words converted to English equivalents

    Args:
        query: The original search query

    Returns:
        List of query variants to try in order of priority

    Examples:
        >>> preprocess_query_for_semantic_search("Dinner wala task complete krdo")
        ["Dinner wala task complete krdo", "Dinner of task complete do", "Dinner related task complete do"]

        >>> preprocess_query_for_semantic_search("دنر کا ٹاسک")
        ["دنر کا ٹاسک", "Dinner ka task", "Dinner task"]
    """
    if not query:
        return [query]

    variants = [query]  # Always include original query first

    # Check if query contains Urdu script
    has_urdu_script = is_urdu_text(query)

    # Check if query contains common Roman Urdu patterns
    words = query.lower().split()
    has_roman_urdu = any(word in ROMAN_URDU_TO_ENGLISH for word in words)

    if has_urdu_script or has_roman_urdu:
        # Create English-transliterated variant
        transliterated = query

        # Replace Urdu script words with English equivalents
        for urdu_word, english_word in URDU_TO_ENGLISH_MAPPING.items():
            transliterated = transliterated.replace(urdu_word, english_word)

        # Replace Roman Urdu words with English equivalents
        for roman_urdu, english in ROMAN_URDU_TO_ENGLISH.items():
            # Use word boundary regex for more accurate replacement
            import re as re_module
            pattern = r'\b' + re_module.escape(roman_urdu) + r'\b'
            transliterated = re_module.sub(
                pattern,
                english,
                transliterated,
                flags=re_module.IGNORECASE
            )

        # Handle common suffixes like "wala" / "wali"
        if "wala" in transliterated.lower() or "wali" in transliterated.lower():
            # "X wala" roughly means "X of" or "related to X" or "X person"
            # Replace with "related to" or remove for better semantic matching
            import re as re_module
            transliterated = re_module.sub(
                r'\bwala\b',
                'related to',
                transliterated,
                flags=re_module.IGNORECASE
            )
            transliterated = re_module.sub(
                r'\bwali\b',
                'related to',
                transliterated,
                flags=re_module.IGNORECASE
            )

        # Add transliterated variant if different from original
        if transliterated != query and transliterated not in variants:
            variants.append(transliterated)

        # Create a simpler English-only variant for key terms
        # Extract key English words and create a simplified query
        import re as re_module
        # Remove common Roman Urdu particles
        simplified = re_module.sub(
            r'\b(kr|karna|kar|karo|do|hai|hai|ka|ki|ke|ko|se|mein|par|pe|bhi|to|hi)\b',
            '',
            transliterated,
            flags=re_module.IGNORECASE
        )
        simplified = ' '.join(simplified.split())  # Clean up extra spaces
        if simplified and simplified not in variants and len(simplified) > 3:
            variants.append(simplified)

    return variants


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
