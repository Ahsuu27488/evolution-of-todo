---
name: todo-domain
description: Apply todo app domain knowledge and data models. Use when designing or implementing todo features.
version: 2.0.0
---

# Todo Domain Mastery Skill

## Theoretical Foundation

This skill encapsulates the **canonical todo/task domain model** used across all phases:
- **Core Entity**: Task with priority, status, tags, timestamps
- **CRUD Operations**: Create, Read, Update, Delete, Toggle Complete
- **Advanced Features**: Search, filter, sort, recurring tasks
- **User Isolation**: Multi-user with user-specific data

### Domain Model Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                         TODO DOMAIN DATA MODEL                                │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                          Task Entity                                │     │
│  │  ┌─────────────────┐  ┌─────────────────────────────────────────┐   │     │
│  │  │  Core Fields     │  │  Optional Fields (Phase I Enhanced)     │   │     │
│  │  │                 │  │                                         │   │     │
│  │  │ • id: int       │  │ • description: str (max 1000)           │   │     │
│  │  │ • title: str    │  │ • due_date: datetime                   │   │     │
│  │  │ • completed:    │  │ • recurrence_pattern: str (future)      │   │     │
│  │  │   bool          │  │ • tags: set[str] (max 10, 30 chars)     │   │     │
│  │  │ • created_at:   │  │ • user_id: str (Phase II+)             │   │     │
│  │  │   datetime      │  │                                         │   │     │
│  │  └─────────────────┘  └─────────────────────────────────────────┘   │     │
│  │                                                                  │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │                  Priority Enum                               │ │     │
│  │  │  HIGH (3)    >    MEDIUM (2)    >    LOW (1)                │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## When to Use This Skill

Activation triggers:
- Implementing todo/task features (add, delete, update, view, complete)
- Designing data models for tasks
- Creating API endpoints for task management
- Implementing filters, search, or sorting
- Validating task input

## Domain Model Specification

### Core Task Entity

```python
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Optional, Set

class Priority(IntEnum):
    """Task priority with numeric ordering."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class Task:
    """Canonical Task entity - valid across all phases."""
    id: int                    # Auto-assigned, sequential, unique
    title: str                 # Required, 1-200 chars
    description: str = ""      # Optional, max 1000 chars
    priority: Priority = Priority.MEDIUM
    tags: set[str] = None      # Max 10 tags, each max 30 chars
    completed: bool = False    # Toggleable status
    created_at: datetime = None  # Auto-assigned on creation
```

### Validation Rules

| Field | Rules |
|-------|-------|
| `id` | Auto-generated, unique, never reused |
| `title` | Required, 1-200 chars, trimmed |
| `description` | Optional, max 1000 chars |
| `priority` | One of: HIGH, MEDIUM, LOW |
| `tags` | Max 10 tags, each max 30 chars, lowercase, unique |
| `completed` | Boolean, toggleable |

## CRUD Operations

### Create Task

```python
def create_task(
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    tags: set[str] = None
) -> Task:
    """
    Create a new task.

    Validation:
    - Title trimmed and validated (1-200 chars)
    - Tags deduplicated and limited to 10
    - ID auto-generated
    - created_at set to now

    Returns: The created Task with generated ID
    """
    task_id = generate_id()
    normalized_tags = normalize_tags(tags or set())

    return Task(
        id=task_id,
        title=title.strip(),
        description=description.strip(),
        priority=priority,
        tags=normalized_tags,
        completed=False,
        created_at=datetime.utcnow()
    )
```

### Read/Filter Tasks

```python
def list_tasks(
    status: str = "all",      # all, pending, completed
    priority: Priority = None, # HIGH, MEDIUM, LOW, or None
    tag: str = None,           # Filter by tag
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> list[Task]:
    """
    List tasks with optional filters and sorting.

    Filter combinations:
    - status + priority: Tasks matching both
    - tag only: Tasks with that tag
    - No filters: All tasks

    Sorting:
    - created_at, priority, title
    - asc or desc order
    """
    tasks = get_all_tasks()

    # Apply filters
    if status != "all":
        tasks = filter_by_status(tasks, status)
    if priority:
        tasks = filter_by_priority(tasks, priority)
    if tag:
        tasks = filter_by_tag(tasks, tag)

    # Apply sorting
    return sort_tasks(tasks, sort_by, sort_order)
```

### Update Task

```python
def update_task(
    task_id: int,
    title: str = None,
    description: str = None,
    priority: Priority = None,
    tags: set[str] = None,
    completed: bool = None
) -> Task:
    """
    Update an existing task.

    Only updates provided fields (partial update).
    Returns error if task_id not found.
    """
    task = get_task(task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip()
    if priority is not None:
        task.priority = priority
    if tags is not None:
        task.tags = normalize_tags(tags)
    if completed is not None:
        task.completed = completed

    return task
```

### Delete Task

