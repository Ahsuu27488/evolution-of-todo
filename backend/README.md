---
title: Evolution of Todo API
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Evolution of Todo Backend

FastAPI backend for the Evolution of Todo hackathon project.

## Features

- JWT Authentication with Better Auth
- Task CRUD with filtering, sorting, search
- Recurring tasks with auto-scheduling
- Audit logging for all modifications
- Async PostgreSQL with Neon

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration (with firstName, lastName)
- `POST /api/auth/signin` - User login
- `GET /api/auth/me` - Get current user (includes displayName)

**User Schema (v2)**:
- `firstName` (string, required): User's first name
- `lastName` (string, optional): User's last name (supports mononyms)
- `displayName` (string, computed): "First Last" or "First" or legacy name
- `email` (string): User email address
- `created_at` (datetime): Account creation timestamp

### Tasks
- `GET /api/tasks` - List tasks (with filters/sort/pagination)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `GET /api/tasks/search` - Search tasks
- `GET /api/tasks/{id}/logs` - Get audit logs

### Health
- `GET /api/health` - System health check

## Data Migration

### Legacy User Name Migration

The backend includes a migration service for migrating legacy single-name users to the new first_name/last_name schema:

**Migration Script**:
```bash
# Check migration status
python backend/scripts/migrate_users.py --status

# Preview changes (dry-run)
python backend/scripts/migrate_users.py --dry-run

# Run migration
python backend/scripts/migrate_users.py
```

**Migration Strategy**:
- Legacy `name` value becomes `first_name`
- `last_name` set to `NULL` (supports mononyms)
- Batch processing (100 users per batch)
- Zero-downtime with rollback safety
- Progress monitoring and integrity checks

**Migration Service** (`app/services/migration.py`):
- `get_migration_progress()`: Get migration statistics
- `migrate_user_names()`: Execute batch migration
- `verify_migration_integrity()`: Check data consistency

## Tech Stack

- **Framework**: FastAPI
- **Database**: Neon PostgreSQL (asyncpg)
- **Authentication**: JWT (shared secret with frontend)
- **Deployment**: Hugging Face Spaces (Docker SDK)
