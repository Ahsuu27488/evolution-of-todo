# Data Model: Advanced Level Features

**Feature**: 004-advanced-features
**Date**: 2025-12-27
**Status**: Design Complete

---

## Entity Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Task                                 │
├─────────────────────────────────────────────────────────────┤
│ id: int                     [PK, auto-increment]            │
│ title: str                  [required, 1-200 chars]         │
│ description: str            [optional, max 1000 chars]      │
│ priority: Priority          [enum, default: MEDIUM]         │
│ tags: set[str]              [max 10, each max 30 chars]     │
│ completed: bool             [default: False]                │
│ created_at: datetime        [auto-assigned]                 │
│ ─────────────────────────── NEW FIELDS ─────────────────── │
│ due_date: date | None       [optional, YYYY-MM-DD]          │
│ recurrence: Recurrence      [enum, default: NONE]           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Recurrence (NEW)                        │
├─────────────────────────────────────────────────────────────┤
│ NONE    = "none"    → No recurrence (default)               │
│ DAILY   = "daily"   → Repeat every day                      │
│ WEEKLY  = "weekly"  → Repeat every 7 days                   │
│ MONTHLY = "monthly" → Repeat same day next month            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Priority (EXISTING)                        │
├─────────────────────────────────────────────────────────────┤
│ LOW    = 1                                                   │
│ MEDIUM = 2                                                   │
│ HIGH   = 3                                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity: Task (Extended)

### Fields

| Field | Type | Required | Default | Validation | Notes |
|-------|------|----------|---------|------------|-------|
| `id` | `int` | Yes (auto) | Auto-increment | Unique, positive | Never reused |
| `title` | `str` | Yes | - | 1-200 chars, non-empty after trim | Required |
| `description` | `str` | No | `""` | Max 1000 chars | Trimmed |
| `priority` | `Priority` | No | `MEDIUM` | Valid enum value | IntEnum |
| `tags` | `set[str]` | No | `set()` | Max 10 items, each max 30 chars | Lowercase, trimmed |
| `completed` | `bool` | No | `False` | - | Toggle via service |
| `created_at` | `datetime` | Yes (auto) | UTC now | - | Immutable |
| `due_date` | `date \| None` | No | `None` | Valid date if provided | **NEW** |
| `recurrence` | `Recurrence` | No | `NONE` | Valid enum value | **NEW** |

### Business Rules

1. **Due Date**
   - Must be in `YYYY-MM-DD` format when provided
   - Past dates are valid (immediately shown as "overdue")
   - Can be set, updated, or removed at any time
   - Independent of completion status

2. **Recurrence**
   - Only meaningful when `due_date` is set
   - If `due_date` is `None`, recurrence has no effect
   - Setting recurrence without due_date: allowed but dormant
   - Removing due_date preserves recurrence setting (dormant)

3. **Recurring Task Completion**
   - When task with `recurrence != NONE` and `due_date != None` is marked complete:
     - Current task stays completed
     - New task is created with:
       - Same: title, description, priority, tags, recurrence
       - New: id (auto), completed=False, created_at=now
       - Calculated: due_date = next occurrence date
   - New occurrence due_date is always in the future
   - If calculated date would be in past, advance to next valid future date

4. **Recurring Task Deletion**
   - Deleting a recurring task deletes only that occurrence
   - No automatic creation of replacement
   - User must explicitly create new recurring task if needed

---

## Enum: Recurrence (NEW)

### Definition

```python
from enum import Enum

class Recurrence(Enum):
    """Task recurrence patterns for automatic scheduling."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        """Return lowercase name for user input matching."""
        return self.value

    @property
    def display(self) -> str:
        """Display format for CLI: (Daily), (Weekly), etc."""
        if self == Recurrence.NONE:
            return ""
        return f"({self.value.title()})"
```

### Next Date Calculation