```python
def delete_task(task_id: int) -> bool:
    """
    Delete a task by ID.

    Returns: True if deleted, False if not found
    """
    task = get_task(task_id)
    if not task:
        return False

    remove_task(task_id)
    return True
```

### Toggle Complete

```python
def toggle_complete(task_id: int) -> Task:
    """
    Toggle task completion status.

    If pending → mark completed
    If completed → mark pending

    Returns: The updated task
    """
    task = get_task(task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    task.completed = not task.completed
    return task
```

## Advanced Features

### Search

```python
def search_tasks(query: str) -> list[Task]:
    """
    Case-insensitive search in title and description.

    Matches: Substring anywhere in title or description
    Returns: Tasks matching the search query
    """
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    return [
        task for task in get_all_tasks()
        if query_lower in task.title.lower()
        or query_lower in task.description.lower()
    ]
```

### Filter Combinations

```python
def filter_tasks(
    status: str = "all",
    priority: Priority = None,
    tag: str = None,
    search: str = None
) -> list[Task]:
    """
    Apply multiple filters simultaneously.

    Filter logic: AND between different filter types
    - status AND priority AND tag AND search

    Example:
        status="completed", priority="HIGH"
        Returns: High priority tasks that are completed
    """
    tasks = get_all_tasks()

    if status != "all":
        tasks = [t for t in tasks if
            (status == "completed" and t.completed) or
            (status == "pending" and not t.completed)]

    if priority:
        tasks = [t for t in tasks if t.priority == priority]

    if tag:
        tasks = [t for t in tasks if tag.lower() in [t.lower() for t in t.tags]]

    if search:
        search_lower = search.lower()
        tasks = [t for t in tasks if
            search_lower in t.title.lower() or
            search_lower in t.description.lower()]

    return tasks
```

### Sorting

```python
def sort_tasks(tasks: list[Task], by: str, order: str) -> list[Task]:
    """
    Sort tasks by field and order.

    Fields: created_at, priority, title
    Order: asc, desc

    Priority sort: HIGH > MEDIUM > LOW (descending by value)
    """
    reverse = order == "desc"

    if by == "priority":
        # Sort by priority value (higher = more important)
        return sorted(tasks, key=lambda t: t.priority.value, reverse=reverse)
    elif by == "title":
        return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)
    else:  # created_at
        return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
```

## Tag Management

```python
def normalize_tags(tags: set[str]) -> set[str]:
    """
    Normalize tags to canonical form.

    Rules:
    - Limit to 10 tags
    - Each tag max 30 chars
    - Lowercase
    - Trim whitespace
    - Remove duplicates
    """
    normalized = set()

    for tag in tags:
        tag = tag.strip().lower()[:30]
        if tag:
            normalized.add(tag)

    # Limit to 10 tags (deterministic selection)
    if len(normalized) > 10:
        return set(list(normalized)[:10])

    return normalized

def format_tags(tags: set[str]) -> str:
    """Format tags for display: #tag1 #tag2 #tag3"""
    return " ".join(f"#{tag}" for tag in sorted(tags))
```

## Display Format

```
┌─────────────────────────────────────────────────────────────────┐
│ Task ID: 42               [HIGH]              [✓]               │
├─────────────────────────────────────────────────────────────────┤
│ Title: Buy groceries for the week                               │
│                                                                 │
│ Description: Get milk, eggs, bread, and vegetables               │
│                                                                 │
│ Tags: #groceries #weekly                                        │
│                                                                 │
│ Created: 2025-01-09 14:30 UTC                                   │
│ Status: Pending                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase-Specific Rules

| Phase | Storage | User Isolation |
|-------|---------|----------------|
| I | In-memory (`dict[int, Task]`) | None (single user) |
| II+ | Database (PostgreSQL/Neon) | Required (`user_id` field) |
| III | Database + MCP tools | Required |
| V | Database + recurrence | Required |

## Common Operations by User Intent

| User Intent | Operation |
|-------------|------------|
| "Add task: buy milk" | `create_task(title="buy milk")` |
| "Show my tasks" | `list_tasks()` |
| "Complete task 5" | `toggle_complete(5)` |
| "Delete task 3" | `delete_task(3)` |
| "Show high priority" | `list_tasks(priority=HIGH)` |
| "Search for grocery" | `search_tasks("grocery")` |
| "Show pending" | `list_tasks(status="pending")` |
| "Sort by priority" | `list_tasks(sort_by="priority", sort_order="desc")` |

## Error Handling

```python
class TaskError(Exception):
    """Base exception for task operations."""
    pass

class TaskNotFoundError(TaskError):
    """Raised when a task ID doesn't exist."""
    pass

class TaskValidationError(TaskError):
    """Raised when task data is invalid."""
    pass

# Usage
def get_task_or_raise(task_id: int) -> Task:
    task = get_task(task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")
    return task
```
