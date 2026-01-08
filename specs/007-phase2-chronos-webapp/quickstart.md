# Quickstart Guide: Phase II "Chronos" Web App

**Feature**: 007-phase2-chronos-webapp
**Date**: 2026-01-06
**Prerequisites**: Python 3.13+, Node.js 20+, UV package manager

---

## Overview

This guide gets you up and running with the Phase II "Chronos" Professional Web App development environment.

---

## Prerequisites Installation

### 1. Install UV (Python Package Manager)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Install Node.js 20+

```bash
# Using nvm (recommended)
nvm install 20
nvm use 20

# Verify installation
node --version
npm --version
```

### 3. Create Neon PostgreSQL Database

1. Go to [https://neon.tech](https://neon.tech)
2. Sign up for free account
3. Create a new project: "chronos-db"
4. Copy the connection string (format: `postgresql://user:password@host/database`)

---

## Backend Setup (FastAPI)

### 1. Create Virtual Environment

```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
uv pip install fastapi uvicorn[standard] sqlmodel psycopg2-binary python-jose passlib[bcrypt] pydantic pydantic-settings
```

### 3. Configure Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Secret (must match frontend)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 4. Run Database Migrations

```bash
# Create tables
python -c "
from app.db import engine
from sqlmodel import SQLModel
from app.models import Task, TaskLog

SQLModel.metadata.create_all(engine)
print('Database tables created successfully!')
"
```

### 5. Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

API Docs: http://localhost:8000/docs

---

## Frontend Setup (Next.js 16)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create `frontend/.env.local`:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (shared secret with backend)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long

# Database (for server-side queries)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend `.env` files!

### 3. Start Development Server

```bash
npm run dev
```

Frontend runs at: http://localhost:3000

---

## Verify Setup

### 1. Test Backend Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "timestamp": "2026-01-06T..."
}
```

### 2. Test Frontend

1. Open http://localhost:3000 in browser
2. You should see the "Evolution of Todo" landing page
3. Click "Start Your Journey" to create an account
4. Sign up with email/password
5. You should be redirected to the dashboard

---

## Development Workflow

### File Watch Mode

Both frontend and backend support hot-reload during development:

| Terminal | Command | Hot Reload |
|----------|---------|------------|
| Terminal 1 | `cd backend && uvicorn app.main:app --reload` | ✅ Yes |
| Terminal 2 | `cd frontend && npm run dev` | ✅ Yes |

### Code Organization

```
├── backend/                 # FastAPI backend
│   └── app/
│       ├── main.py         # App entry point
│       ├── models.py       # SQLModel models
│       ├── routes/         # API endpoints
│       └── ...
├── frontend/                # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── ...
└── specs/007-phase2-chronos-webapp/  # This feature's specs
```

---

## Common Issues

### Issue: "Module not found" error

**Solution**: Make sure you've activated the virtual environment:
```bash
source backend/.venv/bin/activate
```

### Issue: "Connection refused" on DATABASE_URL

**Solution**: Verify Neon database is running and connection string is correct. Ensure `?sslmode=require` is included.

### Issue: "CORS error" when frontend calls backend

**Solution**: Check that `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`

### Issue: "Invalid JWT token" errors

**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in both frontend and backend `.env` files

---

## Next Steps

1. **Run tests**: `npm test` (frontend), `pytest` (backend)
2. **Create tasks**: Run `/sp.tasks` to generate implementation tasks
3. **Start coding**: Follow tasks.md for step-by-step implementation

---

## Production Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
vercel --prod
```

### Backend (Railway/Render)

```bash
# Deploy using platform CLI
# See platform documentation for details
```

---

## Useful Commands

### Backend

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Format code
black app/

# Type check
mypy app/
```

### Frontend

```bash
# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format

# Build for production
npm run build
```

---

## Support

- **Constitution**: `.specify/memory/constitution.md`
- **Spec**: `specs/007-phase2-chronos-webapp/spec.md`
- **Plan**: `specs/007-phase2-chronos-webapp/plan.md`
- **Data Model**: `specs/007-phase2-chronos-webapp/data-model.md`
- **API Contract**: `specs/007-phase2-chronos-webapp/contracts/backend-api.yaml`
