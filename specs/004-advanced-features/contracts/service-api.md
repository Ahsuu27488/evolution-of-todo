# Service API Contract: Advanced Level Features

**Feature**: 004-advanced-features
**Date**: 2025-12-27
**Layer**: TaskService (Business Logic)

---

## Overview

This document defines the API contract for the TaskService layer extensions required for Advanced Level features. Since Phase I is a console application without HTTP APIs, these contracts define the **Python method signatures** that the CLI layer will invoke.

---

## Extended Methods

### 1. create_task() - Extended

```python
def create_task(
    self,
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    tags: set[str] | None = None,
    due_date: date | None = None,           # NEW
    recurrence: Recurrence = Recurrence.NONE # NEW
) -> Task:
    """Create a new task with validation.

    Args:
        title: Task title (required, 1-200 chars)
        description: Optional description (max 1000 chars)
        priority: Priority level (default: MEDIUM)
        tags: Optional set of tags
        due_date: Optional deadline date (NEW)
        recurrence: Repeat pattern (default: NONE) (NEW)

    Returns:
        The created task with assigned ID

    Raises:
        ValidationError: If validation fails
    """
```

**Contract**:
- `due_date` accepts `date` object or `None`
- `recurrence` accepts any `Recurrence` enum value
- Recurrence without due_date is allowed (dormant until due_date set)

---

### 2. update_task() - Extended

```python
def update_task(
    self,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: Priority | None = None,
    tags: set[str] | None = None,
    due_date: date | None | "REMOVE" = None,  # NEW: special sentinel for removal
    recurrence: Recurrence | None = None       # NEW
) -> Task:
    """Update an existing task (partial update).

    Args:
        task_id: The task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        tags: New tags - replaces existing (optional)
        due_date: New due date, None to skip, or sentinel to remove (NEW)
        recurrence: New recurrence pattern (optional) (NEW)

    Returns:
        The updated task

    Raises:
        TaskNotFoundError: If task doesn't exist
        ValidationError: If validation fails
    """
```

**Contract**:
- Passing `None` for `due_date` means "don't change"
- To remove due_date, pass a special sentinel (implementation choice: could be empty string from CLI)
- `recurrence=None` means "don't change"

---

### 3. toggle_complete() - Extended

```python
def toggle_complete(self, task_id: int) -> tuple[Task, Task | None]:
    """Toggle a task's completion status.

    For recurring tasks being completed:
    - Current task is marked complete
    - New task occurrence is created with next due date

    Args:
        task_id: The task to toggle

    Returns:
        Tuple of (updated_task, new_occurrence_or_None)
        - new_occurrence is None if task is not recurring or being uncompleted

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
```

**Contract**:
- Return type changes from `Task` to `tuple[Task, Task | None]`
- Second element is the newly created recurring task, or `None`
- New task only created when:
  1. Task is being marked complete (not incomplete)
  2. Task has `recurrence != NONE`
  3. Task has `due_date != None`

---

### 4. list_tasks() - Extended

```python
def list_tasks(
    self,
    status: str | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    due_date_filter: str | None = None  # NEW
) -> list[Task]:
    """List tasks with optional filtering and sorting.

    Args:
        status: Filter by "pending" or "completed"
        priority: Filter by priority level
        tag: Filter by tag (case-insensitive)
        search: Search keyword in title/description
        sort_by: Sort field: "id", "priority", "title", "created", "status", "due_date" (NEW)
        due_date_filter: Filter by due date: "overdue", "today", "this_week", "no_deadline" (NEW)

    Returns:
        List of matching tasks (may be empty)
    """
```

**Contract**:
- New `due_date_filter` values:
  - `"overdue"`: `due_date < today`
  - `"today"`: `due_date == today`
  - `"this_week"`: `today <= due_date <= today + 7 days`
  - `"no_deadline"`: `due_date is None`
- New `sort_by` value: `"due_date"` (ascending, nulls last)

---

## New Functions

### 5. calculate_next_due_date()

```python
def calculate_next_due_date(due_date: date, recurrence: Recurrence) -> date | None:
    """Calculate the next occurrence date based on recurrence pattern.

    Args:
        due_date: Current due date
        recurrence: Recurrence pattern

    Returns:
        Next due date, or None if recurrence is NONE

    Notes:
        - Always returns a date >= today (skips past dates)
        - Monthly handles day overflow (Jan 31 -> Feb 28)
    """
```

**Contract**:
- Returns `None` if `recurrence == NONE`
- Returned date is always in the future (>= today)
- For monthly: clamps to last day of month if necessary

---

## CLI Layer Contracts

### 6. get_due_date_input()

```python
def get_due_date_input(prompt: str = "Enter due date (YYYY-MM-DD, or press Enter to skip): ") -> date | None:
    """Get and validate due date input from user.

    Args:
        prompt: The prompt to display

    Returns:
        Parsed date or None if skipped

    Notes:
        - Empty input returns None
        - Invalid format: prompts again with error message
        - Invalid date: prompts again with error message
    """
```

---

### 7. get_recurrence_input()

```python
def get_recurrence_input(prompt: str = "Set recurrence? (none/daily/weekly/monthly) [none]: ") -> Recurrence:
    """Get and validate recurrence pattern input from user.

    Args:
        prompt: The prompt to display

    Returns:
        Recurrence enum value (defaults to NONE)

    Notes:
        - Empty input returns NONE
        - Case-insensitive matching
        - Invalid input: prompts again with error message
    """
```

---

### 8. format_due_date_display()

```python
def format_due_date_display(due_date: date | None, recurrence: Recurrence = Recurrence.NONE) -> str:
    """Format due date for display with color codes and recurrence indicator.

    Args:
        due_date: The due date or None
        recurrence: The recurrence pattern

    Returns:
        Formatted string with ANSI color codes

    Examples:
        - "(no deadline)"              [gray]
        - "Overdue by 2d"              [red]
        - "Due today! (Daily)"         [yellow]
        - "In 5d (2025-01-05) (Weekly)" [gray]
    """
```

---

## Error Handling

### ValidationError Extensions

| Field | Error Condition | Message |
|-------|-----------------|---------|
| `due_date` | Invalid format | "Due date must be in YYYY-MM-DD format" |
| `due_date` | Invalid date | "Invalid date. Please check month/day values." |
| `recurrence` | Invalid value | "Recurrence must be none, daily, weekly, or monthly" |

---

## Return Type Summary

| Method | Returns | Changes |
|--------|---------|---------|
| `create_task()` | `Task` | No change |
| `update_task()` | `Task` | No change |
| `toggle_complete()` | `tuple[Task, Task \| None]` | **CHANGED** |
| `list_tasks()` | `list[Task]` | No change |
| `delete_task()` | `bool` | No change |
| `get_task()` | `Task` | No change |
| `get_stats()` | `dict[str, int]` | No change |
