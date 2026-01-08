# Implementation Plan: Phase 1 Console App

**Branch**: `003-phase1-console-app` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase1-console-app/spec.md`

---

## Summary

Build an **in-memory Python console todo application** implementing all 5 Basic Level features (Add, Delete, Update, View, Mark Complete) **plus** all 4 Intermediate Level features (Priorities, Tags, Search & Filter, Sort). The application uses a layered architecture (Domain → Services → Repository → CLI) designed for evolution into a full-stack web application in Phase II.

**Primary Achievement**: Exceed Phase 1 requirements by delivering 9 features instead of 5, establishing competitive advantage in the hackathon.

---

## Technical Context

| Aspect | Value |
|--------|-------|
| **Language/Version** | Python 3.13+ |
| **Primary Dependencies** | Standard library only (dataclasses, enum, datetime, abc) |
| **Storage** | In-memory `dict[int, Task]` with O(1) lookup |
| **Testing** | pytest (dev dependency) |
| **Target Platform** | Linux/macOS/Windows console (UTF-8 terminals) |
| **Project Type** | Single project |
| **Performance Goals** | <100ms for any operation on 1000 tasks |
| **Constraints** | <50MB memory, no external runtime dependencies |
| **Scale/Scope** | Up to 1000 tasks per session |

---

## Constitution Check

*GATE: Validated against `.specify/memory/constitution.md`*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **Phase I Scope** | ✅ PASS | In-memory only, no DB/Files/Auth/Web/APIs |
| **Standard Library Only** | ✅ PASS | Using dataclasses, enum, datetime, abc (all stdlib) |
| **SDD Workflow** | ✅ PASS | Spec → Plan → Tasks → Implement pipeline |
| **Clean Architecture** | ✅ PASS | Domain/Services/Repository/CLI layers |
| **Type Hints Required** | ✅ PASS | All functions will have type annotations |
| **Reusable Intelligence** | ✅ PASS | Updated `todo-domain` skill with enhanced model |
| **Context7 for External Docs** | ✅ N/A | No external libraries in Phase I |

**Gate Result**: PASS - Proceed to implementation planning.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-phase1-console-app/
├── spec.md              # Feature specification (WHAT)
├── plan.md              # This file - architecture (HOW)
├── research.md          # Technical decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer guide
├── contracts/
│   └── cli-interface.md # CLI interaction contract
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── todo/
│   ├── __init__.py           # Package init with version
│   ├── domain/               # Layer 1: Business Entities
│   │   ├── __init__.py
│   │   ├── task.py           # Task dataclass, Priority enum
│   │   └── exceptions.py     # TodoError, TaskNotFoundError, ValidationError
│   ├── services/             # Layer 2: Business Logic
│   │   ├── __init__.py
│   │   └── task_service.py   # TaskService with CRUD + query operations
│   ├── repository/           # Layer 3: Data Access
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract TaskRepository
│   │   └── memory.py         # InMemoryTaskRepository
│   └── cli/                  # Layer 4: Presentation
│       ├── __init__.py
│       ├── app.py            # Main CLI application loop
│       ├── handlers.py       # Menu option handlers
│       ├── display.py        # Output formatting utilities
│       └── validators.py     # Input validation helpers
└── main.py                   # Entry point

tests/
├── __init__.py
├── conftest.py               # pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_task.py          # Task entity tests
│   ├── test_priority.py      # Priority enum tests
│   ├── test_exceptions.py    # Exception tests
│   ├── test_repository.py    # InMemoryTaskRepository tests
│   └── test_service.py       # TaskService tests
└── integration/
    ├── __init__.py
    └── test_cli_flows.py     # End-to-end CLI flow tests
```

**Structure Decision**: Single project with layered architecture. Domain and Services layers are framework-agnostic, enabling direct reuse in Phase II (FastAPI) and Phase III (MCP tools).

---

## Architecture Design

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI LAYER (Presentation)                  │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌────────────┐    │
│  │ app.py  │  │handlers.py│  │display.py│  │validators.py│   │
│  └────┬────┘  └─────┬─────┘  └────┬────┘  └─────┬──────┘    │
│       │             │             │             │            │
│       └─────────────┴─────────────┴─────────────┘            │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │ depends on
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER (Use Cases)                  │
│                    ┌─────────────────┐                       │
│                    │  TaskService    │                       │
│                    │  - create_task  │                       │
│                    │  - update_task  │                       │
│                    │  - delete_task  │                       │
│                    │  - toggle_complete │                    │
│                    │  - list_tasks   │                       │
│                    │  - get_stats    │                       │
│                    └────────┬────────┘                       │
│                             │                                │
└─────────────────────────────┼────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 REPOSITORY LAYER (Data Access)               │
│   ┌──────────────────┐      ┌────────────────────────┐      │
│   │  TaskRepository  │◄─────│ InMemoryTaskRepository │      │
│   │     (ABC)        │      │   _tasks: dict[int, Task]│    │
│   └──────────────────┘      │   _next_id: int         │     │
│                             └────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (Entities)                   │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────────────┐  │
│  │    Task      │  │  Priority  │  │   Exceptions        │  │
│  │  (dataclass) │  │  (IntEnum) │  │  TodoError          │  │
│  │              │  │  LOW=1     │  │  TaskNotFoundError  │  │
│  │  id          │  │  MEDIUM=2  │  │  ValidationError    │  │
│  │  title       │  │  HIGH=3    │  └─────────────────────┘  │
│  │  description │  └────────────┘                           │
│  │  priority    │                                           │
│  │  tags        │                                           │
│  │  completed   │                                           │
│  │  created_at  │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rule

