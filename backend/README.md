---
title: Evolution of Todo API
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Chronos Todo API — FastAPI Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.21%2B-blue)](https://sqlmodel.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Phase](https://img.shields.io/badge/Phase-II-Chronos_WebApp-success)](https://github.com/panaversity)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Phase II** backend API for the Chronos Todo Full-Stack Web Application — A RESTful API built with FastAPI, SQLModel, and Neon PostgreSQL with async/await throughout.

## Features

- Complete CRUD operations for tasks
- JWT authentication with Better Auth integration
- Task filtering, sorting, and search
- Recurring tasks with auto-creation
- Audit trail for all task modifications
- Request ID tracking for debugging
- Comprehensive error handling

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, CORS, lifespan
│   ├── db.py                # Async database engine, session factory
│   ├── models.py            # SQLModel models (Task, TaskLog, User, schemas)
│   ├── errors.py            # Exception handling, error middleware
│   ├── simple_auth.py       # JWT verification, password hashing
│   └── routes/
│       ├── __init__.py
│       ├── tasks.py         # Task CRUD endpoints
│       └── auth.py          # Auth endpoints (signup/signin/me)
├── scripts/
│   ├── db/
│   │   ├── reset.py         # Database reset utility
│   │   └── test_connection.py
│   └── test_all.py
├── .env.example             # Environment variable template
├── pyproject.toml           # UV package configuration
└── requirements.txt         # Pip dependencies
```

## Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| **Web Framework** | FastAPI 0.115+ | Async REST API |
| **ORM** | SQLModel 0.21+ | Pydantic + SQLAlchemy |
| **Database** | Neon PostgreSQL | Serverless Postgres |
| **Driver** | asyncpg | Async PostgreSQL driver |
| **Authentication** | python-jose | JWT handling |
| **Password Hashing** | passlib | Bcrypt hashing |
| **CORS** | FastAPI CORSMiddleware | Frontend integration |

## Installation

### Prerequisites
- Python 3.10 or higher
- UV package manager (recommended) or pip
- Neon PostgreSQL database account

### Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Neon PostgreSQL Database Connection
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Better Auth JWT Secret (MUST match frontend)
BETTER_AUTH_SECRET=your-32-character-secret-here

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:3000
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT secret (≥32 chars, must match frontend) |
| `CORS_ORIGINS` | No | Comma-separated list of allowed origins (default: `http://localhost:3000`) |
| `DEBUG` | No | Enable debug logging (default: `false`) |

## Usage

### Starting the Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-01-10T12:00:00Z",
  "version": "2.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 15
    }
  }
}
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/signin` | Login and get JWT token |
| POST | `/api/auth/signout` | Logout (client-side) |
| GET | `/api/auth/me` | Get current user info |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks (filter, sort, paginate) |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/search` | Search tasks by keyword |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |
| GET | `/api/tasks/{id}/logs` | Get task audit logs |

### Example Request

```bash
# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review PRs",
    "description": "Review pull requests for the auth feature",
    "priority": "HIGH",
    "tags": [{"name": "work", "color": "#00f5ff"}],
    "due_date": "2025-01-15T12:00:00Z",
    "recurrence_pattern": "WEEKLY"
  }'
```

## Data Model

### Task

```python
class Task(SQLModel, table=True):
    id: int                              # Auto-generated primary key
    user_id: str                         # Owner UUID from Better Auth
    title: str                           # Required, 1-200 chars
    description: str | None              # Optional, max 1000 chars
    priority: Priority                   # LOW, MEDIUM, HIGH
    tags: list[Tag]                      # JSONB: max 10 tags
    completed: bool                      # Completion status
    due_date: datetime | None            # Optional deadline
    recurrence_pattern: RecurrencePattern # NONE, DAILY, WEEKLY, MONTHLY

    # AI-ready fields for Phase III
    transcription_text: str | None       # Voice command text
    ai_summary: str | None               # LLM-generated summary
    embedding_id: str | None             # Vector search ID

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### Tag

```python
class Tag(BaseModel):
    name: str   # 1-30 characters
    color: str  # Hex color code (#RRGGBB)
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py
```

### Database Utilities

```bash
# Test database connection
python scripts/db/test_connection.py

# Reset database (WARNING: deletes all data)
python scripts/db/reset.py
```

## Security

### JWT Authentication Flow

1. Frontend sends JWT in `Authorization: Bearer <token>` header
2. Backend verifies token using `BETTER_AUTH_SECRET`
3. Extracts `sub` claim as user_id
4. Grants access to user's own resources only

### Password Security

- Passwords hashed with bcrypt (passlib)
- Minimum 8 characters enforced
- Never stored in plain text

### CORS Configuration

By default, only `http://localhost:3000` is allowed. Configure additional origins via `CORS_ORIGINS` environment variable.

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Link and deploy
railway link
railway up
```

Set environment variables in Railway dashboard.

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

See the main [README](../README.md) for contribution guidelines.

## License

MIT License — see [LICENSE](../LICENSE) for details.
