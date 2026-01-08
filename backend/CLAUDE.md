# Backend Guidelines

## Stack
- Python 3.13+
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL (via DATABASE_URL)
- PyJWT for token verification

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entry point
│   ├── models.py           # SQLModel database models
│   ├── db.py               # Database connection & session
│   ├── auth.py             # JWT verification middleware
│   └── routes/
│       ├── __init__.py
│       └── tasks.py        # Task CRUD endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_tasks.py
├── .env                    # Environment variables (not committed)
├── .env.example            # Environment template
├── requirements.txt
└── pyproject.toml
```

## API Conventions
- All routes under `/api/{user_id}/`
- Return JSON responses
- Use Pydantic/SQLModel models for request/response
- Handle errors with HTTPException
- All endpoints require JWT authentication
- User ID in URL must match JWT token subject

## Database
- Use SQLModel for all database operations
- Connection string from `DATABASE_URL` environment variable
- Tables created automatically on startup via lifespan handler

## Authentication
- JWT tokens issued by Better Auth (frontend)
- Verify tokens using `BETTER_AUTH_SECRET` (shared with frontend)
- Extract user_id from token's `sub` claim
- Return 401 for invalid/expired tokens
- Return 403 when URL user_id doesn't match token user

## Running
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | JWT secret (must match frontend) |
| `CORS_ORIGINS` | Allowed frontend origins |

## Patterns
- Use dependency injection for database sessions
- Use `Depends(get_current_user_id)` for auth
- Return `TaskPublic` models (not raw `Task`) to hide internal fields
- Order tasks by `created_at` descending by default
