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
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET /api/auth/me` - Get current user

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

## Tech Stack

- **Framework**: FastAPI
- **Database**: Neon PostgreSQL (asyncpg)
- **Authentication**: JWT (shared secret with frontend)
- **Deployment**: Hugging Face Spaces (Docker SDK)
