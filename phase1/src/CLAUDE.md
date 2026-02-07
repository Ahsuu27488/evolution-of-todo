# src/ — Phase I Console Application

**Claude Code Context** for the in-memory Python console todo application (Phase I).

## Project Purpose

This is the **foundation phase** of a 5-phase evolution. The code here is designed for **reuse** in Phase II (FastAPI backend) and demonstrates clean architecture patterns that will scale to the full-stack application.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │
│  │   app    │─▶│ handlers  │─▶│ display  │─▶│validators │  │
│  └──────────┘  └───────────┘  └──────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
│                    ┌──────────────────┐                     │
│                    │  TaskService    │                     │
│                    │  - Validation    │                     │
│                    │  - Business      │                     │
│                    │  - Queries       │                     │
│                    └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                         │
│  ┌─────────────┐          ┌──────────────────┐             │
│  │ TaskRepository◀────────│ InMemoryTaskRepo │             │
│  │   (ABC)     │          │                  │             │
│  └─────────────┘          └──────────────────┘             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                           │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────┐       │
│  │  Task    │  │  Priority  │  │   Recurrence     │       │
│  │ (entity) │  │  (IntEnum) │  │     (Enum)       │       │
│  └──────────┘  └────────────┘  └──────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              TodoError Hierarchy                     │  │
│  │  TodoError ──┬──▶ TaskNotFoundError                │  │
│  │               └──▶ ValidationError                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Task Implementation Guidelines (CRITICAL for Long-Running Sessions)

**IMPORTANT**: When implementing multiple tasks (e.g., via `/sp.implement`), follow this pattern to prevent context loss and hallucinations during session compactions:

1. **Complete ONE task at a time** — Finish implementing, testing, and verifying a single task before moving to the next
2. **Mark task as complete immediately** — Update task status in `tasks.md` to `completed` before starting the next task
3. **Re-read tasks.md after each task** — After marking complete, re-read `tasks.md` to refresh context on remaining tasks
4. **Verify code state** — Before proceeding, confirm the current codebase state matches expected changes
5. **Commit after logical checkpoints** — After every 2-3 completed tasks or when a milestone is reached

**Why this matters:**
- Session compaction after ~200K tokens compresses conversation history
- Without checkpoints, the agent loses track of:
  - Which tasks were already completed
  - Current codebase state
  - Decisions made during implementation
- This leads to hallucinations, repeated work, or contradicting changes

**Mandatory Pattern:**
```
1. Read task details from tasks.md
2. Implement task
3. Test/verify implementation
4. Update tasks.md: change status to "completed"
5. Re-read tasks.md to see remaining work
6. Proceed to next task
```

## Debugging Workflow

**IMPORTANT**: Always use the `superpowers:systematic-debugging` skill when encountering bugs, errors, or unexpected behavior in the console application.

### When to Use Systematic Debugging

Invoke this skill before attempting to fix:
- CLI menu navigation issues
- Task CRUD operation failures
- Input validation errors
- Recurrence calculation bugs
- Display/output formatting problems

### Debugging Console Application Issues

The systematic debugging skill will help you:

1. **Gather Context**: Check error messages, stack traces, user input
2. **Check State**: Verify repository state, service layer behavior
3. **Form Hypotheses**: Based on error patterns and code flow
4. **Test Isolated**: Run specific functions in Python REPL
5. **Implement Fix**: Make targeted changes based on evidence

**Phase I-Specific Debugging Tips**:
- Use Python debugger (`pdb.set_trace()`) for stepping through code
- Test repository methods directly in REPL
- Verify input validators are returning expected types
- Check sentinel value handling (`_REMOVE_DUE_DATE`)
- Verify enum display values are formatted correctly

---

## Key File Locations