| Pattern | Formula | Edge Cases |
|---------|---------|------------|
| `NONE` | N/A - no next date | - |
| `DAILY` | `due_date + 1 day` | None |
| `WEEKLY` | `due_date + 7 days` | None |
| `MONTHLY` | Same day next month | Day overflow: clamp to last day |

### Monthly Edge Case Examples

| Original | Next Month Has | Calculated |
|----------|----------------|------------|
| Jan 31 | Feb 28/29 | Feb 28 (or 29 in leap year) |
| Mar 31 | Apr 30 | Apr 30 |
| Aug 30 | Sep 30 | Sep 30 |
| Oct 15 | Nov 30 | Nov 15 |

---

## State Transitions

### Task Completion State

```
                     ┌──────────────────────────────────────┐
                     │                                      │
                     ▼                                      │
┌──────────────┐  toggle   ┌──────────────┐                │
│   PENDING    │ ────────► │  COMPLETED   │                │
│ completed=F  │           │ completed=T  │                │
└──────────────┘           └──────────────┘                │
       ▲                          │                        │
       │                          │ If recurring:          │
       │                          │ Create new task ───────┘
       │                          ▼
       │                   ┌──────────────┐
       └───────────────────│  NEW TASK    │
             toggle        │ completed=F  │
          (if toggled      │ new due_date │
           back)           └──────────────┘
```

### Due Date Status (Display Only)

```
due_date=None ──────► "(no deadline)" [gray]

due_date < today ───► "Overdue by Nd" [red]

due_date == today ──► "Due today!" [yellow]

due_date == tomorrow► "Due tomorrow" [yellow]

due_date > tomorrow ► "In Nd (YYYY-MM-DD)" [gray]
```

---

## Relationships

### Task Dependencies

```
Task
 ├── Priority (existing enum, required)
 ├── Recurrence (new enum, optional with default)
 └── Tags (existing set, optional)

No foreign keys or external entity relationships.
All data is self-contained within Task entity.
```

### Creation Relationship (Recurring Tasks)

```
Parent Task (completed)
       │
       │ triggers creation of
       ▼
Child Task (new occurrence)
       │
       │ No persistent link stored
       │ Child is independent entity
       ▼
Relationship is event-driven, not stored
```

---

## Validation Rules Summary

### Create Task

| Field | Validation |
|-------|------------|
| `title` | Required, 1-200 chars after trim |
| `description` | Optional, max 1000 chars |
| `priority` | Valid `Priority` enum |
| `tags` | Max 10 items, each max 30 chars, lowercase |
| `due_date` | Optional, valid date if provided |
| `recurrence` | Valid `Recurrence` enum |

### Update Task

| Field | Validation |
|-------|------------|
| `title` | If provided: 1-200 chars after trim, non-empty |
| `description` | If provided: max 1000 chars |
| `priority` | If provided: valid `Priority` enum |
| `tags` | If provided: replaces existing, same rules as create |
| `due_date` | If provided: valid date or `None` to remove |
| `recurrence` | If provided: valid `Recurrence` enum |

### Date Input Validation

| Input | Result |
|-------|--------|
| Empty/blank | `None` (no due date) |
| `YYYY-MM-DD` format | Parsed `date` object |
| Invalid format | Error: "Please enter date in YYYY-MM-DD format" |
| Invalid date (Feb 30) | Error: "Invalid date. Please check month/day values." |

---

## Migration Notes

### Backward Compatibility

The new fields are **additive** and use defaults:
- `due_date`: defaults to `None` → existing tasks have no deadline
- `recurrence`: defaults to `NONE` → existing tasks don't recur

**No migration needed** - existing tasks work unchanged.

### Repository Impact

- `InMemoryTaskRepository`: No changes (stores full Task objects)
- Repository interface: No changes
- Task dataclass: Add two fields with defaults

### Service Impact

- `create_task()`: Add optional `due_date` and `recurrence` parameters
- `update_task()`: Add optional `due_date` and `recurrence` parameters
- `toggle_complete()`: Check for recurrence and create new occurrence
- `list_tasks()`: Add `due_date_filter` parameter and `"due_date"` sort option
