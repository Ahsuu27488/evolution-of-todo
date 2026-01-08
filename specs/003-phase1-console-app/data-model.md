# Data Model: Phase 1 Console App

**Feature**: 003-phase1-console-app
**Date**: 2025-12-27
**Source**: spec.md §Key Entities, research.md §RQ-001 to RQ-005

---

## Entity: Task

The core entity representing a todo item.

### Fields

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes | Auto-assigned | Unique, sequential, ≥1, never reused | Unique task identifier |
| `title` | `str` | Yes | - | 1-200 chars, trimmed, non-empty | Task title |
| `description` | `str` | No | `""` | 0-1000 chars, trimmed | Optional task description |
| `priority` | `Priority` | No | `MEDIUM` | Enum: HIGH, MEDIUM, LOW | Task priority level |
| `tags` | `set[str]` | No | `set()` | 0-10 tags, each max 30 chars, unique, lowercase | Categorization tags |
| `completed` | `bool` | No | `False` | - | Completion status |
| `created_at` | `datetime` | Yes | Auto-assigned | UTC timezone | Creation timestamp |

### Enumerations

#### Priority

```python
class Priority(IntEnum):
    """Task priority levels with natural ordering.

    Higher value = higher priority for sorting.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
```

| Value | Display | Sort Order |
|-------|---------|------------|
| `HIGH` | `[HIGH]` | 1st (highest) |
| `MEDIUM` | `[MEDIUM]` | 2nd |
| `LOW` | `[LOW]` | 3rd (lowest) |

### Entity Definition

```python
@dataclass
class Task:
    """Represents a todo item.

    Attributes:
        id: Unique identifier (auto-assigned, sequential)
        title: Task title (1-200 chars, required)
        description: Optional task description (0-1000 chars)
        priority: Priority level (default: MEDIUM)
        tags: Set of categorization tags (max 10)
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
```

### Validation Rules

| Rule ID | Field | Rule | Error Message |
|---------|-------|------|---------------|
| VR-001 | `title` | Not empty after trimming | "Title is required" |
| VR-002 | `title` | Length ≤ 200 chars | "Title must be 200 characters or less" |
| VR-003 | `description` | Length ≤ 1000 chars | "Description must be 1000 characters or less" |
| VR-004 | `priority` | Must be valid enum value | "Priority must be high, medium, or low" |
| VR-005 | `tags` | Each tag ≤ 30 chars | "Tag must be 30 characters or less" |
| VR-006 | `tags` | Max 10 tags | "Maximum 10 tags allowed" |
| VR-007 | `tags` | Lowercase, trimmed | (auto-normalized) |
| VR-008 | `tags` | Unique (no duplicates) | (auto-deduplicated) |

### State Transitions

```
                    ┌──────────────────────┐
                    │                      │
                    │      PENDING         │
                    │   (completed=False)  │
                    │                      │
                    └──────────┬───────────┘
                               │
                               │ toggle_complete()
                               │
                               ▼
                    ┌──────────────────────┐
                    │                      │
                    │     COMPLETED        │
                    │   (completed=True)   │
                    │                      │
                    └──────────┬───────────┘
                               │
                               │ toggle_complete()
                               │
                               ▼
                    ┌──────────────────────┐
                    │                      │
                    │      PENDING         │
                    │   (completed=False)  │
                    │                      │
                    └──────────────────────┘
```

---

## Repository: TaskRepository

Abstract interface for task storage operations.

### Interface

```python
class TaskRepository(ABC):
    """Abstract base for task storage.

    Implementations:
    - InMemoryTaskRepository (Phase I)
    - PostgresTaskRepository (Phase II - future)
    """

    @abstractmethod
    def add(self, task: Task) -> Task:
        """Add a new task, returns task with assigned ID."""
        pass

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        """Get task by ID, returns None if not found."""
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Get all tasks."""
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update existing task, raises TaskNotFoundError if not found."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete task by ID, returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total number of tasks."""
        pass
```

### In-Memory Implementation

