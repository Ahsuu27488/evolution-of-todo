# Evolution of Todo — Hackathon II

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents_SDK-green)](https://platform.openai.com/docs/agents)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A full-stack todo application demonstrating **Spec-Driven Development** across 5 evolutionary phases, from a simple console app to an **AI-powered chatbot with natural language task management**, cloud-deployed web application.

## Project Phases

| Phase | Status | Description | Documentation |
|-------|--------|-------------|---------------|
| **Phase I** | ✅ Complete | In-memory Python console app | [`src/README.md`](src/README.md) |
| **Phase II** | ✅ Complete | Full-stack web application | [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md) |
| **Phase III** | ✅ Complete | **AI-powered chatbot with OpenAI Agents SDK** | [`specs/012-ai-chatbot-phase3/README.md`](specs/012-ai-chatbot-phase3/README.md) |
| Phase IV | ⏳ Pending | Local Kubernetes deployment with Minikube/Helm | — |
| Phase V | ⏳ Pending | Cloud deployment with Kafka/Dapr | — |

---

## ✨ Phase III: Meet **Chronos** — Your AI Time Guardian

> *"Named after Chronos, the Greek personification of time — I am the guardian of your productivity and the keeper of your schedule."*

Phase III introduces **Chronos**, an intelligent AI assistant that transforms task management through natural conversation. Built with the **OpenAI Agents SDK** and **Model Context Protocol (MCP)**, Chronos represents the cutting edge of agentic AI technology.

### 🤖 Who is Chronos?

**Chronos** is not just another chatbot — it's a **multi-agent system** with a distinct personality and specialized capabilities:

| Attribute | Description |
|-----------|-------------|
| **Name** | Chronos (Greek: Χρόνος — personification of time) |
| **Role** | Time Guardian & Productivity Assistant |
| **Personality** | Warm but efficient, proactive, celebrates wins, mindful of work-life balance |
| **Languages** | Fluent in English and Urdu (اردو) — detects and responds in user's language |
| **Specialists** | Planning Agent (weekly scheduling), Query Agent (semantic search) |
| **Core Technology** | OpenAI Agents SDK + MCP Tools + gpt-4o-mini + Whisper API |

### 🌟 Chronos's Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHRONOS AI ASSISTANT                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   TodoAgent  │  │ PlanningAgent│  │     QueryAgent         │ │
│  │   (Chronos)  │◄─┤   (Specialist)│   │    (Specialist)       │ │
│  │              │  │  - Weekly    │  │  - Semantic Search     │ │
│  │  - Main      │  │    Planning  │  │  - Complex Filters     │ │
│  │    Interface │  │  - Priority  │  │  - Task Discovery      │ │
│  │  - Handoffs  │  │    Mgmt     │  │                        │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP TOOLS (7 Tools)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ add_task │ │list_tasks│ │complete  │ │delete_task│           │
│  └──────────┘ └──────────┘ │_task     │ └──────────┘           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                         │
│  │update_task│ │ get_task │ │semantic  │                         │
│  │          │ │          │ │_search   │                         │
│  └──────────┘ └──────────┘ └──────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 🎙️ Voice Input & Transcription

Chronos understands spoken commands through **Whisper API** integration:
- **30-second recording limit** — Quick voice memos
- **Urdu biasing** — Prevents Devanagari output for Urdu speakers
- **Ambiguity confirmation** — Asks for clarification when transcription is unclear
- **Multi-language support** — English, Urdu script (اردو), and Roman Urdu

### 🔍 Semantic Search (Vector Embeddings)

Unlike traditional keyword search, Chronos uses **Qdrant vector database** with OpenAI embeddings:
- **Search by meaning**: "grocery items" finds tasks with "buy milk", "eggs", "bread"
- **Topic discovery**: "work tasks" finds all professional-related items
- **User-scoped**: No cross-user data leakage
- **Circuit breaker**: Falls back to keyword search if Qdrant unavailable

### 🌐 Bilingual English/Urdu Support

Chronos is truly bilingual:

| Language | Support | Examples |
|----------|---------|----------|
| **English** | Full | "Add task", "Show pending", "Complete task 5" |
| **Urdu Script** (اردو) | Full with RTL | "ٹاسک شامل کرو", "میرے ٹاسکس دکھاؤ", "مکمل کر دیں" |
| **Roman Urdu** | Full | "Task add karo", "Mere tasks dikhao", "Complete kar do" |
| **Code-Switching** | Partial | "Add a task for آج" → Responds in dominant language |

### 📱 Chat Features

| Feature | Description |
|---------|-------------|
| **SSE Streaming** | Real-time token-by-token responses |
| **Conversation History** | Persistent chat sessions with auto-generated titles |
| **Tool Calling Display** | Visual feedback when Chronos uses MCP tools |
| **Agent Handoff Notifications** | Shows when Chronos transfers to specialists |
| **RTL Rendering** | Noto Nastaliq Urdu font for proper Urdu display |
| **Task Cards in Chat** | Inline task display for AI-created items |

### 💬 Example Conversations

**English:**
```
You: "I need to buy groceries tomorrow"
Chronos: "Task added! 🛒 I've created 'Buy groceries' for tomorrow with HIGH priority.
        Would you like me to add common grocery items as subtasks?"

You: "Show me my work tasks"
Chronos: [Handing off to QueryAgent] "Let me search for your work-related tasks..."
        [Returns 5 tasks via semantic search]
```

**Urdu:**
```
You: "کل میری میٹنگ ہے"
Chronos: "ٹاسک شامل کر دیا گیا! میں نے 'میری میٹنگ' کل کے لیے HIGH ٹاولیرنٹی کے ساتھ شامل کر دیا۔
        [Task added! I've added 'My meeting' for tomorrow with HIGH priority.]"
```

---

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

### Phase III (AI Chatbot) ⭐ NEW

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Framework** | OpenAI Agents SDK | Multi-agent system |
| **Model** | gpt-4o-mini | Main chat model |
| **Embeddings** | text-embedding-3-small | Vector search (1536 dims) |
| **Voice** | Whisper API (whisper-1) | Audio transcription |
| **Vector DB** | Qdrant Cloud | Semantic search storage |
| **MCP Protocol** | Official MCP SDK | Tool calling interface |
| **Language Detection** | langdetect | English/Urdu detection |
| **Logging** | structlog | Structured JSON logging |
| **Rate Limiting** | slowapi | Per-user API limits |

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
# Database
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-32-character-secret-here
CORS_ORIGINS=http://localhost:3000

# Phase III: AI Features (NEW)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_WHISPER_MODEL=whisper-1

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Feature Flags
PHASE_III_ENABLED=true
MAX_MESSAGE_LENGTH=5000
MAX_AUDIO_SIZE_MB=25
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
# Database (shared with backend)
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Authentication (MUST match backend!)
BETTER_AUTH_SECRET=your-32-character-secret-here
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Phase III: OpenAI (for chatbot)
OPENAI_API_KEY=sk-your-openai-api-key
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

## Troubleshooting

### Dropdown Menus Not Visible

**Symptom:** Clicking dropdown menus (sort, filters, date picker) doesn't show any options.

**Cause:** Ad blocker extensions (AdLock, uBlock Origin, AdBlock Plus, etc.) may mistakenly block Portal-rendered UI components, thinking they are popup advertisements.

**Solutions:**

1. **Disable Ad Blocker** (quickest test)
   - Open your browser in incognito/private mode (extensions disabled by default)
   - Or disable the ad blocker extension temporarily
   - Test if dropdowns appear correctly

2. **Whitelist localhost** (recommended)
   - Add `localhost:3000` to your ad blocker's allowlist
   - For AdLock: Settings → Whitelist → Add `localhost:3000`
   - For uBlock Origin: Click the icon → Dashboard → Whitelist → `localhost:3000`

3. **Production Deployment**
   - If deploying to production, add your domain to the ad blocker's allowlist
   - Document this in your user-facing help section

**Why This Happens:**
The app uses Radix UI's Portal component to render dropdowns, which places them in `document.body` for proper z-index layering. Ad blockers see this pattern and mistakenly identify these legitimate UI components as popup ads, since both use:
- Portal rendering to `document.body`
- `position: fixed` or `absolute` positioning
- High z-index values
- Overlay behavior

**Affected Browsers:**
- Chrome / Chromium-based browsers (Edge, Brave, Opera)
- Mostly affects desktop browsers with extensions installed
- Mobile browsers typically unaffected

**Unaffected Browsers:**
- Firefox (different extension architecture)
- Safari (different ad blocking approach)
- Mobile browsers (fewer extensions)

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

#### Core Task Management
- ✅ User registration and email/password authentication
- ✅ User profile with first name and last name fields (supports mononyms)
- ✅ Edit profile functionality with timezone support
- ✅ JWT-based session management
- ✅ Task CRUD with optimistic UI updates
- ✅ Task filtering by status, priority, tags
- ✅ Task search and sorting
- ✅ Data isolation between users
- ✅ Recurring tasks (daily/weekly/monthly)
- ✅ Audit trail for task modifications
- ✅ Zero-downtime database migrations

#### User Experience
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark mode support with Deep Space theme
- ✅ Enhanced loading states with dual-ring spinner animation
- ✅ Inline error handling with retry functionality
- ✅ Toast notifications via sonner

#### Notification System
- ✅ **In-App Notifications** — Real-time notification center with SSE streaming
- ✅ **Push Notifications** — Web Push API with browser notifications
- ✅ **Email Notifications** — Transactional emails via Resend
- ✅ **Digest Emails** — Daily (8 AM) and weekly (Monday 9 AM) digests with timezone support
- ✅ **Notification Preferences** — Per-channel enable/disable settings
- ✅ **Do Not Disturb Hours** — Silence notifications during specific times
- ✅ **One-Click Unsubscribe** — Token-based email unsubscribe
- ✅ **Webhook Tracking** — Email delivery status (sent, delivered, opened, bounced)
- ✅ **Rate Limiting** — Push notifications limited to 3/hour (urgent exempt)

### API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user (with first name, last name) |
| POST | `/api/auth/signin` | Login and get JWT |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/me` | Update current user profile |

#### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks (filter, sort, paginate) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/search` | Search tasks |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |
| GET | `/api/tasks/{id}/logs` | Get audit logs |

#### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications (with unread count) |
| PUT | `/api/notifications/{id}/read` | Mark notification as read |
| POST | `/api/notifications/mark-all-read` | Mark all as read |
| DELETE | `/api/notifications/{id}` | Delete notification |
| GET | `/api/notifications/stream` | SSE stream for real-time updates |
| GET | `/api/notifications/settings` | Get notification preferences |
| PUT | `/api/notifications/settings` | Update notification preferences |

#### Push Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notifications/push/subscribe` | Subscribe to push |
| DELETE | `/api/notifications/push/unsubscribe` | Unsubscribe from push |
| GET | `/api/notifications/push/status` | Get subscription status |
| POST | `/api/notifications/push/test` | Send test push notification |

#### Email Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/email/preferences` | Get email preferences |
| PUT | `/api/notifications/email/preferences` | Update email preferences |
| POST | `/api/notifications/email/test` | Send test email |
| POST | `/api/notifications/email/webhook` | Resend webhook handler |

#### AI Chatbot (Phase III) ⭐ NEW
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to Chronos (SSE streaming) |
| POST | `/api/chat/transcribe` | Transcribe audio file (Whisper) |
| GET | `/api/chat/conversations` | List all conversations |
| GET | `/api/chat/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/chat/conversations/{id}` | Delete conversation |

**Chronos AI Capabilities:**
- 🤖 Multi-agent system (TodoAgent, PlanningAgent, QueryAgent)
- 🔍 Semantic search via vector embeddings (Qdrant)
- 🎙️ Voice input via Whisper API
- 🌐 Bilingual English/Urdu with RTL support
- 🛠️ 7 MCP tools for task management
- 📊 Real-time SSE streaming responses

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
