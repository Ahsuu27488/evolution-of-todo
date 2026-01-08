# Research: Phase 1 Console App Technical Decisions

**Feature**: 003-phase1-console-app
**Date**: 2025-12-27
**Purpose**: Resolve technical decisions and research best practices before implementation

---

## Research Questions

### RQ-001: Python Project Structure for Clean Architecture

**Question**: What's the optimal Python project structure for a CLI app that will evolve into a web API (Phase II) and MCP tools (Phase III)?

**Research Findings**:

1. **Clean Architecture Layers**:
   - **Domain Layer** (innermost): Business entities and logic - no dependencies
   - **Use Cases Layer**: Application-specific business rules
   - **Interface Adapters**: Convert data between use cases and external interfaces
   - **Frameworks/Drivers** (outermost): CLI, web frameworks, databases

2. **Python Best Practice Structure**:
   ```
   src/
   ├── todo/
   │   ├── __init__.py
   │   ├── domain/           # Entities, value objects
   │   │   ├── __init__.py
   │   │   ├── task.py       # Task entity
   │   │   └── enums.py      # Priority enum
   │   ├── services/         # Use cases / business logic
   │   │   ├── __init__.py
   │   │   └── task_service.py
   │   ├── repository/       # Data access interface
   │   │   ├── __init__.py
   │   │   ├── base.py       # Abstract repository
   │   │   └── memory.py     # In-memory implementation
   │   └── cli/              # CLI presentation layer
   │       ├── __init__.py
   │       ├── app.py        # Main CLI app
   │       └── handlers.py   # Menu handlers
   └── main.py               # Entry point
   ```

**Decision**: Adopt layered architecture with domain, services, repository, and cli packages.

**Rationale**:
- Domain and services layers can be reused directly in Phase II (FastAPI) and Phase III (MCP tools)
- Repository pattern allows swapping in-memory for PostgreSQL in Phase II
- CLI layer is isolated, easy to replace with web/API layer

**Alternatives Rejected**:
- Flat structure (all in one file): Won't scale to later phases
- MVC pattern: Better for web apps, domain layer concept needed for evolution

---

### RQ-002: In-Memory Data Storage Strategy

**Question**: What data structures best support the task operations with priorities, tags, and sorting?

**Research Findings**:

1. **Primary Storage**: `dict[int, Task]` - O(1) lookup by ID
2. **ID Generation**: Auto-incrementing counter, never reused
3. **Task Entity**: Dataclass or Pydantic-like class with validation

**Decision**: Use `dict[int, Task]` with `@dataclass` for Task entity.

**Rationale**:
- Dictionary provides O(1) access by ID for get/update/delete
- Dataclass is standard library (no dependencies), supports type hints
- Fields can include: id, title, description, priority (Enum), tags (set), completed, created_at

**Alternatives Rejected**:
- List of tasks: O(n) lookup by ID
- SQLite in-memory: Violates "no external dependencies" per constitution

---

### RQ-003: CLI Menu Implementation Pattern

**Question**: What pattern provides clean, extensible menu handling?

**Research Findings**:

1. **Command Pattern**: Each menu option is a command object with execute()
2. **Handler Pattern**: Dictionary mapping menu choices to handler functions
3. **Loop Pattern**: While loop with input validation

**Decision**: Use handler pattern with dictionary dispatch.

**Rationale**:
- Simple, readable, no external dependencies
- Easy to add new options (just add to dictionary)
- Each handler function maps to a use case in the service layer

**Implementation Sketch**:
```python
handlers = {
    "1": view_tasks_handler,
    "2": add_task_handler,
    "3": update_task_handler,
    # ...
}

while True:
    choice = display_menu_and_get_input()
    handler = handlers.get(choice)
    if handler:
        handler(task_service)
```

**Alternatives Rejected**:
- click/typer library: External dependency, violates constitution
- Class-based commands: Over-engineered for 9 menu options

---

### RQ-004: Priority Enum Design

**Question**: How to implement priority levels with proper ordering for sorting?

**Research Findings**:

1. **IntEnum**: Integer-based enum, supports comparison operators
2. **Order**: HIGH=3, MEDIUM=2, LOW=1 (higher value = higher priority)

**Decision**: Use `IntEnum` for Priority with descending sort order.

**Rationale**:
- IntEnum from standard library
- Comparison operators work naturally (HIGH > MEDIUM > LOW)
- String representation for display ("high", "medium", "low")

**Implementation**:
```python
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __str__(self) -> str:
        return self.name.lower()
```

---

### RQ-005: Tags Implementation

**Question**: How to store and validate tags efficiently?

**Research Findings**:

1. **Set vs List**: Set prevents duplicates automatically
2. **Normalization**: Lowercase, stripped whitespace
3. **Validation**: Max 10 tags, each max 30 characters

**Decision**: Use `set[str]` with normalization on input.

**Rationale**:
- Set prevents duplicates (FR-020)
- Efficient membership testing for filtering
- Immutable frozenset not needed since we allow tag updates

**Parsing Logic**:
```python
def parse_tags(input_str: str) -> set[str]:
    """Parse comma-separated tags, normalize, deduplicate."""
    if not input_str.strip():
        return set()
    tags = {tag.strip().lower() for tag in input_str.split(",")}
    return {t for t in tags if t}[:10]  # Max 10 tags
```