| File | Purpose | Key Details |
|------|---------|-------------|
| `main.py` | Entry point | Demo data loader, app initialization |
| `todo/domain/task.py` | Core entity | `Task` dataclass, `Priority`, `Recurrence` enums |
| `todo/domain/exceptions.py` | Domain errors | Base `TodoError`, `TaskNotFoundError`, `ValidationError` |
| `todo/repository/base.py` | Repository contract | Abstract `TaskRepository` with 6 methods |
| `todo/repository/memory.py` | In-memory storage | `InMemoryTaskRepository` — O(1) lookup via dict |
| `todo/services/task_service.py` | Business logic | Validation, CRUD, filtering, sorting, recurrence |
| `todo/cli/app.py` | CLI orchestration | `TodoCLI` class, filter/sort state, handler routing |
| `todo/cli/handlers.py` | Menu handlers | 9 handler functions for menu options |
| `todo/cli/display.py` | Terminal output | ANSI colors, table formatting, due date display |
| `todo/cli/validators.py` | Input validation | All user input parsing and validation functions |

## Architectural Patterns

### Repository Pattern

The abstract `TaskRepository` enables swapping storage backends without changing service code:

```python
# Phase I: In-memory
repository = InMemoryTaskRepository()

# Phase II: Database (drop-in replacement)
repository = SQLModelTaskRepository(engine)

# Service code unchanged
service = TaskService(repository)
```

### Service Layer Reuse

`TaskService` contains **all business logic** and is designed for reuse in FastAPI:

- Validation rules (title length, tag limits)
- Recurrence calculation logic
- Filtering and sorting
- All methods return domain entities, not CLI-specific types

### Handler Pattern

Menu options map to handlers via dictionary lookup in `app.py:71-81`:

```python
self._handlers = {
    "1": view_tasks_handler,
    "2": add_task_handler,
    # ... etc
}
```

## Coding Conventions

### Type Hints

All functions use full type hints:

```python
def create_task(
    self,
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    tags: set[str] | None = None,
    due_date: date | None = None,
    recurrence: Recurrence = Recurrence.NONE,
) -> Task:
```

### Domain Exceptions

All domain errors inherit from `TodoError`:

```python
raise TaskNotFoundError(task_id)  # Includes task_id attribute
raise ValidationError("title", "Title is required")  # Includes field, message
```

### Sentinel Values

For distinguishing "None" from "don't change", a sentinel object is used:

```python
_REMOVE_DUE_DATE = object()  # In task_service.py:98

# Usage:
service.update_task(task_id, due_date=TaskService._REMOVE_DUE_DATE)
```

### Enum Display Pattern

Enums provide both user-facing display and internal value:

```python
class Priority(IntEnum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1

    @property
    def display(self) -> str:
        return f"[{self.name}]"  # "[HIGH]", "[MEDIUM]", etc.
```

## Data Flow Example: Adding a Task

```
User Input (validators.py)
    │
    ▼
get_title_input() → validates 1-200 chars
    │
    ▼
add_task_handler() → calls service.create_task()
    │
    ▼
TaskService.create_task() → validates, normalizes tags
    │
    ▼
repository.add(task) → assigns ID, stores
    │
    ▼
display.print_success() → shows result
```

## Recurrence Logic

When a recurring task is marked complete, a new occurrence is created:

1. Original task marked `completed = True`
2. Next due date calculated based on recurrence pattern
3. New task created with same properties but new due date
4. Calendar overflow handled (Jan 31 → Feb 28)

**Location**: `task_service.py:174-216` (toggle_complete method)

## Extension Points for Phase II

### Database Integration

Replace `InMemoryTaskRepository` with SQLModel-based implementation:

```python
class SQLModelTaskRepository(TaskRepository):
    def __init__(self, engine):
        self._engine = engine

    def add(self, task: Task) -> Task:
        with Session(self._engine) as session:
            db_task = DBTask.from_domain(task)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task.to_domain()
```

### FastAPI Route Integration

Service methods map directly to API endpoints:

| Service Method | FastAPI Endpoint |
|----------------|------------------|
| `create_task()` | `POST /api/tasks` |
| `get_task(id)` | `GET /api/tasks/{id}` |
| `list_tasks(filters)` | `GET /api/tasks` |
| `update_task(id, ...)` | `PUT /api/tasks/{id}` |
| `delete_task(id)` | `DELETE /api/tasks/{id}` |
| `toggle_complete(id)` | `PATCH /api/tasks/{id}/complete` |

## Important Constraints

- **No external dependencies** in domain layer (only Python stdlib)
- **Repository interface** must not change when adding DB implementation
- **Service layer** must remain CLI-agnostic for FastAPI reuse
- **Task IDs are never reused** after deletion (sequential counter only increments)