```python
class InMemoryTaskRepository(TaskRepository):
    """In-memory task storage using dictionary.

    Data structures:
    - _tasks: dict[int, Task] - primary storage, O(1) lookup
    - _next_id: int - auto-incrementing ID counter
    """

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| `add` | O(1) | O(1) |
| `get` | O(1) | O(1) |
| `get_all` | O(n) | O(n) |
| `update` | O(1) | O(1) |
| `delete` | O(1) | O(1) |
| `count` | O(1) | O(1) |

---

## Service: TaskService

Business logic layer for task operations.

### Interface

```python
class TaskService:
    """Task management business logic.

    Coordinates between CLI and repository.
    Handles validation, filtering, sorting.
    """

    def __init__(self, repository: TaskRepository):
        self._repository = repository

    # CRUD Operations
    def create_task(self, title: str, description: str = "",
                    priority: Priority = Priority.MEDIUM,
                    tags: set[str] | None = None) -> Task

    def get_task(self, task_id: int) -> Task

    def update_task(self, task_id: int, title: str | None = None,
                    description: str | None = None,
                    priority: Priority | None = None,
                    tags: set[str] | None = None) -> Task

    def delete_task(self, task_id: int) -> bool

    def toggle_complete(self, task_id: int) -> Task

    # Query Operations
    def list_tasks(self, status: str | None = None,
                   priority: Priority | None = None,
                   tag: str | None = None,
                   search: str | None = None,
                   sort_by: str | None = None) -> list[Task]

    def get_stats(self) -> dict[str, int]
```

### Method Specifications

#### `create_task`

| Input | Validation | Output |
|-------|------------|--------|
| `title: str` | VR-001, VR-002 | `Task` with new ID |
| `description: str` | VR-003 | |
| `priority: Priority` | VR-004 | |
| `tags: set[str]` | VR-005, VR-006, VR-007, VR-008 | |

#### `list_tasks`

| Parameter | Filter Behavior |
|-----------|-----------------|
| `status="pending"` | Tasks where `completed=False` |
| `status="completed"` | Tasks where `completed=True` |
| `status="all"` or `None` | All tasks |
| `priority=Priority.HIGH` | Tasks with `priority=HIGH` |
| `tag="work"` | Tasks where `"work" in tags` |
| `search="milk"` | Tasks where `"milk"` in title or description (case-insensitive) |
| `sort_by="priority"` | Sort by priority descending (HIGH → LOW) |
| `sort_by="title"` | Sort alphabetically by title |
| `sort_by="created"` | Sort by creation date (newest first) |
| `sort_by="status"` | Sort by status (pending first) |

#### `get_stats`

Returns:
```python
{
    "total": int,      # Total task count
    "pending": int,    # Tasks with completed=False
    "completed": int   # Tasks with completed=True
}
```

---

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

---

## Display Formats

### Task List Display

```
╔═══════════════════════════════════════════════════════════════════╗
║                         📋 YOUR TASKS                              ║
╠═══════════════════════════════════════════════════════════════════╣
║ Total: 5 | Pending: 3 | Completed: 2                              ║
╠════╦════════════════════════╦════════╦═══════════════╦════════════╣
║ ID ║ Title                  ║ Status ║ Priority      ║ Tags       ║
╠════╬════════════════════════╬════════╬═══════════════╬════════════╣
║ 1  ║ Buy groceries          ║ [ ]    ║ [HIGH]        ║ #shopping  ║
║ 2  ║ Call mom               ║ [✓]    ║ [MEDIUM]      ║ #personal  ║
║ 3  ║ Review PR              ║ [ ]    ║ [HIGH]        ║ #work      ║
╚════╩════════════════════════╩════════╩═══════════════╩════════════╝
```

### Priority Display

| Priority | Display | Emphasis |
|----------|---------|----------|
| HIGH | `[HIGH]` | Bold/Red in color terminals |
| MEDIUM | `[MEDIUM]` | Normal |
| LOW | `[LOW]` | Dim/Gray in color terminals |

### Status Display

| Status | Display |
|--------|---------|
| Pending | `[ ]` |
| Completed | `[✓]` |

### Tag Display

Format: `#tag1 #tag2 #tag3`

If no tags: `(no tags)`

---

## Evolution Path

This data model is designed for evolution:

| Phase | Extension |
|-------|-----------|
| Phase II | Add `user_id: str` field, persist to PostgreSQL |
| Phase III | Task operations become MCP tools |
| Phase IV-V | Add `due_date`, `recurring` fields |

---

*Data model version: 1.0*
*Compatible with: spec.md v1.0*
