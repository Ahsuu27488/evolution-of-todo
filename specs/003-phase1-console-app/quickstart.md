# Quickstart: Phase 1 Console App

**Feature**: 003-phase1-console-app
**Date**: 2025-12-27
**Purpose**: Step-by-step guide to run and develop the application

---

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.13+ | `python --version` |
| UV | Latest | `uv --version` |

## Project Setup

### 1. Initialize Project with UV

```bash
# From repository root
uv init todo-console --python 3.13
cd todo-console

# Or if project exists
uv sync
```

### 2. Project Structure

After setup, your project should look like:

```
src/
├── todo/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── task.py          # Task entity and Priority enum
│   │   └── exceptions.py    # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract repository
│   │   └── memory.py        # In-memory implementation
│   └── cli/
│       ├── __init__.py
│       ├── app.py           # Main CLI loop
│       ├── handlers.py      # Menu handlers
│       └── display.py       # Display formatting
└── main.py                  # Entry point

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task.py
│   ├── test_service.py
│   └── test_repository.py
└── integration/
    ├── __init__.py
    └── test_cli.py

pyproject.toml
README.md
```

### 3. pyproject.toml

```toml
[project]
name = "todo-console"
version = "1.0.0"
description = "Phase 1 - In-Memory Todo Console Application"
requires-python = ">=3.13"
dependencies = []

[project.scripts]
todo = "main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

## Running the Application

### Development Mode

```bash
# Run directly
python src/main.py

# Or with UV
uv run python src/main.py
```

### Expected Output

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

## Running Tests

```bash
# Install test dependencies
uv add --dev pytest

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todo

# Run specific test file
uv run pytest tests/unit/test_task.py -v
```

## Development Workflow

### 1. Implement Domain Layer First

```bash
# Create and test Task entity
python -c "
from src.todo.domain.task import Task, Priority
task = Task(id=1, title='Test task')
print(f'Task: {task.title}, Priority: {task.priority}')
"
```

### 2. Implement Repository Layer

```bash
# Test in-memory repository
python -c "
from src.todo.repository.memory import InMemoryTaskRepository
from src.todo.domain.task import Task, Priority

repo = InMemoryTaskRepository()
task = repo.add(Task(id=0, title='Test'))
print(f'Added task with ID: {task.id}')
print(f'All tasks: {repo.get_all()}')
"
```

### 3. Implement Service Layer

```bash
# Test service operations
python -c "
from src.todo.services.task_service import TaskService
from src.todo.repository.memory import InMemoryTaskRepository
from src.todo.domain.task import Priority

service = TaskService(InMemoryTaskRepository())
task = service.create_task('Buy groceries', priority=Priority.HIGH, tags={'shopping'})
print(f'Created: {task.title} [{task.priority.name}]')
print(f'Stats: {service.get_stats()}')
"
```

### 4. Wire Up CLI

```bash
# Run full application
python src/main.py
```

## Key Implementation Notes

### Task Entity

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    tags: set[str] = field(default_factory=set)
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### Repository Pattern

```python
# Abstract base (repository/base.py)
class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task: ...
    @abstractmethod
    def get(self, task_id: int) -> Task | None: ...
    # ... other methods

# In-memory implementation (repository/memory.py)
class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

### Service Layer

```python
class TaskService:
    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def create_task(self, title: str, ...) -> Task:
        # Validate inputs
        # Create task
        # Add to repository
        return task
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure `src/` is in PYTHONPATH or run from project root |
| `ImportError` | Check `__init__.py` files exist in all packages |
| Tests not found | Verify `tests/` directory structure and `test_` prefix |
| Unicode display issues | Use UTF-8 terminal encoding |

## Next Steps

After Phase 1 implementation:

1. **Phase II**: Add FastAPI backend, PostgreSQL persistence
2. **Phase III**: Implement MCP tools and AI chatbot
3. **Phase IV**: Containerize with Docker, deploy to Minikube

---

*Quickstart version: 1.0*
*Compatible with: spec.md v1.0, data-model.md v1.0*
