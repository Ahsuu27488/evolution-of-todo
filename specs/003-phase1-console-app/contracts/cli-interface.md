# CLI Interface Contract: Phase 1 Console App

**Feature**: 003-phase1-console-app
**Date**: 2025-12-27
**Type**: Command-Line Interface Specification

---

## Main Menu Contract

### Display Format

```
╔═══════════════════════════════════════╗
║       📝 TODO CONSOLE APP             ║
╠═══════════════════════════════════════╣
║  1. View Tasks                        ║
║  2. Add Task                          ║
║  3. Update Task                       ║
║  4. Delete Task                       ║
║  5. Mark Complete/Incomplete          ║
║  6. Search Tasks                      ║
║  7. Filter Tasks                      ║
║  8. Sort Tasks                        ║
║  9. Exit                              ║
╚═══════════════════════════════════════╝
Enter your choice (1-9): _
```

### Menu Options

| Option | Name | Handler | Description |
|--------|------|---------|-------------|
| 1 | View Tasks | `view_tasks_handler` | Display all tasks with current filter/sort |
| 2 | Add Task | `add_task_handler` | Create new task with prompts |
| 3 | Update Task | `update_task_handler` | Modify existing task fields |
| 4 | Delete Task | `delete_task_handler` | Remove task with confirmation |
| 5 | Mark Complete | `toggle_complete_handler` | Toggle task completion status |
| 6 | Search Tasks | `search_tasks_handler` | Search by keyword |
| 7 | Filter Tasks | `filter_tasks_handler` | Filter by status/priority/tag |
| 8 | Sort Tasks | `sort_tasks_handler` | Sort by various criteria |
| 9 | Exit | `exit_handler` | Graceful application exit |

---

## Handler Contracts

### 1. View Tasks Handler

**Input**: None (uses current filter/sort state)

**Output Display**:
```
╔═══════════════════════════════════════════════════════════════════╗
║                         📋 YOUR TASKS                              ║
╠═══════════════════════════════════════════════════════════════════╣
║ Total: 5 | Pending: 3 | Completed: 2                              ║
║ Filter: All | Sort: Created (newest first)                        ║
╠════╦════════════════════════╦════════╦═══════════════╦════════════╣
║ ID ║ Title                  ║ Status ║ Priority      ║ Tags       ║
╠════╬════════════════════════╬════════╬═══════════════╬════════════╣
║ 1  ║ Buy groceries          ║ [ ]    ║ [HIGH]        ║ #shopping  ║
║ 2  ║ Call mom               ║ [✓]    ║ [MEDIUM]      ║ #personal  ║
╚════╩════════════════════════╩════════╩═══════════════╩════════════╝
```

**Empty State**:
```
╔═══════════════════════════════════════════════════════════════════╗
║                         📋 YOUR TASKS                              ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║    No tasks yet! Use option 2 to add your first task.             ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

### 2. Add Task Handler

**Interaction Flow**:

```
═══ ADD NEW TASK ═══

Enter title (required): Buy groceries
Enter description (optional, press Enter to skip): Milk, eggs, bread
Enter priority (high/medium/low) [medium]: high
Enter tags (comma-separated, optional): shopping, errands

✓ Task created successfully!
  ID: 1
  Title: Buy groceries
  Priority: [HIGH]
  Tags: #shopping #errands

Press Enter to continue...
```

**Validation Errors**:
```
Enter title (required):
✗ Error: Title is required. Please enter a title.
Enter title (required): _
```

```
Enter priority (high/medium/low) [medium]: critical
✗ Error: Invalid priority. Please enter high, medium, or low.
Enter priority (high/medium/low) [medium]: _
```

---

### 3. Update Task Handler

**Interaction Flow**:

```
═══ UPDATE TASK ═══

Enter task ID to update: 1

Current task:
  Title: Buy groceries
  Description: Milk, eggs, bread
  Priority: [HIGH]
  Tags: #shopping #errands
  Status: Pending

What would you like to update?
  1. Title
  2. Description
  3. Priority
  4. Tags
  5. Cancel

Enter choice (1-5): 1
Enter new title: Buy groceries and vegetables

✓ Task 1 updated successfully!
  Title: Buy groceries and vegetables

Press Enter to continue...
```

**Error Cases**:
```
Enter task ID to update: 99
✗ Error: Task with ID 99 not found.

Press Enter to continue...
```

---

### 4. Delete Task Handler

**Interaction Flow**:

```
═══ DELETE TASK ═══

Enter task ID to delete: 1

Task to delete:
  ID: 1
  Title: Buy groceries
  Priority: [HIGH]

⚠ Are you sure you want to delete this task? (y/n): y

✓ Task 1 deleted successfully.

Press Enter to continue...
```

**Cancellation**:
```
⚠ Are you sure you want to delete this task? (y/n): n

Operation cancelled. Task was not deleted.