---

### RQ-006: Search and Filter Implementation

**Question**: How to efficiently implement search and multi-criteria filtering?

**Research Findings**:

1. **Search**: Case-insensitive substring match in title and description
2. **Filter**: Chain predicates for status, priority, tag
3. **Performance**: Iterate once with combined predicate

**Decision**: Use generator with predicate functions.

**Rationale**:
- Single pass through tasks
- Composable filters
- Memory efficient for large lists

**Implementation Sketch**:
```python
def filter_tasks(
    tasks: Iterable[Task],
    status: str | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
    search: str | None = None
) -> list[Task]:
    """Filter tasks by multiple criteria."""
    result = list(tasks)
    if status == "pending":
        result = [t for t in result if not t.completed]
    if priority:
        result = [t for t in result if t.priority == priority]
    if tag:
        result = [t for t in result if tag.lower() in t.tags]
    if search:
        search_lower = search.lower()
        result = [t for t in result if
                  search_lower in t.title.lower() or
                  search_lower in (t.description or "").lower()]
    return result
```

---

### RQ-007: Sorting Implementation

**Question**: How to implement multi-criteria sorting efficiently?

**Research Findings**:

1. **Built-in sorted()**: Stable sort with key function
2. **Multiple criteria**: Tuple keys for multi-field sort
3. **Reverse handling**: Different for each sort type

**Decision**: Use sorted() with key functions and reverse parameter.

**Rationale**:
- Built-in sorted() is efficient (Timsort)
- Key functions are composable
- No external dependencies

**Implementation**:
```python
def sort_tasks(tasks: list[Task], sort_by: str, reverse: bool = False) -> list[Task]:
    key_funcs = {
        "priority": lambda t: t.priority,
        "title": lambda t: t.title.lower(),
        "created": lambda t: t.created_at,
        "status": lambda t: t.completed,
    }
    key_func = key_funcs.get(sort_by, lambda t: t.id)
    # For priority, high should come first (reverse=True)
    if sort_by == "priority":
        reverse = True
    return sorted(tasks, key=key_func, reverse=reverse)
```

---

### RQ-008: Error Handling Strategy

**Question**: How to handle errors gracefully in CLI context?

**Research Findings**:

1. **Custom Exceptions**: Domain-specific exceptions for business errors
2. **Display Layer**: Catch exceptions, display user-friendly messages
3. **Never Crash**: All exceptions caught at CLI layer

**Decision**: Custom exception hierarchy with CLI-level catch-all.

**Rationale**:
- Domain exceptions communicate intent
- CLI layer provides user-friendly messages
- Ctrl+C handled with signal handler

**Exception Hierarchy**:
```python
class TodoError(Exception):
    """Base exception for todo app."""
    pass

class TaskNotFoundError(TodoError):
    """Raised when task ID doesn't exist."""
    pass

class ValidationError(TodoError):
    """Raised when input validation fails."""
    pass
```

---

### RQ-009: Reusable Intelligence Integration

**Question**: How to structure code to maximize reuse as Claude Code Skills/Agents?

**Research Findings**:

1. **Skills**: Lightweight, markdown-based, auto-activated
2. **Domain Knowledge**: Can be extracted as `todo-domain` skill
3. **Testing Patterns**: Can inform test generation

**Decision**: Create `todo-domain` skill capturing business rules.

**Rationale**:
- Constitution mandates +200 bonus for Reusable Intelligence
- Domain rules (priorities, tags, validation) are reusable across all phases
- Skill can guide Claude Code in maintaining consistency

**Skill Content**:
- Task entity definition and validation rules
- Priority semantics and display format
- Tag parsing and normalization rules
- Error types and handling patterns

---

## Summary of Decisions

| Question | Decision | Key Rationale |
|----------|----------|---------------|
| Project Structure | Layered (domain/services/repository/cli) | Enables Phase II-III reuse |
| Data Storage | `dict[int, Task]` with `@dataclass` | O(1) lookup, standard library |
| CLI Pattern | Handler dictionary dispatch | Simple, extensible, no deps |
| Priority | `IntEnum` (LOW=1, MEDIUM=2, HIGH=3) | Natural comparison support |
| Tags | `set[str]` with normalization | Auto-dedup, efficient filtering |
| Search/Filter | Predicate chain with list comprehension | Single pass, composable |
| Sorting | `sorted()` with key functions | Built-in, efficient |
| Errors | Custom exception hierarchy | Clear intent, graceful handling |
| Reusable Intelligence | Extract `todo-domain` skill | +200 bonus, cross-phase consistency |

---

## Resolved Technical Context

| Aspect | Value |
|--------|-------|
| **Language/Version** | Python 3.13+ |
| **Primary Dependencies** | Standard library only (dataclasses, enum, datetime) |
| **Storage** | In-memory dict[int, Task] |
| **Testing** | pytest (dev dependency only) |
| **Target Platform** | Linux/macOS/Windows console |
| **Project Type** | Single project |
| **Performance Goals** | <100ms for any operation on 1000 tasks |
| **Constraints** | <50MB memory, no external runtime dependencies |
| **Scale/Scope** | Up to 1000 tasks per session |

---

*Research completed: 2025-12-27*
*All NEEDS CLARIFICATION items: RESOLVED*
