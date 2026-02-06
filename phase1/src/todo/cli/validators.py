"""Input validation helpers for CLI interactions."""

from datetime import date

from todo.domain.task import Priority, Recurrence
from todo.cli.display import print_error


def get_input(prompt: str) -> str:
    """Get trimmed string input from user.

    Args:
        prompt: The prompt to display

    Returns:
        Trimmed user input
    """
    return input(prompt).strip()


def get_integer_input(prompt: str, min_val: int | None = None, max_val: int | None = None) -> int | None:
    """Get integer input with optional range validation.

    Args:
        prompt: The prompt to display
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Valid integer or None if input invalid
    """
    try:
        value = int(input(prompt).strip())
        if min_val is not None and value < min_val:
            print_error(f"Please enter a number greater than or equal to {min_val}.")
            return None
        if max_val is not None and value > max_val:
            print_error(f"Please enter a number less than or equal to {max_val}.")
            return None
        return value
    except ValueError:
        print_error("Please enter a valid number.")
        return None


def get_yes_no_input(prompt: str) -> bool | None:
    """Get yes/no confirmation from user.

    Args:
        prompt: The prompt to display (should include y/n hint)

    Returns:
        True for yes, False for no, None for invalid input
    """
    response = input(prompt).strip().lower()
    if response in ("y", "yes"):
        return True
    if response in ("n", "no"):
        return False
    print_error("Please enter y or n.")
    return None


def get_choice_input(prompt: str, valid_choices: list[str]) -> str | None:
    """Get input that must match one of the valid choices.

    Args:
        prompt: The prompt to display
        valid_choices: List of acceptable values

    Returns:
        Valid choice or None if input invalid
    """
    response = input(prompt).strip()
    if response in valid_choices:
        return response
    print_error(f"Invalid option. Please select one of: {', '.join(valid_choices)}")
    return None


def get_priority_input(prompt: str = "Enter priority (high/medium/low) [medium]: ") -> Priority:
    """Get priority level from user with default.

    Args:
        prompt: The prompt to display

    Returns:
        Priority enum value (defaults to MEDIUM)
    """
    response = input(prompt).strip().lower()

    if not response:
        return Priority.MEDIUM

    priority_map = {
        "high": Priority.HIGH,
        "h": Priority.HIGH,
        "medium": Priority.MEDIUM,
        "m": Priority.MEDIUM,
        "med": Priority.MEDIUM,
        "low": Priority.LOW,
        "l": Priority.LOW,
    }

    if response in priority_map:
        return priority_map[response]

    print_error("Invalid priority. Please enter high, medium, or low.")
    return get_priority_input(prompt)


def get_tags_input(prompt: str = "Enter tags (comma-separated, optional): ") -> set[str]:
    """Parse comma-separated tags from user input.

    Tags are normalized: lowercased, trimmed, deduplicated.
    Maximum 10 tags, each max 30 characters.

    Args:
        prompt: The prompt to display

    Returns:
        Set of normalized tag strings
    """
    response = input(prompt).strip()

    if not response:
        return set()

    # Split by comma, normalize each tag
    tags = set()
    for tag in response.split(","):
        normalized = tag.strip().lower()
        if normalized and len(normalized) <= 30:
            tags.add(normalized)
        elif normalized:
            print_error(f"Tag '{normalized[:30]}...' too long (max 30 chars), skipped.")

    # Enforce max 10 tags
    if len(tags) > 10:
        print_error(f"Too many tags ({len(tags)}). Only first 10 will be kept.")
        tags = set(list(tags)[:10])

    return tags


def get_task_id_input(prompt: str = "Enter task ID: ") -> int | None:
    """Get a valid task ID from user.

    Args:
        prompt: The prompt to display

    Returns:
        Task ID as integer or None if invalid
    """
    response = input(prompt).strip()

    try:
        task_id = int(response)
        if task_id < 1:
            print_error("Task ID must be a positive number.")
            return None
        return task_id
    except ValueError:
        print_error("Please enter a valid task ID (number).")
        return None


def get_title_input(prompt: str = "Enter title (required): ", allow_empty: bool = False) -> str | None:
    """Get a valid task title from user.

    Args:
        prompt: The prompt to display
        allow_empty: Whether empty input is allowed

    Returns:
        Valid title string or None if validation fails
    """
    response = input(prompt).strip()

    if not response:
        if allow_empty:
            return ""
        print_error("Title is required. Please enter a title.")
        return None

    if len(response) > 200:
        print_error("Title must be 200 characters or less.")
        return None

    return response


def get_description_input(prompt: str = "Enter description (optional, press Enter to skip): ") -> str:
    """Get optional task description from user.

    Args:
        prompt: The prompt to display

    Returns:
        Description string (may be empty)
    """
    response = input(prompt).strip()

    if len(response) > 1000:
        print_error("Description must be 1000 characters or less. Truncating.")
        return response[:1000]

    return response


def get_due_date_input(prompt: str = "Enter due date (YYYY-MM-DD, or press Enter to skip): ") -> date | None:
    """Get and validate due date input from user.

    Accepts dates in YYYY-MM-DD format. Empty input returns None (no due date).
    Re-prompts on invalid format or invalid date values.

    Args:
        prompt: The prompt to display

    Returns:
        Parsed date object or None if skipped

    Examples:
        >>> get_due_date_input()  # User enters "2025-01-15"
        date(2025, 1, 15)
        >>> get_due_date_input()  # User presses Enter
        None
    """
    while True:
        response = input(prompt).strip()

        if not response:
            return None

        try:
            return date.fromisoformat(response)
        except ValueError:
            print_error("Invalid format. Please enter date as YYYY-MM-DD (e.g., 2025-01-15)")


def get_recurrence_input(prompt: str = "Set recurrence? (none/daily/weekly/monthly) [none]: ") -> Recurrence:
    """Get and validate recurrence pattern input from user.

    Accepts: none, daily, weekly, monthly (case-insensitive).
    Empty input defaults to NONE. Re-prompts on invalid input.

    Args:
        prompt: The prompt to display

    Returns:
        Recurrence enum value (defaults to NONE on empty input)

    Examples:
        >>> get_recurrence_input()  # User enters "daily"
        Recurrence.DAILY
        >>> get_recurrence_input()  # User presses Enter
        Recurrence.NONE
    """
    recurrence_map = {
        "none": Recurrence.NONE,
        "n": Recurrence.NONE,
        "daily": Recurrence.DAILY,
        "d": Recurrence.DAILY,
        "weekly": Recurrence.WEEKLY,
        "w": Recurrence.WEEKLY,
        "monthly": Recurrence.MONTHLY,
        "m": Recurrence.MONTHLY,
    }

    while True:
        response = input(prompt).strip().lower()

        if not response:
            return Recurrence.NONE

        if response in recurrence_map:
            return recurrence_map[response]

        print_error("Invalid recurrence. Please enter none, daily, weekly, or monthly.")
