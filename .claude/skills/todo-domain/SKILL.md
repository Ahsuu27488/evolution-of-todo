---
name: "todo-domain"
description: "Apply todo app domain knowledge and data models. Use when designing or implementing todo features."
version: "2.0.0"
---

# Todo Domain Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User discusses todo/task features (add, delete, update, view, complete)
- Data model design for tasks or todos
- API endpoint design for task management
- Implementing priorities, tags, search, filter, or sort features
- CLI menu design for task operations

## How This Skill Works

Step-by-step workflow:
1. **Identify Feature**: Map user request to Basic/Intermediate/Advanced level
2. **Apply Model**: Use standard Task data model with priority, tags, timestamps
3. **Validate Scope**: Ensure feature matches current phase constraints
4. **Generate**: Produce implementation aligned with domain rules and patterns

## Output Format

Provide structured output:
- **Feature Level**: Basic, Intermediate, or Advanced
- **Data Model**: Entity fields, types, and constraints
- **Operations**: CRUD operations and query methods involved
- **Validation**: Input validation rules to apply

## Domain Model Summary

### Task Entity (Phase I - Enhanced)

```python
@dataclass
class Task:
    id: int                    # Auto-assigned, sequential, unique
    title: str                 # Required, 1-200 chars
    description: str = ""      # Optional, max 1000 chars
    priority: Priority = MEDIUM # HIGH(3), MEDIUM(2), LOW(1)
    tags: set[str] = set()     # Max 10 tags, each max 30 chars
    completed: bool = False    # Toggleable status
    created_at: datetime       # Auto-assigned on creation
```

### Priority Enum

```python
class Priority(IntEnum):
    LOW = 1      # Display: [LOW]
    MEDIUM = 2   # Display: [MEDIUM] (default)
    HIGH = 3     # Display: [HIGH]
```

## Constraints and Rules

**Validation Rules:**
- Task ID must be unique and auto-generated (never reused)
- Title is required, 1-200 characters after trimming
- Description is optional, max 1000 characters
- Priority must be valid enum value (high/medium/low)
- Tags: max 10 per task, each max 30 chars, lowercase, unique
- Status toggles between complete/incomplete

**Phase Constraints:**
- Phase I: In-memory storage only, standard library only
- Phase II+: User isolation required (user_id field)
- Phase III+: Operations become MCP tools

## Feature Levels

### Basic Level (Phase I Required)
1. **Add Task** - Create with title, description, priority, tags
2. **Delete Task** - Remove with confirmation prompt
3. **Update Task** - Modify any field by task ID
4. **View Tasks** - Display with status, priority, tags indicators
5. **Mark Complete** - Toggle completion status

### Intermediate Level (Phase I Enhanced)
1. **Priorities** - HIGH/MEDIUM/LOW with visual indicators
2. **Tags** - Multiple tags, hashtag display (#work #urgent)
3. **Search** - Case-insensitive keyword search in title/description
4. **Filter** - By status, priority, or tag
5. **Sort** - By priority, title, created date, status

### Advanced Level (Phase V)
1. **Recurring Tasks** - Auto-reschedule repeating tasks
2. **Due Dates & Reminders** - Deadlines with notifications

## Example

**Input**: "Implement task search functionality"

**Output**:
```
Feature Level: Intermediate
Data Model: Task { id, title, description, priority, tags, completed, created_at }
Operations:
  - list_tasks(search="keyword") - Filter tasks by keyword
  - Search in title and description fields
  - Case-insensitive matching
Validation:
  - Empty search returns all tasks
  - Search term trimmed before matching
Display:
  - Show matching results with keyword context
  - Indicate "No tasks found matching 'xyz'" if empty
```

**Input**: "Add high priority task with tags"

**Output**:
```
Feature Level: Basic + Intermediate
Data Model: Task with priority=HIGH, tags=set()
Operations:
  - create_task(title, description, priority=Priority.HIGH, tags={"work", "urgent"})
Validation:
  - Title required, ≤200 chars
  - Priority must be valid enum
  - Tags: parse comma-separated, dedupe, max 10
Display:
  - Task ID: X
  - Priority: [HIGH]
  - Tags: #work #urgent
```

## Supporting Files

- `reference/data-models.md`: Complete data models for all phases with code examples