Press Enter to continue...
```

---

### 5. Toggle Complete Handler

**Interaction Flow (Mark Complete)**:

```
═══ MARK COMPLETE/INCOMPLETE ═══

Enter task ID: 1

✓ Task 1 marked as completed.
  Title: Buy groceries

Press Enter to continue...
```

**Interaction Flow (Mark Incomplete)**:

```
═══ MARK COMPLETE/INCOMPLETE ═══

Enter task ID: 2

✓ Task 2 marked as pending.
  Title: Call mom

Press Enter to continue...
```

---

### 6. Search Tasks Handler

**Interaction Flow**:

```
═══ SEARCH TASKS ═══

Enter search term (searches title and description): milk

Found 2 tasks matching "milk":

╠════╦════════════════════════╦════════╦═══════════════╦════════════╣
║ ID ║ Title                  ║ Status ║ Priority      ║ Tags       ║
╠════╬════════════════════════╬════════╬═══════════════╬════════════╣
║ 1  ║ Buy groceries          ║ [ ]    ║ [HIGH]        ║ #shopping  ║
║ 5  ║ Return milk bottles    ║ [ ]    ║ [LOW]         ║ #errands   ║
╚════╩════════════════════════╩════════╩═══════════════╩════════════╝

Press Enter to continue...
```

**No Results**:
```
═══ SEARCH TASKS ═══

Enter search term: xyz123

No tasks found matching "xyz123".

Press Enter to continue...
```

---

### 7. Filter Tasks Handler

**Interaction Flow**:

```
═══ FILTER TASKS ═══

Current filter: All tasks

Select filter type:
  1. By Status (pending/completed/all)
  2. By Priority (high/medium/low)
  3. By Tag
  4. Clear all filters

Enter choice (1-4): 1

Select status:
  1. Pending only
  2. Completed only
  3. All tasks

Enter choice (1-3): 1

✓ Filter applied: Showing pending tasks only.

Filtered results:
[... task list display ...]

Press Enter to continue...
```

---

### 8. Sort Tasks Handler

**Interaction Flow**:

```
═══ SORT TASKS ═══

Current sort: Created (newest first)

Select sort criteria:
  1. By Priority (high → low)
  2. By Title (A → Z)
  3. By Created Date (newest first)
  4. By Created Date (oldest first)
  5. By Status (pending first)
  6. Default (by ID)

Enter choice (1-6): 1

✓ Tasks sorted by priority.

[... task list display ...]

Press Enter to continue...
```

---

### 9. Exit Handler

**Interaction Flow**:

```
═══ EXIT ═══

Thank you for using Todo Console App!
Goodbye! 👋

[Application terminates]
```

**Ctrl+C Handling**:
```
^C
Goodbye! 👋
[Application terminates]
```

---

## Input Validation Contract

### General Validation

| Input Type | Validation | Error Message |
|------------|------------|---------------|
| Menu choice | Must be 1-9 | "Invalid option. Please select 1-9." |
| Task ID | Must be positive integer | "Please enter a valid task ID (number)." |
| Yes/No | Must be y/n (case-insensitive) | "Please enter y or n." |
| Priority | Must be high/medium/low | "Invalid priority. Please enter high, medium, or low." |

### Field Validation

| Field | Validation | Error Message |
|-------|------------|---------------|
| Title | Non-empty after trim | "Title is required." |
| Title | ≤ 200 chars | "Title must be 200 characters or less." |
| Description | ≤ 1000 chars | "Description must be 1000 characters or less." |
| Tags | Each ≤ 30 chars | "Each tag must be 30 characters or less." |
| Tags | Max 10 tags | "Maximum 10 tags allowed." |

---

## State Management

### Application State

```python
class AppState:
    """Tracks current filter and sort preferences."""
    current_filter: FilterState | None = None
    current_sort: SortState = SortState(field="id", reverse=False)

@dataclass
class FilterState:
    status: str | None = None      # "pending", "completed", or None
    priority: Priority | None = None
    tag: str | None = None

@dataclass
class SortState:
    field: str = "id"              # "id", "priority", "title", "created", "status"
    reverse: bool = False
```

### State Persistence

- State persists only within session
- Filter/sort preferences reset on exit
- No file-based persistence (Phase I constraint)

---

## Color Support (Optional Enhancement)

If terminal supports ANSI colors:

| Element | Color |
|---------|-------|
| HIGH priority | Red (`\033[91m`) |
| MEDIUM priority | Yellow (`\033[93m`) |
| LOW priority | Gray (`\033[90m`) |
| Completed status | Green (`\033[92m`) |
| Error messages | Red (`\033[91m`) |
| Success messages | Green (`\033[92m`) |
| Headers | Bold (`\033[1m`) |

Fallback: Plain text if color not supported.

---

*Contract version: 1.0*
*Compatible with: spec.md v1.0, data-model.md v1.0*