**Inner layers know nothing about outer layers.**

- Domain layer has NO dependencies (pure Python)
- Repository layer depends only on Domain
- Service layer depends on Repository and Domain
- CLI layer depends on Services, Repository, and Domain

This enables:
- Domain and Services to be reused in Phase II (FastAPI)
- Repository to be swapped for PostgreSQL in Phase II
- CLI to be replaced with web/API layer

---

## Component Specifications

### Domain Layer

#### `task.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

class Priority(IntEnum):
    """Task priority with natural ordering for sorting."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def display(self) -> str:
        """Display format for CLI: [HIGH], [MEDIUM], [LOW]"""
        return f"[{self.name}]"

@dataclass
class Task:
    """Core task entity."""
    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    tags: set[str] = field(default_factory=set)
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
```

#### `exceptions.py`

```python
class TodoError(Exception):
    """Base exception for todo application."""
    pass

class TaskNotFoundError(TodoError):
    """Task with given ID does not exist."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class ValidationError(TodoError):
    """Input validation failed."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")
```

### Repository Layer

#### `base.py`

```python
from abc import ABC, abstractmethod
from todo.domain.task import Task

class TaskRepository(ABC):
    """Abstract base for task persistence."""

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

#### `memory.py`

```python
class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation with dict storage."""

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        task.id = self._next_id
        self._next_id += 1
        self._tasks[task.id] = task
        return task

    # ... other methods with O(1) or O(n) complexity
```

### Service Layer

#### `task_service.py`

```python
class TaskService:
    """Business logic for task operations."""

    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: set[str] | None = None
    ) -> Task:
        """Create new task with validation."""
        # Validate title
        title = title.strip()
        if not title:
            raise ValidationError("title", "Title is required")
        if len(title) > 200:
            raise ValidationError("title", "Title must be 200 characters or less")

        # Validate description
        if len(description) > 1000:
            raise ValidationError("description", "Description must be 1000 characters or less")

        # Normalize and validate tags
        normalized_tags = self._normalize_tags(tags or set())

        task = Task(
            id=0,  # Will be assigned by repository
            title=title,
            description=description.strip(),
            priority=priority,
            tags=normalized_tags
        )
        return self._repository.add(task)

    def list_tasks(
        self,
        status: str | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search: str | None = None,
        sort_by: str | None = None
    ) -> list[Task]:
        """List tasks with filtering and sorting."""
        tasks = self._repository.get_all()

        # Apply filters
        if status == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif status == "completed":
            tasks = [t for t in tasks if t.completed]

        if priority:
            tasks = [t for t in tasks if t.priority == priority]

        if tag:
            tag_lower = tag.lower()
            tasks = [t for t in tasks if tag_lower in t.tags]

        if search:
            search_lower = search.lower()
            tasks = [t for t in tasks if
                     search_lower in t.title.lower() or
                     search_lower in t.description.lower()]

        # Apply sorting
        if sort_by:
            tasks = self._sort_tasks(tasks, sort_by)

        return tasks

    def get_stats(self) -> dict[str, int]:
        """Return task statistics."""
        all_tasks = self._repository.get_all()
        return {
            "total": len(all_tasks),
            "pending": sum(1 for t in all_tasks if not t.completed),
            "completed": sum(1 for t in all_tasks if t.completed)
        }

    def _normalize_tags(self, tags: set[str]) -> set[str]:
        """Normalize tags: lowercase, trim, dedupe, max 10."""
        normalized = {t.strip().lower() for t in tags if t.strip()}
        normalized = {t for t in normalized if len(t) <= 30}
        return set(list(normalized)[:10])

    def _sort_tasks(self, tasks: list[Task], sort_by: str) -> list[Task]:
        """Sort tasks by specified criteria."""
        if sort_by == "priority":
            return sorted(tasks, key=lambda t: t.priority, reverse=True)
        elif sort_by == "title":
            return sorted(tasks, key=lambda t: t.title.lower())
        elif sort_by == "created":
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)
        elif sort_by == "status":
            return sorted(tasks, key=lambda t: t.completed)
        return tasks
