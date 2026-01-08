# Implementation Plan: Phase II - "Chronos" Professional Web App (REPAIR MODE)

**Branch**: `007-phase2-chronos-webapp` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-phase2-chronos-webapp/spec.md`
**Mode**: REPAIR MODE - Fixing critical bugs identified in audit

## Summary

Transform the Phase I console Todo application into a full-stack web application with:
- **Frontend**: Next.js 16+ with "Deep Space Glassmorphism" aesthetic, Command Center UI foundation for Phase III voice integration
- **Backend**: FastAPI with SQLModel ORM, JWT authentication via Better Auth
- **Database**: Neon PostgreSQL with AI-ready schema fields
- **Key Features**: Full Phase I feature parity (Basic + Intermediate + Advanced), responsive design, landing page

**REPAIR FOCUS**: This plan addresses critical bugs found during audit:
1. **CRITICAL**: bcrypt 5.0 incompatibility with passlib - backend crashes on signup
2. **CRITICAL**: Missing dependencies in requirements.txt (passlib, bcrypt, asyncpg, requests)
3. **HIGH**: Frontend auth pages missing (signin/page.tsx, signup/page.tsx)
4. **HIGH**: Security - exposed credentials in .env.local need rotation

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5+ (Next.js 16 App Router)
- Backend: Python 3.13+ (STRICT - per constitution Section V.1.1)

**Primary Dependencies**:
- Frontend: Next.js 16, React 19, Tailwind CSS, shadcn/ui, framer-motion, canvas-confetti, TanStack Query, Zustand
- Backend: FastAPI, SQLModel, psycopg2-binary, python-jose, passlib>=1.7.4, **bcrypt>=4.0.0,<5.0.0** (CRITICAL: must pin <5.0 for passlib compatibility), **asyncpg** (CRITICAL: missing from requirements.txt)
- Auth: Better Auth (frontend), JWT (backend)

**Storage**: Neon Serverless PostgreSQL (connection pooling enabled)

**Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)

**Target Platform**:
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions) with backdrop-filter support
- Backend: Linux server (FastAPI async)

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Task list render < 1.5s (100 tasks)
- Lighthouse scores > 90 (all categories)
- 60fps animations on target devices

**Constraints**:
- JWT token expiry: 7 days
- Title length: 1-200 characters
- Description length: 0-1000 characters
- Tags per task: 0-10 items, max 30 chars each
- Touch targets: minimum 44x44 pixels
- **bcrypt must be <5.0.0** for passlib compatibility

**Scale/Scope**:
- Single-user isolation (multi-user with data separation)
- Expected: 100-1000 tasks per user
- Responsive: 320px (mobile) to 2560px (desktop)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Phase Isolation (Section 4.1)

| Gate | Status | Notes |
|------|--------|-------|
| Phase I features (Basic + Intermediate + Advanced) | ✅ PASS | All Phase I features carried forward: Add, Delete, Update, View, Complete, Priorities, Tags, Search, Filter, Sort, Due Dates, Recurring Tasks |
| Future-phase features excluded | ✅ PASS | Voice input, OpenAI Agents SDK, MCP Server, WebSocket explicitly deferred to Phase III |
| Architecture evolution | ✅ PASS | Database schema includes AI-ready fields (transcription_text, ai_summary, embedding_id) for Phase III continuity |

### Technology Constraints (Section 5.2)

| Gate | Status | Notes |
|------|--------|-------|
| Frontend: Next.js 16+ | ✅ PASS | Specified in requirements |
| Backend: FastAPI | ✅ PASS | Specified in requirements |
| ORM: SQLModel | ✅ PASS | Specified in requirements |
| Database: Neon PostgreSQL | ✅ PASS | Specified in requirements |
| Authentication: Better Auth | ✅ PASS | Specified in requirements |
| Python Version: 3.13+ | ⚠️ FIX REQUIRED | Environment is running 3.12.3 - must upgrade to 3.13+ per constitution Section V.1.1 |

### Agent Behavior Rules (Section 2.1)

| Gate | Status | Notes |
|------|--------|-------|
| No code without approved specs | ✅ PASS | spec.md exists and validated |
| No feature invention | ✅ PASS | All features trace to spec FR-XXX requirements |
| Phase II features only | ✅ PASS | Out of Scope section explicitly defines boundaries |

### Knowledge & Documentation Protocol (Section 3.1)

| Gate | Status | Notes |
|------|--------|-------|
| Context7 MCP Mandate | ⚠️ ACTION REQUIRED | Must use Context7 MCP for: Next.js, FastAPI, SQLModel, Better Auth, framer-motion, canvas-confetti before implementation |

**Constitution Check Result**: ⚠️ **CONDITIONAL PASS** - Python version must be upgraded to 3.13+ before proceeding with implementation.

## Project Structure

### Documentation (this feature)

```text
specs/007-phase2-chronos-webapp/
├── spec.md              # Feature specification (WHAT)
├── plan.md              # This file (HOW - architecture)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Database schema and entities
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts (OpenAPI)
│   └── backend-api.yaml # FastAPI OpenAPI specification
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
backend/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── models.py        # SQLModel database models
│   ├── db.py            # Database connection and session management
│   ├── auth.py          # JWT verification middleware
│   ├── simple_auth.py   # Password hashing (REPAIR: fix bcrypt usage)
│   └── routes/
│       ├── __init__.py
│       ├── tasks.py     # Task CRUD endpoints
│       ├── auth.py      # Auth routes (signup, signin)
│       └── health.py    # Health check endpoint
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test fixtures
│   ├── test_tasks.py    # Task API tests
│   └── test_auth.py     # Auth middleware tests
├── requirements.txt     # Python dependencies (REPAIR: add missing deps)
├── pyproject.toml       # UV project configuration
└── .env                 # Environment variables (gitignored)

