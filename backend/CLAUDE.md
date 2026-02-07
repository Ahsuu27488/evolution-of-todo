# backend/ — Chronos Todo API

**Claude Code Context** for the FastAPI backend (Phase II + Phase III AI Chatbot).

## Version: 3.0.0

Current implementation includes:
- **Phase II**: Full-stack web API with task CRUD, notifications, and authentication
- **Phase III**: AI chatbot with OpenAI Agents SDK, semantic search, and voice transcription

---

## Project Purpose

FastAPI REST API serving the Evolution of Todo application with:
- Task CRUD operations with filtering, sorting, search
- JWT authentication compatible with Better Auth
- Async PostgreSQL database operations
- Audit trail for all task modifications
- **Comprehensive notification system** (SSE, push, email, digests)
- **AI-powered chatbot** for natural language task management
- **Semantic search** using vector embeddings
- **Voice input** via Whisper transcription

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application v3.0                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  CORS Mdw    │  │ Correlation  │  │ Rate Limiting            │  │
│  │              │  │ ID Mdw       │  │ (per-user)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│        └──────────────────┴────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            API Routes                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  /api/auth   │  │  /api/tasks  │  │  /api/chat              │  │
│  │  - signup    │  │  - CRUD      │  │  - SSE streaming         │  │
│  │  - signin    │  │  - search    │  │  - transcribe (Whisper)  │  │
│  │  - me        │  │  - filter    │  │  - conversations         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           /api/notifications/*                             │  │
│  │  - In-app (SSE), Push, Email, Digest                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Phase III: AI Layer                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  OpenAI Agents   │  │  MCP Tools       │  │  Qdrant Vector  │  │
│  │  SDK             │  │  (Task Ops)      │  │  Database       │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐                       │
│  │  Whisper         │  │  Language Detect │                       │
│  │  Transcription   │  │  (Urdu/English)  │                       │
│  └──────────────────┘  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Database (Neon PostgreSQL)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   tasks      │  │  task_logs   │  │  conversations           │  │
│  │   (JSONB)    │  │  (audit)     │  │  messages                │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                               │
│  │ notifications│  │  agent_handoffs│                               │
│  │  (multi-chan)│  │  (tracking)   │                               │
│  └──────────────┘  └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Background Scheduler (APScheduler)                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  Daily Digest   │  │  Weekly Summary  │  │  Task Reminders │  │
│  │  (8 AM user tz)  │  │  (Mon 9 AM tz)   │  │  (every 15 min) │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Task Implementation Guidelines (CRITICAL for Long-Running Sessions)

**IMPORTANT**: When implementing multiple tasks (e.g., via `/sp.implement`), follow this pattern to prevent context loss and hallucinations during session compactions:

1. **Complete ONE task at a time** — Finish implementing, testing, and verifying a single task before moving to the next
2. **Mark task as complete immediately** — Update task status in `tasks.md` to `completed` before starting the next task
3. **Re-read tasks.md after each task** — After marking complete, re-read `tasks.md` to refresh context on remaining tasks
4. **Verify code state** — Before proceeding, confirm the current codebase state matches expected changes
5. **Commit after logical checkpoints** — After every 2-3 completed tasks or when a milestone is reached

**Why this matters:**
- Session compaction after ~200K tokens compresses conversation history
- Without checkpoints, the agent loses track of:
  - Which tasks were already completed
  - Current codebase state
  - Decisions made during implementation
- This leads to hallucinations, repeated work, or contradicting changes

**Mandatory Pattern:**
```
1. Read task details from tasks.md
2. Implement task
3. Test/verify implementation
4. Update tasks.md: change status to "completed"
5. Re-read tasks.md to see remaining work
6. Proceed to next task
```

---

## Debugging Workflow

**IMPORTANT**: Always use the `superpowers:systematic-debugging` skill when encountering bugs, errors, or unexpected behavior in the backend.

### When to Use Systematic Debugging

Invoke this skill before attempting to fix:
- API endpoint errors (4xx/5xx responses)
- Database query failures
- Authentication/authorization issues
- AI service failures (OpenAI, Qdrant, Whisper)
- Notification delivery problems
- Test failures

### Debugging Backend Issues

The systematic debugging skill will help you:

1. **Gather Context**: Check logs (structlog JSON output), correlation IDs, error traces
2. **Check Dependencies**: Verify database connectivity, external API status, environment variables
3. **Form Hypotheses**: Based on error patterns and code flow
4. **Test Locally**: Use Swagger UI (`/docs`) to reproduce issues
5. **Implement Fix**: Make targeted changes based on evidence

**Backend-Specific Debugging Tips**:
- Check `/api/health` endpoint for service status
- Review `structlog` output with correlation ID tracing
- Verify JWT tokens with shared `BETTER_AUTH_SECRET`
- Test database queries in the Python REPL
- Use Swagger UI at `http://localhost:8000/docs` for manual API testing

---

## Key File Locations

### Core Application
| File | Purpose | Key Details |
|------|---------|-------------|
| `main.py` | FastAPI app | Lifespan, CORS, middleware, Qdrant init, scheduler |
| `db.py` | Database config | Async engine, session factory, table creation |
| `models.py` | Data models | Task, TaskLog, Tag, User, Pydantic schemas |
| `errors.py` | Error handling | Custom exceptions, error middleware |
| `simple_auth.py` | JWT auth | Token verification, password hashing, dependencies |

### Routes
| File | Purpose | Key Details |
|------|---------|-------------|
| `routes/tasks.py` | Task endpoints | CRUD, search, filtering, audit logs |
| `routes/auth.py` | Auth endpoints | Signup, signin, /me, profile updates |
| `routes/notifications.py` | Notification endpoints | SSE, push, email, preferences |
| `routes/chat.py` | Chatbot endpoints (Phase III) | SSE streaming, transcription, conversations |

### Services
| File | Purpose | Key Details |
|------|---------|-------------|
| `services/notification_service.py` | Notification core | CRUD, deduplication, multi-channel dispatch |
| `services/sse_service.py` | SSE streaming | Real-time notification updates |
| `services/push_service.py` | Web Push API | VAPID, rate limiting (3/hour), subscription mgmt |
| `services/email_service.py` | Resend integration | HTML templates, webhooks, unsubscribe |
| `services/scheduler_service.py` | Background jobs | Digest emails, reminders, cleanup (779 lines) |
| `services/unsubscribe_service.py` | Token-based unsubscribe | RFC 8058 compliant |

### AI Services (Phase III)
| File | Purpose | Key Details |
|------|---------|-------------|
| `ai/services/openai_client.py` | OpenAI API | Chat (gpt-4o-mini), embeddings, Whisper (596 lines) |
| `ai/services/qdrant_client.py` | Vector database | Semantic search, user-scoped, circuit breaker (591 lines) |
| `ai/services/runner_service.py` | Agent execution | Streaming, tool calling, handoffs |
| `ai/agents/todo_agent.py` | Multi-agent system | TodoAgent + PlanningAgent + QueryAgent |
| `ai/mcp/tools.py` | MCP tools | Task operations for agent invocation |

### AI Models (Phase III)
| File | Purpose | Key Details |
|------|---------|-------------|
| `ai/models/conversation.py` | Chat sessions | Message history, title generation, soft delete |
| `ai/models/message.py` | Messages | Role-based (user/assistant/tool), tool_calls tracking |
| `ai/models/conversation_preference.py` | User settings | Language preference, theme |
| `ai/models/agent_handoff.py` | Handoff tracking | Agent transfer audit trail |

### AI Utilities (Phase III)
| File | Purpose | Key Details |
|------|---------|-------------|
| `ai/utils/logging.py` | Structured logging | Correlation ID, context propagation (479 lines) |
| `ai/utils/language.py` | Language detection | Urdu/English detection, code-switching (330 lines) |
| `ai/utils/sanitize.py` | Input sanitization | Prompt injection detection (242 lines) |
| `ai/middleware.py` | Correlation middleware | Distributed tracing across async boundaries |

---

## Complete Technology Stack

### Core Framework
- **Python 3.13+** (strict requirement per constitution §V.1.1)
- **FastAPI 0.109+** — Async REST framework
- **Uvicorn 0.27+** — ASGI server
- **Pydantic 2.0+** — Request/response validation

### Database & ORM
- **PostgreSQL** (via Neon) — Primary database with JSONB support
- **SQLModel** — ORM with Pydantic integration
- **asyncpg** — Async PostgreSQL driver
- **SQLAlchemy** — Core ORM engine (async)

### Authentication
- **Better Auth** — Frontend JWT authentication
- **python-jose[cryptography]** — JWT token verification
- **bcrypt 3.2.2** — Password hashing (pinned for passlib compatibility)
- **passlib** — Password hashing abstraction

### Notification System
- **sse-starlette** — Server-Sent Events for real-time updates
- **pywebpush** — Web Push API for browser notifications
- **resend** — Email delivery service
- **svix** — Webhook signature verification

### AI & Phase III Features
- **openai-agents** — OpenAI Agents SDK for multi-agent chatbot
- **openai 1.60+** — OpenAI API client
  - gpt-4o-mini for chat
  - text-embedding-3-small for embeddings (1536 dimensions)
  - whisper-1 for audio transcription
- **mcp** — Model Context Protocol SDK for tools
- **qdrant-client** — Vector database client for semantic search
- **structlog** — Structured JSON logging
- **langdetect** — Language detection (Urdu/English)
- **aiofiles** — Async file operations for audio
- **slowapi** — Rate limiting

---

## Phase III: AI Chatbot Features

### Agent Architecture

```
User Message
      │
      ▼
┌─────────────────┐
│  TodoAgent      │ ← Main agent for general task operations
│  (gpt-4o-mini)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────────┐ ┌──────────┐
│Planning  │ │  Query  │ ← Handoff for specialized operations
│Agent     │ │  Agent  │
└──────────┘ └──────────┘
```

### Tool Calling (MCP)

The AI agent can invoke these MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create task with auto-tag extraction | title, description, priority, due_date, tags |
| `list_tasks` | List tasks with filters | status, priority, tags, limit |
| `complete_task` | Mark task as complete | task_id |
| `update_task` | Modify task properties | task_id, fields to update |
| `delete_task` | Remove task | task_id |
| `get_task` | Get task details | task_id |
| `semantic_search` | Vector-based task search | query, limit |

**Location**: `app/ai/mcp/tools.py`

### Semantic Search

- Uses OpenAI **text-embedding-3-small** (1536 dimensions)
- Stored in **Qdrant** vector database
- User-scoped search (no cross-user data leakage)
- Falls back to keyword search if Qdrant unavailable
- Circuit breaker pattern for Qdrant failures

**Location**: `app/ai/services/qdrant_client.py`

### Voice Input (Whisper)

- Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm
- Max file size: 25 MB
- Auto-detects language (English/Urdu)
- **Urdu biasing** prevents Devanagari output (critical for Urdu speakers)
- Prompt includes Urdu script to guide Whisper away from Hindi/Devanagari

**Location**: `app/ai/services/openai_client.py:335-431`

### Language Support

| Language | Support Level | Detection Method |
|----------|---------------|------------------|
| English | Full | Default |
| Urdu Script (اردو) | Full with RTL | >30% Arabic Unicode chars |
| Roman Urdu | Full | Common word detection |
| Code-Switching | Partial | Dominant script detection |

**Location**: `app/ai/utils/language.py`

### Conversation Management

- **Auto-title generation**: First message = truncated title (50 chars), third message = AI-generated title
- **Soft delete**: 90-day archive for deleted conversations
- **Message pagination**: 50 messages per page
- **Tool call tracking**: All tool invocations stored for context
- **Agent handoff logging**: All transfers recorded for debugging

**Location**: `app/routes/chat.py`

---

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Create new user account |
| POST | `/signin` | Sign in with email/password |
| GET | `/me` | Get current user profile |
| PUT | `/profile` | Update user profile |

### Tasks (`/api/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List tasks with filtering |
| POST | `/` | Create new task |
| GET | `/{task_id}` | Get task details |
| PUT | `/{task_id}` | Update task |
| DELETE | `/{task_id}` | Delete task |
| POST | `/{task_id}/complete` | Toggle task completion |
| GET | `/{task_id}/logs` | Get task audit logs |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List notifications |
| PUT | `/{id}/read` | Mark as read |
| PUT | `/read-all` | Mark all as read |
| GET | `/settings` | Get notification preferences |
| PUT | `/settings` | Update preferences |
| GET | `/stream` | SSE notification stream |
| POST | `/push/subscribe` | Subscribe to push notifications |
| DELETE | `/push/unsubscribe` | Unsubscribe from push |
| POST | `/email/unsubscribe` | One-click email unsubscribe (RFC 8058) |

### Chat (Phase III) (`/api/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Send chat message (SSE streaming) |
| POST | `/transcribe` | Transcribe audio file (Whisper) |
| GET | `/conversations` | List conversations |
| GET | `/conversations/{id}` | Get conversation with paginated messages |
| DELETE | `/conversations/{id}` | Delete conversation |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with DB/Qdrant status |
| GET | `/` | Root endpoint with API info |
| GET | `/docs` | Interactive API documentation (Swagger) |

---

## Architecture Patterns

### Dependency Injection for Auth

All protected endpoints use `get_current_user_id` dependency:

```python
@router.get("/api/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),  # ← Injects user_id from JWT
    session: AsyncSession = Depends(get_session),  # ← Injects DB session
) -> TaskList:
    # user_id is guaranteed to be valid here
    statement = select(Task).where(Task.user_id == user_id)
```

### Async Database Sessions

Database operations use SQLAlchemy async:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### Error Handling Hierarchy

```
Exception (base)
    │
    ├── HTTPException (FastAPI)
    │     └── Handled by http_exception_handler → 4xx/5xx response
    │
    └── AppException (custom)
            ├── AuthenticationError → 401
            ├── AuthorizationError → 403
            ├── NotFoundError → 404
            ├── ValidationError → 422
            └── DatabaseError → 500
```

### Correlation ID Tracking

Every request gets a unique correlation ID for distributed tracing across:
- API calls
- MCP tool invocations
- Agent handoffs
- External API calls (OpenAI, Qdrant, Whisper)

**Implementation**: `app/ai/middleware.py`

### Circuit Breaker Pattern

Applied to external API failures:

| Service | Threshold | Timeout | Fallback |
|---------|-----------|---------|----------|
| OpenAI | 5 failures | 60 seconds | Return error |
| Qdrant | 3 failures | 30 seconds | Keyword search |

**Location**: `app/ai/services/openai_client.py:530-595`, `app/ai/services/qdrant_client.py:77-132`

---

## Security Features

### Authentication
- JWT signed with BETTER_AUTH_SECRET
- HS256 algorithm
- `sub` claim contains user ID
- Token extracted from `Authorization: Bearer <token>` header

### Rate Limiting
- 30 requests/minute per user (default)
- 10 req/min for transcription (expensive operation)
- Sliding window algorithm
- Returns 429 with `Retry-After` header

**Location**: `app/ai/rate_limit.py`

### Input Sanitization
- Prompt injection detection with pattern matching
- Max message length: 5000 characters
- System instruction redaction from outputs
- Repeated character reduction

**Location**: `app/ai/utils/sanitize.py`

### Data Isolation
- All queries scoped to user_id
- Vector search scoped to user_id
- 404 instead of 403 for ownership verification (prevents enumeration)

---

## Environment Variables

### Required
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
```

### Phase III: AI Features
```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_WHISPER_MODEL=whisper-1

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Features
PHASE_III_ENABLED=true
MAX_MESSAGE_LENGTH=5000
MAX_AUDIO_SIZE_MB=25
```

### Notification System
```bash
# Resend Email
RESEND_API_KEY=re_...

# Web Push
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_PUBLIC_KEY=your-vapid-public-key

# Webhook Secret
WEBHOOK_SECRET=your-webhook-secret

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### CORS
```bash
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Connection Pool Settings

Optimized for serverless Neon:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `pool_size` | 5 | Min connections per Neon quickstart |
| `max_overflow` | 15 | Max additional connections (total: 20) |
| `pool_recycle` | 300s | Recycle before Neon closes idle |
| `pool_pre_ping` | True | Verify connections before use |
| `echo` | DEBUG | SQL logging in development only |

---

## Background Jobs (Scheduler)

The scheduler runs these periodic tasks:

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Digest | 8 AM user time | Email summary of pending tasks |
| Weekly Summary | Monday 9 AM user time | Weekly task overview |
| Task Reminders | Every 15 min | Tasks due within 24 hours |
| Cleanup | Daily 2 AM UTC | Soft-delete old notifications (30-day archive) |

**Location**: `app/services/scheduler_service.py`

---

## Notification System Details

### Notification Types

- `TASK_DUE` — Task due soon (within 1 hour)
- `TASK_OVERDUE` — Task is overdue
- `TASK_COMPLETED` — Task marked complete
- `TASK_ASSIGNED` — Task assigned to user
- `SYSTEM_UPDATE` — System notifications
- `WELCOME` — Welcome email for new users

### Deduplication Windows

| Type | Window | Purpose |
|------|--------|---------|
| TASK_DUE | 5 minutes | Tasks can become due quickly |
| TASK_OVERDUE | 15 minutes | Less frequent, important |
| TASK_COMPLETED | 1 minute | Instant feedback |
| SYSTEM_UPDATE | 24 hours | Low priority |

### Push Notification Rate Limiting

- 3 push notifications per hour per user
- Urgent notifications (TASK_DUE, TASK_OVERDUE) are exempt
- Tracked in-memory with sliding window

---

## Important Constraints

- **All endpoints return JSON** — No HTML responses
- **404 not 403** for ownership checks — Prevents ID enumeration
- **Token must include `sub` claim** — User ID extracted from JWT
- **Tags stored as JSONB** — Max 10 tags, validated in Pydantic
- **Python 3.13+** — Strict requirement per constitution

---

## Task Deletion: Foreign Key Cascade

Tasks have multiple dependent records that must be deleted in a specific order:

```
tasks → notifications → email_delivery_logs
         ↓
         task_logs
```

When deleting a task:
1. Find notification IDs that reference the task
2. Delete `email_delivery_logs` for those notifications
3. Delete `notifications` that reference the task
4. Delete `task_logs` for the task
5. Delete the `task` itself

**Location**: `routes/tasks.py:455-491`

---

## Extension Points

### AI Field Usage (Pre-provisioned in Task Model)

```python
# Phase III: Store voice transcription
task.transcription_text = transcribe_audio(audio_file)

# Phase III: Store LLM summary
task.ai_summary = generate_summary(task.title, task.description)

# Phase III: Store vector embedding
task.embedding_id = vector_store.embed(task.title + " " + task.description)
```

### Adding New Agents

1. Create agent class in `app/ai/agents/`
2. Register in `app/ai/agents/__init__.py`
3. Add handoff logic in `TodoAgent`
4. Update system prompts for language support

### Adding New MCP Tools

1. Define tool function in `app/ai/mcp/tools.py`
2. Register with `@mcp.tool()` decorator
3. Add to agent's tool list in `todo_agent.py`
4. Update tool calling logic in `runner_service.py`

---

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_mcp/test_tools.py
```

---

## Deployment Notes

### Environment Variables for Production
- Set `DEBUG=false`
- Use strong `BETTER_AUTH_SECRET` (32+ chars)
- Configure `CORS_ORIGINS` for production domain
- Set `DATABASE_URL` to production PostgreSQL
- Configure `QDRANT_URL` for vector search
- Set `RESEND_API_KEY` for emails

### Health Checks
- `/api/health` returns status of database and Qdrant
- Use for load balancer health checks
- Returns 503 if any critical service is down