```

### CLI Layer

#### `app.py`

```python
class TodoCLI:
    """Main CLI application."""

    def __init__(self, service: TaskService):
        self._service = service
        self._handlers = self._setup_handlers()
        self._current_filter: FilterState | None = None
        self._current_sort: str = "id"

    def run(self) -> None:
        """Main application loop."""
        try:
            while True:
                self._display_menu()
                choice = self._get_input("Enter your choice (1-9): ")

                handler = self._handlers.get(choice)
                if handler:
                    handler()
                else:
                    self._display_error("Invalid option. Please select 1-9.")

        except KeyboardInterrupt:
            self._display_goodbye()

    def _setup_handlers(self) -> dict[str, Callable]:
        return {
            "1": self._view_tasks,
            "2": self._add_task,
            "3": self._update_task,
            "4": self._delete_task,
            "5": self._toggle_complete,
            "6": self._search_tasks,
            "7": self._filter_tasks,
            "8": self._sort_tasks,
            "9": self._exit,
        }
```

---

## Testing Strategy

### Unit Tests

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Task entity | `test_task.py` | Field defaults, validation, equality |
| Priority enum | `test_priority.py` | Ordering, display, string conversion |
| Exceptions | `test_exceptions.py` | Message formatting, inheritance |
| Repository | `test_repository.py` | All CRUD operations, edge cases |
| Service | `test_service.py` | Business logic, validation, filtering, sorting |

### Integration Tests

| Flow | Test | Acceptance Criteria |
|------|------|---------------------|
| Add → View | `test_add_and_view` | Task appears in list with correct data |
| Add → Complete → View | `test_complete_flow` | Status toggles correctly |
| Add → Update → View | `test_update_flow` | Changes persist |
| Add → Delete → View | `test_delete_flow` | Task removed from list |
| Filter + Sort | `test_filter_sort` | Correct subset and order |

---

## Error Handling Strategy

| Error Type | Handler | User Message |
|------------|---------|--------------|
| `ValidationError` | CLI layer | Display `field: message`, prompt retry |
| `TaskNotFoundError` | CLI layer | "Task with ID X not found" |
| `KeyboardInterrupt` | CLI app | "Goodbye!" and exit gracefully |
| Unknown exception | CLI app | "An error occurred. Please try again." |

**Never crash** - all exceptions caught at CLI level with user-friendly messages.

---

## Reusable Intelligence Assets

### Updated Skill: `todo-domain`

**Location**: `.claude/skills/todo-domain/`

**Changes Made**:
- Updated to version 2.0.0
- Added Priority enum with display format
- Added Intermediate Level features (priorities, tags, search, filter, sort)
- Added validation rules reference
- Updated reference/data-models.md with complete Phase I model

**Usage**: Automatically activated when implementing todo features.

---

## Complexity Tracking

> No Constitution Check violations requiring justification.

The architecture is intentionally simple:
- 4 layers (Domain, Repository, Services, CLI)
- Standard library only
- No abstractions beyond necessary (Repository pattern for future PostgreSQL swap)

---

## Implementation Order

**Recommended sequence for `/sp.tasks`:**

1. **Domain Layer** (no dependencies)
   - Priority enum
   - Task dataclass
   - Custom exceptions

2. **Repository Layer** (depends on Domain)
   - Abstract TaskRepository
   - InMemoryTaskRepository

3. **Service Layer** (depends on Repository + Domain)
   - TaskService with validation
   - CRUD operations
   - Query operations (filter, sort, search)

4. **CLI Layer** (depends on all layers)
   - Display utilities
   - Input validators
   - Menu handlers
   - Main application loop

5. **Integration & Polish**
   - Wire up components
   - End-to-end testing
   - Error handling refinement

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Scope creep to Advanced features | Constitution explicitly forbids; spec clearly scoped |
| Complex CLI state management | Keep filter/sort state simple; reset on exit |
| Unicode display issues | Test on multiple terminals; provide ASCII fallback |
| Performance with 1000 tasks | Dict storage ensures O(1) operations; tested |

---

## Success Metrics

From spec.md Success Criteria:

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| SC-001 | Add task in <30s | Manual timing test |
| SC-002 | View tasks in <5s | Manual timing test |
| SC-003 | Any operation in ≤3 selections | UI flow verification |
| SC-004 | 100 operations without error | Automated stress test |
| SC-005 | 100% invalid inputs handled | Error scenario tests |
| SC-006 | 5 Basic features functional | Feature acceptance tests |
| SC-007 to SC-012 | Intermediate features functional | Feature acceptance tests |
| SC-013 | Start in <2s | Manual timing test |
| SC-014 | 100 tasks display correctly | UI verification test |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation task breakdown
2. Execute tasks in recommended order
3. Create PHR after each significant milestone
4. Verify against spec acceptance criteria
5. Prepare demo video showcasing all 9 features

---

*Plan version: 1.0*
*Constitution check: PASS*
*Ready for: `/sp.tasks`*
