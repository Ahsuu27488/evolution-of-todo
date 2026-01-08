"""Task entity and Priority/Recurrence enums for the todo domain."""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import IntEnum, Enum


class Priority(IntEnum):
    """Task priority levels with natural ordering for sorting.

    Higher value = higher priority. IntEnum enables natural comparison
    and sorting operations.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __str__(self) -> str:
        """Return lowercase name for user input matching."""
        return self.name.lower()

    @property
    def display(self) -> str:
        """Display format for CLI: [HIGH], [MEDIUM], [LOW]."""
        return f"[{self.name}]"


class Recurrence(Enum):
    """Task recurrence patterns for automatic scheduling.

    When a recurring task is marked complete, a new occurrence
    is automatically created with the calculated next due date.
    """
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        """Return lowercase value for user input matching."""
        return self.value

    @property
    def display(self) -> str:
        """Display format for CLI: (Daily), (Weekly), etc.

        Returns empty string for NONE to avoid clutter.
        """
        if self == Recurrence.NONE:
            return ""
        return f"({self.value.title()})"


@dataclass
class Task:
    """Core task entity representing a todo item.

    Attributes:
        id: Unique identifier (auto-assigned, sequential, never reused)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        priority: Priority level (default: MEDIUM)
        tags: Set of categorization tags (max 10, each max 30 chars)
        completed: Completion status (default: False)
        created_at: Creation timestamp (auto-assigned)
        due_date: Optional deadline date (YYYY-MM-DD format)
        recurrence: Repeat pattern for auto-scheduling (default: NONE)
    """
    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    tags: set[str] = field(default_factory=set)
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_date: date | None = None
    recurrence: Recurrence = field(default=Recurrence.NONE)
