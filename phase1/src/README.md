# Todo Console Application

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://python.org)
[![Phase](https://img.shields.io/badge/Phase-I-CRUD-success)](https://github.com/panaversity)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Phase I** of the Evolution of Todo Hackathon — A clean-architecture Python console application demonstrating the five basic level operations with advanced features including priorities, tags, due dates, and recurring tasks.

## Features

### Basic Level (Core Essentials)
- Add Task — Create new todo items with title, description, priority, and tags
- Delete Task — Remove tasks from the list with confirmation
- Update Task — Modify existing task details
- View Task List — Display all tasks with color-coded status
- Mark as Complete — Toggle task completion status

### Intermediate Level (Organization)
- Priorities — High, Medium, Low with color-coded display
- Tags/Categories — Assign and filter by category tags
- Search — Full-text search across title and description
- Filter — By status, priority, tag, or due date range
- Sort — By ID, priority, title, created date, status, or due date

### Advanced Level (Intelligent Features)
- Recurring Tasks — Auto-reschedule repeating tasks (daily, weekly, monthly)
- Due Dates — Set deadlines with visual urgency indicators
- Smart Recurrence — Handles month overflow (Jan 31 → Feb 28)

## Architecture

```
src/
├── main.py                 # Application entry point with demo data loader
└── todo/
    ├── __init__.py
    ├── cli/                # Presentation layer
    │   ├── app.py          # Main CLI application class and state
    │   ├── handlers.py     # Menu option handlers
    │   ├── display.py      # Terminal output formatting
    │   └── validators.py   # Input validation helpers
    ├── domain/             # Business entities
    │   ├── task.py         # Task dataclass + enums
    │   └── exceptions.py   # Domain exceptions
    ├── repository/         # Data access abstraction
    │   ├── base.py         # Abstract repository interface
    │   └── memory.py       # In-memory implementation
    └── services/           # Business logic
        └── task_service.py # Task operations with validation
```

### Design Patterns

| Pattern | Purpose | Location |
|---------|---------|----------|
| **Repository** | Decouple data access from business logic | `repository/base.py` |
| **Dependency Injection** | Pass repository to service | `main.py:124` |
| **Service Layer** | Business logic reuse for Phase II | `services/task_service.py` |
| **Handler Pattern** | Declarative menu routing | `cli/app.py:51-81` |

## Installation

### Prerequisites
- Python 3.13 or higher
- UV package manager (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/evolution-of-todo.git
cd evolution-of-todo

# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or using pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Running the Application

```bash
# Start with empty task list
python3 src/main.py

# Start with demo data for testing
python3 src/main.py --demo
```

### CLI Menu

```
+---------------------------------------+
|       TODO CONSOLE APP                |
+---------------------------------------+
|  1. View Tasks                        |
|  2. Add Task                          |
|  3. Update Task                       |
|  4. Delete Task                       |
|  5. Mark Complete/Incomplete          |
|  6. Search Tasks                      |
|  7. Filter Tasks                      |
|  8. Sort Tasks                        |
|  9. Exit                              |
+---------------------------------------+
```

### Example Workflow

```bash
$ python3 src/main.py --demo

✓ Demo mode: Loaded 9 sample tasks with due dates and recurring patterns

# View all tasks with filtering and sorting
> 1  # View Tasks

# Add a new task with priority and due date
> 2  # Add Task
Enter title: Review pull requests
Enter priority (high/medium/low) [medium]: high
Enter tags (comma-separated, optional): code-review, work
Enter due date (YYYY-MM-DD, or press Enter to skip): 2025-01-15
Set recurrence? (none/daily/weekly/monthly) [none]: weekly

# Search for tasks
> 6  # Search Tasks
Enter search term: review

# Mark a recurring task complete (auto-creates next occurrence)
> 5  # Mark Complete/Incomplete
Enter task ID: 3
✓ Task 3 marked as completed.
Next occurrence scheduled for 2025-01-10
New task ID: 10
```

## Data Model

```python
@dataclass
class Task:
    id: int                              # Auto-assigned, sequential
    title: str                           # Required, 1-200 chars
    description: str = ""                # Optional, max 1000 chars
    priority: Priority = Priority.MEDIUM # LOW, MEDIUM, HIGH
    tags: set[str]                       # Max 10 tags, 30 chars each
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_date: date | None = None
    recurrence: Recurrence = Recurrence.NONE  # NONE, DAILY, WEEKLY, MONTHLY
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NO_COLOR` | Disable ANSI colors in output | Not set |
| `TERM` | Terminal type (affects color detection) | Auto-detected |

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=todo --cov-report=html
```

### Code Style

This project follows:
- PEP 8 style guidelines
- Type hints for all function signatures
- Docstrings for all public modules, classes, and functions
- Clean architecture with clear layer separation

### Extending to Phase II

The `TaskService` class is designed for reuse in FastAPI:

```python
# backend/main.py
from src.todo.services.task_service import TaskService
from src.todo.repository.base import TaskRepository

# Replace InMemoryTaskRepository with SQLModel implementation
repository = SQLModelTaskRepository(engine)
service = TaskService(repository)

# Use service methods directly in FastAPI routes
@app.post("/api/tasks")
async def create_task(title: str, description: str = ""):
    return service.create_task(title=title, description=description)
```

## Contributing

This is a hackathon project. Contributions follow the [root README](../README.md) guidelines.

## License

MIT License — see [LICENSE](../LICENSE) for details.
