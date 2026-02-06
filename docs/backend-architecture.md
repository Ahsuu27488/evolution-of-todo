# Backend Architecture — Complete Overview

**Evolution of Todo — Phase II & Phase III Backend**

Generated: 2026-02-06

---

## Table of Contents

1. [Request Flow Diagram](#request-flow-diagram)
2. [Layer-by-Layer Breakdown](#layer-by-layer-breakdown)
3. [Key Data Flows](#key-data-flows)
4. [Background Scheduler Jobs](#background-scheduler-jobs)
5. [Database Schema](#database-schema)
6. [External APIs](#external-apis)
7. [Architectural Patterns](#architectural-patterns)

---

## Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                             │
│                     (TanStack Query + Server Actions)                       │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ JWT (Bearer) + Cookies
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI APP (main.py)                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Middleware Layer                                                    │   │
│  │  • CORSMiddleware (origins, credentials)                             │   │
│  │  • ErrorHandlers (exception → ErrorResponse)                         │   │
│  │  • CorrelationMiddleware (X-Correlation-ID for distributed tracing)  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                     │                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Route Handlers (JWT → user_id via get_current_user_id)              │   │
│  │  /api/auth     → auth.py          (signup, signin, /me, /token)      │   │
│  │  /api/tasks    → tasks.py         (CRUD, search, filter)             │   │
│  │  /api/chat     → chat.py          (SSE streaming, transcription)      │   │
│  │  /api/notifications → notifications.py (SSE, preferences, webhooks)   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
        ┌────────────┬───────────────┼───────────────┬─────────────┐
        ▼            ▼               ▼               ▼             ▼
┌─────────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────────┐
│   Routes    │ │    AI    │ │  Services   │ │ External │ │ Background   │
│             │ │  Layer   │ │             │ │  APIs    │ │   Jobs       │
└─────────────┘ └──────────┘ └─────────────┘ └──────────┘ └──────────────┘
```

---

## Layer-by-Layer Breakdown

### 1. Routes Layer (`app/routes/`)

| Route | File | Purpose | Key Patterns |
|-------|------|---------|--------------|
| `/api/auth/*` | `auth.py` | Authentication | JWT generation, password hashing |
| `/api/tasks/*` | `tasks.py` | Task CRUD | Ownership verification (404 not 403) |
| `/api/chat/*` | `chat.py` | AI chatbot | SSE streaming, agent orchestration |
| `/api/notifications/*` | `notifications.py` | Notifications | SSE, webhooks, preferences |

---

### 2. AI Layer (`app/ai/`) — Phase III

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Architecture                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  MCP Server (server.py)                                  │  │
│  │  • 7 tools: add_task, list_tasks, complete_task,         │  │
│  │           delete_task, update_task, get_task,            │  │
│  │           semantic_search                                │  │
│  │  • 30-second timeout per tool (asyncio.wait_for)         │  │
│  │  • Error responses formatted for AI agent                │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │ call_tool()                          │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TaskTools (tools.py)                                    │  │
│  │  • add_task() → Creates task + Qdrant embedding          │  │
│  │  • update_task() → Updates task + refreshes embedding    │  │
│  │  • complete_task() → Toggles completed + refreshes embed │  │
│  │  • semantic_search() → Qdrant vector search OR keyword   │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────┴───────────────────────────────────┐  │
│  │  Services                                                 │  │
│  │  • OpenAIService → GPT-4o-mini chat, Whisper, embeddings  │  │
│  │  • QdrantService → Vector search with keyword fallback    │  │
│  │  • RunnerService → Chat orchestration with SSE streaming  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### MCP Tools Specification

| Tool | Purpose | Returns |
|------|---------|---------|
| `add_task` | Create new task with auto-tag extraction | Complete task data with tags |
| `list_tasks` | List tasks with optional filters | Paginated task list |
| `complete_task` | Mark task as complete | Task with completed=true |
| `delete_task` | Delete a task | All task data before deletion |
| `update_task` | Modify existing task | Updated task with all fields |
| `get_task` | Retrieve single task by ID | Complete task data |
| `semantic_search` | Search by meaning, not just keywords | Ranked results with relevance |

---

### 3. Services Layer (`app/services/`)

| Service | File | Purpose | External Dependencies |
|---------|------|---------|----------------------|
| **NotificationService** | `notification_service.py` | CRUD, deduplication, multi-channel dispatch | — |
| **SSEService** | `sse_service.py` | Real-time streaming to frontend | — |
| **EmailService** | `email_service.py` | HTML emails via Resend | Resend API |
| **PushService** | `push_service.py` | Browser push notifications | pywebpush, VAPID |
| **SchedulerService** | `scheduler_service.py` | Background cron jobs | APScheduler |
| **UnsubscribeService** | `unsubscribe_service.py` | One-click email unsubscribe | — |

---

## Key Data Flows

### Chat Flow (SSE Streaming)

```
Frontend EventSource
         │
         ▼
POST /api/chat (create conversation)
         │
         ├─→ 1. Detect language (auto/en/ur)
         ├─→ 2. Sanitize input (prompt injection protection)
         ├─→ 3. Get conversation history
         ├─→ 4. Call OpenAI Agents SDK with MCP tools
         │        │
         │        ├─→ Agent may call tools:
         │        │   • add_task → TaskTools → DB + Qdrant
         │        │   • semantic_search → Qdrant → DB
         │        │   • complete_task → DB + embedding refresh
         │        │
         │        └─→ Agent response with citations
         │
         └─→ 5. Stream response via SSE:
                  • event: message_delta (tokens streaming)
                  • event: message_complete (final message)
                  • event: error (if anything fails)
```

### Notification Flow (Multi-Channel)

```
Event Trigger (task due, completed, etc.)
         │
         ▼
NotificationService.create()
         │
         ├─→ Check deduplication window (type-aware)
         ├─→ Check user preferences (channels enabled?)
         └─→ Check DND hours (if applicable)

         │
         ▼
Dispatch (multi-channel)
         │
         ├─→ In-App: SSEService.broadcast_to_user()
         │       └─→ Frontend EventSource receives instantly
         │
         ├─→ Push: PushService.send_notification()
         │       ├─→ Check rate limit (3/hour, urgent exempt)
         │       ├─→ Encrypt payload (VAPID)
         │       └─→ pywebpush.send()
         │
         └─→ Email: EmailService.send_email()
                 ├─→ Render HTML template (dark mode aware)
                 ├─→ Thread pool executor (blocking I/O)
                 └─→ Resend API POST
```

### Semantic Search Flow

```
User query: "tasks about groceries"
         │
         ▼
semantic_search(user_id, query)
         │
         ├─→ 1. Generate query embedding
         │       └─→ OpenAI.embeddings(text-embedding-3-small)
         │
         ├─→ 2. Qdrant vector search
         │       └─→ QdrantService.search()
         │       ├─→ Filter by user_id
         │       └─→ Return top N results
         │
         └─→ 3. If Qdrant empty/fails → Keyword fallback
                 └─→ SQLAlchemy LIKE query on title/description

         │
         ▼
Return enriched results (title, description, priority, due_date, tags, completed)
```

---

## Background Scheduler Jobs

```
APScheduler (Background Thread)
         │
         ├─→ Daily Digest (8 AM user timezone)
         │       └─→ Aggregate unread notifications → HTML email
         │
         ├─→ Weekly Summary (Monday 9 AM user timezone)
         │       └─→ Task completion stats → HTML email
         │
         ├─→ Task Reminders (every 15 minutes)
         │       └─→ Find tasks due < 24h → Create notifications
         │
         └─→ Cleanup Job (daily 3 AM UTC)
                 ├─→ Soft-delete notifications > 90 days
                 └─→ Soft-delete conversations > 90 days
```

---

## Database Schema

### Key Tables

| Table | Purpose | AI-Related Fields |
|-------|---------|-------------------|
| `tasks` | Core task data | `transcription_text`, `ai_summary`, `embedding_id` |
| `conversations` | Chat sessions | `title`, `language_preference`, `message_count` |
| `messages` | Chat messages | `role`, `content`, `tool_calls` (JSONB) |
| `agent_handoffs` | Agent transitions | `from_agent`, `to_agent`, `reason`, `context_snapshot` |
| `notifications` | Notifications | `type`, `data` (JSONB), `read` |
| `users` | User accounts | `timezone`, `notification_preferences` |

### Notification Types

| Type | Deduplication Window | Priority |
|------|---------------------|----------|
| `TASK_DUE` | 5 minutes | Normal |
| `TASK_OVERDUE` | 15 minutes | High |
| `TASK_COMPLETED` | 1 minute | Low |
| `SYSTEM_UPDATE` | 24 hours | Low |

---

## External APIs

| Service | Purpose | Models/Features | Rate Limits |
|---------|---------|-----------------|-------------|
| **OpenAI** | Chat, Embeddings, Audio | GPT-4o-mini, text-embedding-3-small, whisper-1 | Per OpenAI |
| **Qdrant** | Vector embeddings storage | Semantic search with filtering | Per Qdrant Cloud |
| **Resend** | Transactional email | HTML templates, webhooks | Per Resend plan |
| **Neon PostgreSQL** | Primary database | Tasks, users, notifications, chats | Per Neon plan |

### OpenAI Cost Tracking (per spec.md FR-108)

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| `gpt-4o-mini` | $0.15 / 1M tokens | $0.60 / 1M tokens |
| `text-embedding-3-small` | $0.02 / 1M tokens | — |
| `whisper-1` | $0.006 / minute | — |

---

## Architectural Patterns

### 1. Authentication Flow

```
User Sign In/Up
    │
    ▼
Better Auth (Frontend) creates session + JWT
    │
    ▼
JWT stored in httpOnly cookie (server-side only)
    │
    ▼
API Client fetches JWT via /api/auth/token
    │
    ▼
JWT sent to FastAPI: Authorization: Bearer <token>
    │
    ▼
FastAPI verifies with BETTER_AUTH_SECRET (shared)
    │
    ▼
Extract user_id from 'sub' claim
```

**Critical**: `BETTER_AUTH_SECRET` must be identical in:
- `frontend/.env.local` (Better Auth signing)
- `backend/.env` (FastAPI verification)

### 2. Ownership Verification (404 not 403)

Throughout the codebase, when verifying a user owns a resource:
```python
async def get_task_or_404(task_id: int, user_id: str, session: AsyncSession) -> Task:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await session.execute(statement)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404)  # Not 403 — prevents enumeration
    return task
```

**Rationale**: Prevents ID enumeration attacks — attackers can't distinguish between "doesn't exist" and "exists but not yours."

### 3. SSE over WebSocket

The chat uses Server-Sent Events (`EventSourceResponse`) instead of WebSockets:
- **Simpler** for one-way streaming (server → client)
- **Better** with FastAPI's async model
- Frontend sends user messages via HTTP POST, receives stream via SSE

### 4. Circuit Breaker Pattern

```python
# app/ai/services/openai_client.py
CircuitBreaker (for OpenAI API failures)
    States: CLOSED → OPEN → HALF_OPEN → CLOSED
    Threshold: 5 failures → OPEN
    Timeout: 60 seconds before HALF_OPEN
```

### 5. Type-Aware Deduplication

Different notification types have different deduplication windows:
- **TASK_DUE**: 5 minutes (tasks can become due quickly)
- **TASK_OVERDUE**: 15 minutes (less frequent, important)
- **TASK_COMPLETED**: 1 minute (instant feedback)
- **SYSTEM_UPDATE**: 24 hours (low priority)

### 6. Dependency Injection Pattern

All protected endpoints use FastAPI's `Depends()`:
```python
@router.get("/api/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),  # ← Injects user_id from JWT
    session: AsyncSession = Depends(get_session),  # ← Injects DB session
) -> TaskList:
    # user_id is guaranteed to be valid here
    statement = select(Task).where(Task.user_id == user_id)
```

---

## File Structure Reference

```
backend/app/
├── main.py                          # Application entry point, lifespan, middleware
├── db.py                            # Async database session factory
├── models.py                        # SQLAlchemy models (Task, User, etc.)
├── errors.py                        # Custom exceptions, error handlers
├── routes/
│   ├── auth.py                      # Authentication endpoints
│   ├── tasks.py                     # Task CRUD endpoints
│   ├── chat.py                      # AI chatbot with SSE streaming
│   └── notifications.py             # Notification endpoints
├── ai/                              # Phase III namespace
│   ├── agents/
│   │   └── todo_agent.py            # OpenAI Agents SDK
│   ├── mcp/
│   │   ├── server.py                # MCP server with 7 tools
│   │   └── tools.py                 # TaskTools class
│   ├── services/
│   │   ├── runner_service.py        # Chat orchestration
│   │   ├── openai_client.py         # GPT-4o-mini, Whisper, embeddings
│   │   └── qdrant_client.py         # Vector search service
│   ├── models/
│   │   ├── conversation.py          # Conversation model
│   │   ├── message.py               # Message model
│   │   └── agent_handoff.py         # Agent handoff model
│   ├── utils/
│   │   ├── logging.py               # Structured logging (structlog)
│   │   ├── language.py              # Language detection
│   │   └── nlp.py                   # NLP utilities
│   ├── middleware.py                # CorrelationMiddleware
│   ├── rate_limit.py                # Per-user rate limiting
│   └── context.py                   # TodoContext for agents
└── services/
    ├── notification_service.py      # Notification CRUD
    ├── sse_service.py               # SSE connection manager
    ├── email_service.py             # Resend integration
    ├── push_service.py              # Web Push API
    ├── scheduler_service.py         # Background jobs
    └── unsubscribe_service.py       # Token-based unsubscribe
```

---

## Health Check Endpoint

```
GET /api/health
```

Returns:
```json
{
  "status": "ok",
  "timestamp": "2026-02-06T12:00:00Z",
  "version": "3.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 15
    },
    "qdrant": {
      "status": "healthy",
      "collection_exists": true
    }
  }
}
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-06*