frontend/
├── app/
│   ├── layout.tsx       # Root layout with Better Auth session
│   ├── page.tsx         # Landing page ("The Evolution of Todo")
│   ├── (auth)/          # Auth route group
│   │   ├── signin/      # REPAIR: Create signin page (MISSING)
│   │   │   └── page.tsx # Login page
│   │   └── signup/      # REPAIR: Create signup page (MISSING)
│   │       └── page.tsx # Signup page
│   ├── dashboard/
│   │   ├── page.tsx     # Main task dashboard
│   │   └── layout.tsx   # Dashboard layout with Command Center
│   └── api/
│       └── route.ts     # API route proxy (if needed)
├── components/
│   ├── ui/              # shadcn/ui base components
│   ├── command-center/
│   │   ├── index.tsx    # Command Center bar (text input, mic placeholder)
│   │   └── command-parser.ts # Basic NLP for task creation
│   ├── task-card.tsx    # Individual task glass card
│   ├── task-list.tsx    # Task list container
│   ├── task-modal.tsx   # Glassmorphism create/edit modal
│   ├── task-filters.tsx # Filter/sort controls
│   ├── empty-state.tsx  # Illustrated empty state
│   └── confetti.tsx     # Confetti particle effect wrapper
├── lib/
│   ├── api.ts           # API client with JWT handling
│   ├── auth.ts          # Better Auth client configuration
│   └── utils.ts         # Utility functions
├── stores/
│   └── task-store.ts    # Zustand state management
├── styles/
│   └── globals.css      # Tailwind + custom glassmorphism CSS
├── package.json         # Node dependencies
├── next.config.ts       # Next.js configuration
├── tsconfig.json        # TypeScript strict config
├── tailwind.config.ts   # Tailwind theme (Deep Space colors)
└── .env.local           # Environment variables (gitignored) - REPAIR: Rotate exposed credentials

# Phase I: Console app (unchanged, reference only)
src/                      # Python console app (Phase I)

