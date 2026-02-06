"""
NLP utilities for task extraction from natural language.

Provides functions to extract structured task data from
unstructured user messages like:
- "Add task to buy groceries tomorrow at 5pm" → Task with due_date
- "Remind me to call mom on Friday" → Task with title and due_date
- "High priority task: finish the report" → Task with priority

Per spec.md FR-011 through FR-016.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Any

from app.ai.utils.logging import get_logger


# =============================================================================
# Logging
# =============================================================================

logger = get_logger("ai", "NLPTaskExtraction")


# =============================================================================
# Enums
# =============================================================================

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ExtractedTask:
    """Task data extracted from natural language."""
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    tags: list[str] | None = None
    confidence: float = 1.0  # 0-1, extraction confidence


# =============================================================================
# NLP Patterns
# =============================================================================

# Priority patterns
PRIORITY_PATTERNS = {
    Priority.HIGH: [
        r"\b(high priority|urgent|important|asap|as soon as possible|emergency|critical)\b",
        r"\b!(high|urgent|important)\b",
    ],
    Priority.MEDIUM: [
        r"\b(medium priority|moderate|normal)\b",
    ],
    Priority.LOW: [
        r"\b(low priority|optional|eventually|sometime|when I can)\b",
    ],
}

# Date/time patterns
DATE_PATTERNS = [
    # Relative days
    (r"\btomorrow\b", lambda d: d + timedelta(days=1)),
    (r"\btoday\b", lambda d: d),
    (r"\byesterday\b", lambda d: d - timedelta(days=1)),  # For reference
    # Weekdays
    (r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", None),
    (r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", None),
    # Time patterns
    (r"\bat (\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?\b", None),
    (r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)\b", None),
    # Duration
    (r"\bin (\d+) (day|days|week|weeks)\b", None),
    (r"\bby (\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", None),  # m/d or m/d/yyyy
    (r"\bby (\d{4})-(\d{1,2})-(\d{1,2})\b", None),  # yyyy-m-d
]

# Tag patterns (hashtag-like)
TAG_PATTERN = r'#(\w+)'
CATEGORY_PATTERNS = [
    r'\b(work|personal|shopping|health|finance|home|family|social)\b'
]


# =============================================================================
# Extraction Functions
# =============================================================================

def extract_priority(text: str) -> Priority:
    """
    Extract priority from text.

    Args:
        text: User message text

    Returns:
        Extracted priority (default: MEDIUM)
    """
    text_lower = text.lower()

    # Check HIGH patterns first
    for pattern in PRIORITY_PATTERNS[Priority.HIGH]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return Priority.HIGH

    # Check LOW patterns
    for pattern in PRIORITY_PATTERNS[Priority.LOW]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return Priority.LOW

    # Check MEDIUM patterns
    for pattern in PRIORITY_PATTERNS[Priority.MEDIUM]:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return Priority.MEDIUM

    # Default
    return Priority.MEDIUM


def extract_due_date(text: str, reference_date: datetime | None = None) -> datetime | None:
    """
    Extract due date from text.

    Args:
        text: User message text
        reference_date: Reference date for relative calculations (default: today)

    Returns:
        Extracted due date or None
    """
    if reference_date is None:
        reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    text_lower = text.lower()

    # Simple patterns (more sophisticated parsing would use a date parser library)
    match = re.search(r"\btomorrow\b", text_lower)
    if match:
        result = reference_date + timedelta(days=1)
        # Try to extract time
        time_match = re.search(r"at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
        if time_match:
            result = _apply_time_to_date(result, time_match)
        return result

    match = re.search(r"\btoday\b", text_lower)
    if match:
        result = reference_date
        time_match = re.search(r"at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
        if time_match:
            result = _apply_time_to_date(result, time_match)
        return result

    # Next weekday
    match = re.search(r"\bnext (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", text_lower)
    if match:
        weekday = match.group(1)
        return _next_weekday(reference_date, weekday)

    # This weekday
    match = re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", text_lower)
    if match and "next" not in text_lower[:match.start()]:
        weekday = match.group(1)
        return _next_weekday(reference_date, weekday, allow_same_day=True)

    # Time only (assume today or next occurrence)
    time_match = re.search(r"at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
    if time_match:
        result = reference_date
        result = _apply_time_to_date(result, time_match)
        # If time has passed, assume tomorrow
        if result < datetime.now():
            result = result + timedelta(days=1)
        return result

    return None


def _apply_time_to_date(date: datetime, time_match: re.Match) -> datetime:
    """Apply extracted time to a date."""
    hour = int(time_match.group(1))
    minute = int(time_match.group(2)) if time_match.group(2) else 0
    ampm = time_match.group(3)

    if ampm == "pm" and hour < 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    return date.replace(hour=hour, minute=minute)


def _next_weekday(reference: datetime, weekday: str, allow_same_day: bool = False) -> datetime:
    """Get the next occurrence of a weekday."""
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    target = weekdays[weekday.lower()]
    current = reference.weekday()

    days_ahead = target - current
    if days_ahead <= 0:  # Target day already happened this week
        if allow_same_day and days_ahead == 0:
            days_ahead = 0
        else:
            days_ahead += 7

    return reference + timedelta(days=days_ahead)


def extract_tags(text: str) -> list[str]:
    """
    Extract tags from text.

    Supports both #hashtag format and category keywords.

    Args:
        text: User message text

    Returns:
        List of extracted tags
    """
    tags = []
    text_lower = text.lower()

    # Hashtag-style tags
    for match in re.finditer(TAG_PATTERN, text):
        tags.append(match.group(1))

    # Category keywords (only if no hashtags found)
    if not tags:
        for pattern in CATEGORY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                tag = match.group(1)
                if tag not in tags:
                    tags.append(tag)
                    break  # Just one category tag

    return tags


def extract_task_from_message(message: str) -> ExtractedTask:
    """
    Extract complete task data from natural language message.

    This function analyzes the user's message and extracts:
    - Task title (main content)
    - Priority (high/medium/low)
    - Due date (if specified)
    - Tags (if mentioned)

    Per FR-011 through FR-016.

    Args:
        message: User's natural language message

    Returns:
        ExtractedTask with all extracted information

    Examples:
        >>> extract_task_from_message("Add high priority task to buy groceries tomorrow")
        ExtractedTask(title="buy groceries", priority=Priority.HIGH, due_date=...)

        >>> extract_task_from_message("Remind me to call mom on Friday at 3pm")
        ExtractedTask(title="call mom", due_date=datetime(...))
    """
    # Clean the message
    cleaned = message.strip()

    # Remove common prefixes
    prefixes_to_remove = [
        r"^add (a )?task",
        r"^create (a )?task",
        r"^remind me to",
        r"^reminder:",
        r"^todo:",
        r"^task:",
        r"^i need to",
        r"^i have to",
        r"^don't forget to",
    ]

    title = cleaned
    for prefix in prefixes_to_remove:
        title = re.sub(prefix, "", title, flags=re.IGNORECASE).strip()

    # Extract priority
    priority = extract_priority(message)

    # Extract due date
    due_date = extract_due_date(message)

    # Extract tags
    tags = extract_tags(message) if extract_tags(message) else None

    # Check for description (after "-" or "--")
    description = None
    if " -- " in title:
        parts = title.split(" -- ", 1)
        title = parts[0].strip()
        description = parts[1].strip()
    elif " - " in title:
        parts = title.split(" - ", 1)
        title = parts[0].strip()
        # Only treat as description if it looks like a separate clause
        if len(parts[1]) > 10:
            description = parts[1].strip()

    # Clean title from extracted entities
    title = _clean_title(title, priority, due_date, tags)

    # Calculate confidence based on extraction completeness
    confidence = 1.0
    if not due_date:
        confidence -= 0.1
    if priority == Priority.MEDIUM and "priority" not in message.lower():
        confidence -= 0.05

    logger.debug(
        "Task extracted from message",
        title=title,
        priority=priority.value,
        due_date=str(due_date) if due_date else None,
        tags=tags,
        confidence=confidence,
    )

    return ExtractedTask(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        tags=tags,
        confidence=confidence,
    )


def _clean_title(
    title: str,
    priority: Priority,
    due_date: datetime | None,
    tags: list[str] | None,
) -> str:
    """
    Remove extracted entities from title to avoid duplication.

    Args:
        title: Raw title
        priority: Extracted priority
        due_date: Extracted due date
        tags: Extracted tags

    Returns:
        Cleaned title
    """
    cleaned = title

    # Remove priority keywords
    if priority != Priority.MEDIUM:
        for pattern in PRIORITY_PATTERNS[priority]:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Remove hashtags
    if tags:
        cleaned = re.sub(TAG_PATTERN, "", cleaned)

    # Clean up extra whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def format_task_confirmation(task: ExtractedTask, original_message: str) -> str:
    """
    Format a user-friendly confirmation message for extracted task.

    Args:
        task: Extracted task data
        original_message: Original user message

    Returns:
        Confirmation message
    """
    parts = [f"I'll create the task: **{task.title}**"]

    if task.priority != Priority.MEDIUM:
        parts.append(f"Priority: **{task.priority.value}**")

    if task.due_date:
        # Format date nicely
        if task.due_date.hour == 0 and task.due_date.minute == 0:
            date_str = task.due_date.strftime("%A, %B %d")
        else:
            date_str = task.due_date.strftime("%A, %B %d at %I:%M %p").lower()
        parts.append(f"Due: **{date_str}**")

    if task.tags:
        parts.append(f"Tags: {', '.join(f'#{t}' for t in task.tags)}")

    return ". ".join(parts) + "."


# =============================================================================
# Intent Detection
# =============================================================================

class UserIntent(str, Enum):
    """Detected user intent from message."""
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    SEARCH_TASKS = "search_tasks"
    PLAN_WEEK = "plan_week"
    CHAT = "chat"  # General conversation
    UNKNOWN = "unknown"


INTENT_PATTERNS = {
    UserIntent.CREATE_TASK: [
        r"\b(add|create|new|make) (a )?task\b",
        r"\bremind me to\b",
        r"\breminder:\b",
        r"\bi need to\b",
        r"\bi have to\b",
        r"\bdon't forget to\b",
    ],
    UserIntent.LIST_TASKS: [
        r"\b(show|list|what are my|display) (my )?tasks\b",
        r"\bwhat do I have (to do )?(on|for)\b",
        r"\bmy tasks\b",
    ],
    UserIntent.COMPLETE_TASK: [
        r"\b(complete|finish|done|did|check off|mark done) (task )?\d+\b",
        r"\b(complete|finish|done|check off) (the )?task\b",
    ],
    UserIntent.DELETE_TASK: [
        r"\b(delete|remove) (task )?\d+\b",
        r"\b(delete|remove) (the )?task\b",
    ],
    UserIntent.UPDATE_TASK: [
        r"\b(change|update|modify|edit) (task )?\d+\b",
        r"\b(change|update|modify) (the )?task\b",
    ],
    UserIntent.SEARCH_TASKS: [
        r"\b(search|find|look for|find any) (tasks )?(about|for|related to)\b",
        r"\bdo I have (any )?(tasks )?(about|for)\b",
    ],
    UserIntent.PLAN_WEEK: [
        r"\b(plan|help me plan|schedule) (my )?(week|day)\b",
        r"\bwhat's (on my agenda|scheduled for) (this week|today)\b",
    ],
}


def detect_intent(message: str) -> UserIntent:
    """
    Detect user intent from message.

    Args:
        message: User message text

    Returns:
        Detected intent
    """
    message_lower = message.lower()

    # Check each intent pattern
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                logger.debug(
                    "Intent detected",
                    intent=intent.value,
                    message=message[:50],
                )
                return intent

    return UserIntent.CHAT  # Default to general chat


# =============================================================================
# Hindi-to-Urdu Script Conversion (FR-068)
# =============================================================================

# Devanagari (Hindi) to Perso-Arabic (Urdu) character mapping
# Maps common Hindi characters to their Urdu equivalents
HINDI_TO_URDU_MAP = {
    # Vowels (matras)
    'ा': 'ا',  # aa
    'ि': 'ی',  # i (as in bit) - use ye
    'ी': 'ی',  # ee (as in see) - use bari ye
    'ु': 'و',  # u - use wao
    'ू': 'و',  # oo - use wao
    'े': 'ے',  # e
    'ै': 'ے',  # ai
    'ो': 'و',  # o
    'ौ': 'او', # au

    # Vowel signs (independent)
    'अ': 'ا',  # a
    'आ': 'آ',  # aa
    'इ': 'ای', # i
    'ई': 'ی',  # ee
    'उ': 'و',  # u
    'ऊ': 'او', # oo
    'ए': 'ے',  # e
    'ऐ': 'ے',  # ai
    'ओ': 'او', # o
    'औ': 'او', # au

    # Consonants
    'क': 'ک',   # ka
    'ख': 'کھ',  # kha
    'ग': 'گ',   # ga
    'घ': 'گھ',  # gha
    'च': 'چ',   # cha
    'छ': 'چھ',  # chha
    'ज': 'ج',   # ja
    'झ': 'جھ',  # jha
    'ट': 'ٹ',   # ta (retroflex)
    'ठ': 'ٹھ',  # tha (retroflex)
    'ड': 'ڈ',   # da (retroflex)
    'ढ': 'ڈھ',  # dha (retroflex)
    'ण': 'ن',   # na (retroflex) - map to nun
    'त': 'ت',   # ta
    'थ': 'تھ',  # tha
    'द': 'د',   # da
    'ध': 'دھ',  # dha
    'न': 'ن',   # na
    'प': 'پ',   # pa
    'फ': 'پھ',  # pha
    'ब': 'ب',   # ba
    'भ': 'بھ',  # bha
    'म': 'م',   # ma
    'य': 'ی',   # ya
    'र': 'ر',   # ra
    'ल': 'ل',   # la
    'व': 'و',   # va/wa
    'श': 'ش',   # sha
    'ष': 'ش',   # ssa - map to shin
    'स': 'س',   # sa
    'ह': 'ہ',   # ha

    # Anusvara, visarga, candrabindu
    'ं': 'ں',   # anusvara - nun ghunna
    'ः': 'ہ',   # visarga
    'ँ': 'ں',   # candrabindu

    # Numbers
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',

    # Punctuation
    '।': '۔',   # danda (Urdu full stop)
    '॥': '۔۔',  # double danda

    # Common conjuncts / combinations
    'क्ष': 'کش', # ksha
    'त्र': 'تر', # tra
    'ज्ञ': 'گی', # gya/jna
    'श्र': 'شر', # shra
}


def contains_hindi(text: str) -> bool:
    """
    Detect if text contains Hindi Devanagari script.

    Devanagari Unicode range: U+0900 to U+097F

    Args:
        text: Text to check

    Returns:
        True if text contains Devanagari characters
    """
    # Check for Devanagari characters (U+0900 to U+097F)
    for char in text:
        if '\u0900' <= char <= '\u097F':
            return True
    return False


def convert_hindi_to_urdu(text: str) -> tuple[str, bool]:
    """
    Convert Hindi Devanagari text to Urdu Perso-Arabic script.

    This function handles the common challenge where Whisper confuses
    Urdu speech with Hindi and outputs in Devanagari script.

    Per FR-068: Force output to English or Urdu only.

    Args:
        text: Text that may contain Hindi Devanagari script

    Returns:
        Tuple of (converted_text, was_converted)
        - converted_text: Text with Hindi converted to Urdu (or original if no Hindi)
        - was_converted: True if conversion was applied

    Examples:
        >>> convert_hindi_to_urdu("एक टास्क एड़ करो")
        ("ایک ٹاسک ایڈ کرو", True)

        >>> convert_hindi_to_urdu("मुझे कल कराची जाना है")
        ("مجھے کلا کراچی جانا ہے", True)

        >>> convert_hindi_to_urdu("Hello world")
        ("Hello world", False)
    """
    if not contains_hindi(text):
        return text, False

    # Character-by-character conversion
    result = []
    for char in text:
        # Try direct mapping first
        if char in HINDI_TO_URDU_MAP:
            result.append(HINDI_TO_URDU_MAP[char])
        # Handle halant (virama) - remove it in Urdu
        elif char == '्' or char == '़':
            continue  # Skip halant and nukta in output
        # Pass through non-Hindi characters unchanged
        else:
            result.append(char)

    converted = ''.join(result)

    # Clean up common conversion artifacts
    # Duplicate letters from matra + consonant combinations
    converted = re.sub(r'(یی)+', 'ی', converted)  # Fix double ye
    converted = re.sub(r'(وو)+', 'و', converted)  # Fix double wao
    converted = re.sub(r'\s+', ' ', converted)     # Fix extra spaces

    logger.info(
        "Hindi to Urdu script conversion",
        original_length=len(text),
        converted_length=len(converted),
        was_converted=True,
    )

    return converted, True
