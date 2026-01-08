# Todo Domain Data Models

## Phase I: Enhanced In-Memory Model (Basic + Intermediate)

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

class Priority(IntEnum):
    """Task priority levels with natural ordering.

    Higher value = higher priority for sorting.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def display(self) -> str:
        return f"[{self.name}]"

@dataclass
class Task:
    """Represents a todo item.

    Attributes:
        id: Unique identifier (auto-assigned, sequential)
        title: Task title (1-200 chars, required)
        description: Optional task description (0-1000 chars)
        priority: Priority level (default: MEDIUM)
        tags: Set of categorization tags (max 10, each max 30 chars)
        completed: Completion status (default: False)
        created_at: Creation timestamp (auto-assigned)
    """
    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    tags: set[str] = field(default_factory=set)
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

# In-memory storage with O(1) lookup
tasks: dict[int, Task] = {}
next_id: int = 1
```

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `title` | Non-empty after trim | "Title is required" |
| `title` | ≤ 200 chars | "Title must be 200 characters or less" |
| `description` | ≤ 1000 chars | "Description must be 1000 characters or less" |
| `priority` | Valid enum | "Priority must be high, medium, or low" |
| `tags` | Each ≤ 30 chars | "Tag must be 30 characters or less" |
| `tags` | Max 10 items | "Maximum 10 tags allowed" |

### Tag Parsing

```python
def parse_tags(input_str: str) -> set[str]:
    """Parse comma-separated tags, normalize and deduplicate."""
    if not input_str.strip():
        return set()
    tags = {tag.strip().lower() for tag in input_str.split(",")}
    return {t for t in tags if t and len(t) <= 30}[:10]
```

## Phase II: Database Model (SQLModel)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to users
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: int = Field(default=Priority.MEDIUM)  # Stored as int
    tags: str = Field(default="")  # Stored as comma-separated
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def tags_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]
```

## Phase III: Conversation Models

```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    user_id: str = Field(index=True)
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Exception Hierarchy

```python
class TodoError(Exception):
    """Base exception for todo application."""
    pass

class TaskNotFoundError(TodoError):
    """Raised when task ID doesn't exist."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class ValidationError(TodoError):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")
```

## Feature Levels

### Basic Level (Required - Phase I)
1. Add Task - Create new todo items with title, description, priority, tags
2. Delete Task - Remove tasks from list with confirmation
3. Update Task - Modify existing task details (all fields)
4. View Task List - Display all tasks with status, priority, tags
5. Mark as Complete - Toggle completion status

### Intermediate Level (Included in Phase I - Enhanced)
1. **Priorities** - High/Medium/Low with visual indicators [HIGH], [MEDIUM], [LOW]
2. **Tags/Categories** - Multiple tags per task, displayed as #hashtags
3. **Search & Filter** - By keyword (title/description), status, priority, tag
4. **Sort Tasks** - By priority, title, creation date, status

### Advanced Level (Phase V)
1. Recurring Tasks - Auto-reschedule repeating tasks
2. Due Dates & Reminders - Deadlines with notifications

## Repository Interface

```python
from abc import ABC, abstractmethod

class TaskRepository(ABC):
    """Abstract base for task storage."""

    @abstractmethod
    def add(self, task: Task) -> Task: ...

    @abstractmethod
    def get(self, task_id: int) -> Task | None: ...

    @abstractmethod
    def get_all(self) -> list[Task]: ...

    @abstractmethod
    def update(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: int) -> bool: ...

    @abstractmethod
    def count(self) -> int: ...
```

## Service Layer Operations

```python
class TaskService:
    """Task management business logic."""

    # CRUD Operations
    def create_task(self, title, description="", priority=Priority.MEDIUM, tags=None) -> Task
    def get_task(self, task_id: int) -> Task
    def update_task(self, task_id, title=None, description=None, priority=None, tags=None) -> Task
    def delete_task(self, task_id: int) -> bool
    def toggle_complete(self, task_id: int) -> Task

    # Query Operations
    def list_tasks(self, status=None, priority=None, tag=None, search=None, sort_by=None) -> list[Task]
    def get_stats(self) -> dict[str, int]  # {total, pending, completed}
```

## Display Formats

### Priority Display
| Priority | Display | Emphasis |
|----------|---------|----------|
| HIGH | `[HIGH]` | Red/Bold |
| MEDIUM | `[MEDIUM]` | Yellow/Normal |
| LOW | `[LOW]` | Gray/Dim |

### Status Display
| Status | Display |
|--------|---------|
| Pending | `[ ]` |
| Completed | `[✓]` |

### Tag Display
Format: `#tag1 #tag2 #tag3`
Empty: `(no tags)`