# Shared configuration
.specify/                 # Spec-Kit configuration
.claude/                  # Claude Code skills and agents
specs/                    # All feature specifications
history/                  # Prompt History Records and ADRs
```

**Structure Decision**: Monorepo with separate `frontend/` and `backend/` directories. This aligns with Phase II hackathon requirements and allows independent deployment while maintaining code organization clarity. The frontend uses Next.js App Router for optimal performance and SEO; the backend uses FastAPI for async Python capabilities.

## Complexity Tracking

> **Repair Items** - The following issues must be addressed to unblock the application:

| Issue | Severity | Impact | Fix |
|-------|----------|--------|-----|
| bcrypt 5.0 incompatibility | CRITICAL | Signup crashes, users cannot register | Pin bcrypt<5.0.0 in requirements.txt, reinstall |
| Missing dependencies | HIGH | Import errors, missing functionality | Add passlib, bcrypt<5.0.0, asyncpg, requests to requirements.txt |
| Missing auth pages | HIGH | Cannot login/signup through UI | Create signin/page.tsx and signup/page.tsx |
| Exposed credentials | SECURITY | Database URL exposed in .env.local | Rotate credentials, regenerate .env.local |
| Python version | MEDIUM | Constitution violation | Upgrade from 3.12.3 to 3.13+ |

## Phase 0: Research & Technology Decisions

This section documents the research phase outputs. See [research.md](./research.md) for detailed findings.

### Research Topics

| Topic | Decision | Rationale | Alternatives Considered |
|-------|----------|-----------|------------------------|
| **State Management** | Zustand | Lightweight, minimal boilerplate, works with React Server Components | Redux Toolkit (too complex), TanKit Query (good for server state, not UI state) |
| **Animation Library** | framer-motion | Comprehensive animation toolkit, layout animations, gesture support | AutoAnimate (simpler, but less expressive), pure CSS (insufficient for complex interactions) |
| **Confetti Library** | canvas-confetti | Lightweight, performant, easy integration | react-confetti (heavier), custom implementation (unnecessary complexity) |
| **Form Handling** | react-hook-form + zod | Minimal re-renders, excellent TypeScript support, validation built-in | Formik (older API), TanKit Form (overkill for this use case) |
| **Data Fetching** | TanStack Query (React Query) | Caching, background updates, optimistic updates, loading states built-in | SWR (simpler but fewer features), fetch/useState (too much boilerplate) |
| **Date Picker** | shadcn/ui calendar (react-day-picker) | Consistent with design system, accessible, customizable | react-datepicker (older UI), HTML input (inconsistent styling) |
| **API Client** | fetch with Zustand store wrapper | Native browser API, full control, TanStack Query for server state | axios (unnecessary dependency), ky (good but fetch is sufficient) |
| **JWT Storage** | httpOnly cookies (Better Auth) | Secure against XSS, automatic CSRF protection | localStorage (vulnerable to XSS), sessionStorage (cleared on close) |
| **Password Hashing** | passlib + bcrypt<5.0.0 | Proven secure, passlib compatibility | argon2 (slower), bcrypt 5.x (incompatible with passlib) |

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete database schema, entity definitions, and relationships.

**Key Entities**:
- **User** (managed by Better Auth): id, email, name, created_at
- **Task**: id, user_id, title, description, priority, completed, tags, due_date, recurrence_pattern, transcription_text (AI-ready), ai_summary (AI-ready), embedding_id (AI-ready), created_at, updated_at
- **TaskLog**: id, task_id, user_id, action, changed_fields, timestamp

### API Contracts

See [contracts/backend-api.yaml](./contracts/backend-api.yaml) for OpenAPI specification.

**Endpoint Summary**:

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/signup | Register new user | Public |
| POST | /api/auth/signin | Login and receive JWT | Public |
| POST | /api/auth/signout | Logout | JWT |
| GET | /api/tasks | List all tasks for user | JWT |
| POST | /api/tasks | Create new task | JWT |
| GET | /api/tasks/{id} | Get single task | JWT |
| PUT | /api/tasks/{id} | Update task | JWT |
| DELETE | /api/tasks/{id} | Delete task | JWT |
| PATCH | /api/tasks/{id}/complete | Toggle completion | JWT |
| GET | /api/tasks/search?q={query} | Search tasks | JWT |
| GET | /api/health | Health check | Public |

### Quickstart Guide

See [quickstart.md](./quickstart.md) for developer setup instructions.

## Phase 2: Implementation Planning (REPAIR FOCUS)

**Note**: Implementation tasks are generated by `/sp.tasks` command based on this plan.

### Implementation Phases (Updated for Repair)

| Phase | Focus | Tasks (Approx) | Priority |
|-------|-------|----------------|----------|
| **0.0** | **REPAIR: Environment** | Upgrade Python to 3.13+, fix .env.local credentials | CRITICAL |
| **0.1** | **REPAIR: Backend Dependencies** | Fix requirements.txt (bcrypt<5.0.0, passlib, asyncpg, requests) | CRITICAL |
| **0.2** | **REPAIR: Backend Auth** | Fix simple_auth.py to use correct bcrypt version, verify password hashing | CRITICAL |
| **0.3** | **REPAIR: Frontend Auth Pages** | Create signin/page.tsx and signup/page.tsx | HIGH |
| **2.1** | Backend Foundation | Database models, Auth middleware, Task CRUD endpoints | HIGH |
| **2.2** | Frontend Foundation | Project setup, Tailwind theme, shadcn/ui components, Routing | HIGH |
| **2.3** | Authentication Flow | Better Auth integration, Session management | HIGH |
| **2.4** | Core Task UI | Task list, Task card, Task modal, CRUD operations | MEDIUM |
| **2.5** | Advanced Features | Filters, Sort, Search, Tags, Due dates, Recurring tasks | MEDIUM |
| **2.6** | Command Center | Text input, Basic NLP parsing, Keyboard shortcuts | MEDIUM |
| **2.7** | Polish & Landing Page | Animations, Confetti, Empty states, Landing page | LOW |
| **2.8** | Testing & Deployment | Unit tests, E2E tests, Performance optimization, Deployment | LOW |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Frontend (Next.js 16)                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Pages: Landing, Signin (REPAIR), Signup (REPAIR), Dashboard         │  │
│  │  Components: TaskCard, TaskModal, TaskFilters, CommandCenter          │  │
│  │  State: Zustand (UI) + TanStack Query (server)                        │  │
│  │  Styling: Tailwind + shadcn/ui (Glassmorphism theme)                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTPS + JWT
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                         Backend (FastAPI)                                 │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  Middleware: CORS, JWT Verification                                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  Routes: /api/auth/* (REPAIR: fix bcrypt), /api/tasks/*, /api/health│  │
│  └────────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  Models: Task, TaskLog (SQLModel)                                   │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ PostgreSQL (asyncpg - REPAIR: add to requirements)
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                      Database (Neon PostgreSQL)                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  Tables: users (Better Auth), tasks, task_logs                       │  │
│  │  AI-Ready Fields: transcription_text, ai_summary, embedding_id       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Sign-off

**Plan Status**: ⚠️ **REPAIR MODE** - Critical fixes must be applied before implementation can proceed

**Critical Repairs Required**:
1. Pin `bcrypt<5.0.0` in backend/requirements.txt
2. Add missing dependencies: `passlib`, `asyncpg`, `requests`
3. Create `frontend/app/(auth)/signin/page.tsx`
4. Create `frontend/app/(auth)/signup/page.tsx`
5. Rotate exposed credentials in `frontend/.env.local`
6. Upgrade Python from 3.12.3 to 3.13+

**Constitution Re-check** (Post-Phase 1 Design):
- ✅ No Phase III features leaked into Phase II
- ✅ AI-ready fields documented in data model
- ✅ Command Center designed as extensible for voice input
- ⚠️ Python version must be 3.13+ (currently 3.12.3)

**Next Steps**:
1. Run `/sp.tasks` to generate actionable implementation tasks (including repair tasks)
2. Use Context7 MCP for all external library documentation during implementation
3. Create ADR for bcrypt version pinning: `/sp.adr bcrypt-version-pin`
4. Create ADR for credential rotation: `/sp.adr env-credential-rotation`
