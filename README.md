# Evolution of Todo — Hackathon II

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A full-stack todo application demonstrating **Spec-Driven Development** across 5 evolutionary phases, from a simple console app to an AI-powered, cloud-deployed web application.

## Project Phases

| Phase | Status | Description | Documentation |
|-------|--------|-------------|---------------|
| **Phase I** | ✅ Complete | In-memory Python console app | [`src/README.md`](src/README.md) |
| **Phase II** | ✅ Complete | Full-stack web application | [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md) |
| Phase III | ⏳ Pending | AI-powered chatbot with OpenAI Agents SDK | — |
| Phase IV | ⏳ Pending | Local Kubernetes deployment with Minikube/Helm | — |
| Phase V | ⏳ Pending | Cloud deployment with Kafka/Dapr | — |

## Quick Overview

```
evolution-of-todo/
├── src/                    # Phase I: Console App
│   ├── README.md           # Console app documentation
│   ├── CLAUDE.md           # Architecture patterns
│   └── todo/               # Domain, repository, service, CLI layers
│
├── backend/                # Phase II: FastAPI Backend
│   ├── README.md           # Backend documentation
│   ├── CLAUDE.md           # Backend architecture
│   ├── app/                # FastAPI application
│   │   ├── main.py         # App entry point
│   │   ├── models.py       # SQLModel models
│   │   ├── db.py           # Database connection
│   │   ├── errors.py       # Error handling
│   │   ├── simple_auth.py  # JWT auth
│   │   └── routes/         # API endpoints
│   └── requirements.txt
│
├── frontend/               # Phase II: Next.js Frontend
│   ├── README.md           # Frontend documentation
│   ├── CLAUDE.md           # Frontend architecture
│   ├── app/                # Next.js App Router
│   │   ├── (auth)/         # Auth pages
│   │   ├── dashboard/      # Main app
│   │   ├── actions/        # Server Actions
│   │   ├── api/auth/       # Better Auth routes
│   │   └── providers.tsx   # App providers
│   ├── components/         # React components
│   ├── lib/                # Utilities, API client, auth
│   └── package.json
│
├── specs/                  # Feature specifications
├── history/                # PHRs, ADRs
└── .specify/               # SpecKit Plus templates
```

## Tech Stack

### Phase II (Full-Stack Web App)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15.2.8 | App Router, Server Components |
| **Frontend** | React 19.2.3 | UI framework |
| **Frontend** | TypeScript 5+ | Type safety |
| **Frontend** | Tailwind CSS v4 | Styling |
| **Frontend** | shadcn/ui | Component library |
| **Frontend** | TanStack Query 5+ | Server state |
| **Frontend** | Zustand 5+ | Client state |
| **Frontend** | Better Auth 1.4.9 | Authentication |
| **Backend** | FastAPI 0.115+ | REST API |
| **Backend** | SQLModel 0.21+ | ORM |
| **Backend** | Python 3.13+ | Runtime |
| **Database** | Neon PostgreSQL | Serverless Postgres |
| **Auth** | JWT (HS256) | Shared secret auth |

## Quick Start

### Prerequisites

- **Node.js** 20+
- **Python** 3.13+
- **Neon** DB account ([sign up free](https://neon.tech))
- **UV** package manager (recommended) or pip

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/evolution-of-todo.git
cd evolution-of-todo
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
CORS_ORIGINS=http://localhost:3000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
```

> **⚠️ Important:** `BETTER_AUTH_SECRET` must be **identical** in both `backend/.env` and `frontend/.env.local`!

### 4. Run Development Servers

**Terminal 1 — Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/api/health |

## Phase I: Console Application

The foundation phase demonstrating clean architecture patterns that scale to the full-stack application.

### Running Phase I

```bash
# Start with empty task list
python3 src/main.py

# Start with demo data
python3 src/main.py --demo
```

### Features

- ✅ Add, view, update, delete tasks
- ✅ Mark tasks complete/incomplete
- ✅ Priorities (HIGH/MEDIUM/LOW)
- ✅ Tags/categories with colors
- ✅ Search and filter
- ✅ Sort by multiple fields
- ✅ Recurring tasks (daily/weekly/monthly)
- ✅ Due dates with urgency indicators

See [`src/README.md`](src/README.md) for detailed documentation.

## Phase II: Full-Stack Web Application

A modern, multi-user todo application with authentication and persistent storage.

### Features

- ✅ User registration and email/password authentication
- ✅ User profile with first name and last name fields (supports mononyms)
- ✅ Edit profile functionality for existing users
- ✅ JWT-based session management
- ✅ Task CRUD with optimistic UI updates
- ✅ Task filtering by status, priority, tags
- ✅ Task search and sorting
- ✅ Data isolation between users
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark mode support
- ✅ Enhanced loading states with dual-ring spinner animation
- ✅ Inline error handling with retry functionality
- ✅ Toast notifications
- ✅ Audit trail for task modifications
- ✅ Zero-downtime database migrations with Alembic

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user (with first name, last name) |
| POST | `/api/auth/signin` | Login and get JWT |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/me` | Update current user profile |
| GET | `/api/tasks` | List tasks (filter, sort, paginate) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/search` | Search tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |
| GET | `/api/tasks/{id}/logs` | Get audit logs |

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md) for detailed documentation.

### Database Migration

For users who signed up before name fields were added, use the migration CLI:

```bash
# Check migration status
python backend/scripts/migrate_users.py --status

# Preview changes (dry-run)
python backend/scripts/migrate_users.py --dry-run

# Run migration
python backend/scripts/migrate_users.py
```

**Migration Strategy**:
- Legacy single-name users migrated to first_name/last_name schema
- Zero-downtime with batch processing (100 users per batch)
- Rollback safety and integrity checks
- Supports mononyms (last_name can be NULL)

## Development

### Spec-Driven Development

This project uses **Spec-Driven Development** with:

- **Spec-Kit Plus** for specification management
- **Claude Code** for AI-assisted development
- **MCP Servers** for context-aware tooling

### Documentation Structure

- `specs/` — Feature specifications (spec, plan, tasks)
- `history/prompts/` — Prompt History Records (PHRs)
- `history/adr/` — Architecture Decision Records
- `.claude/skills/` — Reusable intelligence

### Architecture Patterns

The codebase demonstrates several key patterns:

1. **Repository Pattern** — Abstract data access (src/backend)
2. **Service Layer** — Business logic separation (src/backend)
3. **Dependency Injection** — Pass dependencies to services
4. **JWT Authentication** — Shared secret auth between frontend/backend
5. **Async/Await** — Throughout the backend stack
6. **Server Actions** — Next.js server-side mutations
7. **Result Type** — Type-safe error handling

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with Spec-Driven Development using Claude Code*
