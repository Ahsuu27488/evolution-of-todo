@/home/ahsan/Dev/Hackathons/evolution-of-todo/specs/012-ai-chatbot-phase3/CLAUDE.md
# Evolution of Todo — Project Architecture

**Claude Code Context** for the Evolution of Todo Hackathon II project.

## Project Overview

This is a **5-phase evolution** demonstrating Spec-Driven Development:
- **Phase I** (Complete): In-memory Python console app
- **Phase II** (Complete): Full-stack web app (Next.js + FastAPI + Neon DB)
- **Phase III** (Complete): **AI chatbot "Chronos" with OpenAI Agents SDK + MCP** ⭐
- **Phase IV** (Pending): Local K8s deployment with Minikube/Helm
- **Phase V** (Pending): Cloud deployment with Kafka/Dapr

## Directory-Level Context

| Directory | Purpose | Context File |
|-----------|---------|--------------|
| `src/` | Phase I console app | [`src/CLAUDE.md`](src/CLAUDE.md) |
| `backend/` | Phase II FastAPI backend | [`backend/CLAUDE.md`](backend/CLAUDE.md) |
| `frontend/` | Phase II Next.js frontend | [`frontend/CLAUDE.md`](frontend/CLAUDE.md) |

## Cross-Phase Architectural Rules

### 1. Authentication Flow

The project uses a **shared JWT secret** architecture:

```
┌─────────────┐     Sign In/Up      ┌──────────────┐
│   Frontend  │─────────────────────▶│  Better Auth│
│  (Next.js)  │                     │  (Frontend)  │
└─────────────┘                     └──────────────┘
      │                                     │
      │  Generates JWT with BETTER_AUTH_SECRET
      │                                     │
      ▼                                     │
┌─────────────┐                             │
│ API Client  │◀────────────────────────────┘
│             │  Fetches JWT from /api/auth/token
└─────────────┘
      │
      │  Sends: Authorization: Bearer <JWT>
      ▼
┌──────────────┐
│  FastAPI     │  Verifies JWT with same BETTER_AUTH_SECRET
│  Backend     │  Extracts user_id from 'sub' claim
└──────────────┘
```

### 2. Shared Secret Requirement

`BETTER_AUTH_SECRET` MUST be identical in:
1. `frontend/.env.local` — Better Auth signing
2. `backend/.env` — FastAPI verification

Length: ≥32 characters
Algorithm: HS256 (symmetric)

### 3. Task Data Model Evolution

The Task model is consistent across phases:

```python
# Phase I (src/todo/domain/task.py)
@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: Priority  # HIGH, MEDIUM, LOW
    tags: set[str]
    completed: bool
    created_at: datetime
    due_date: date | None
    recurrence: Recurrence  # NONE, DAILY, WEEKLY, MONTHLY
```

```python
# Phase II (backend/app/models.py)
class Task(SQLModel, table=True):
    id: int
    user_id: str  # Added for multi-user
    title: str
    description: str | None
    priority: Priority
    tags: list[Tag]  # Now JSONB with colors
    completed: bool
    created_at: datetime
    due_date: datetime | None
    recurrence_pattern: RecurrencePattern | None

    # Phase III AI-ready fields (pre-provisioned)
    transcription_text: str | None
    ai_summary: str | None
    embedding_id: str | None
```

### 4. Repository Pattern

Both Phase I and Phase II use the Repository pattern:

```python
# Abstract interface
class TaskRepository(ABC):
    def add(self, task: Task) -> Task: ...
    def get(self, task_id: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, task: Task) -> Task: ...
    def delete(self, task_id: int) -> bool: ...

# Phase I: In-memory implementation
class InMemoryTaskRepository(TaskRepository): ...

# Phase II: SQLModel implementation (planned)
class SQLModelTaskRepository(TaskRepository): ...
```

### 5. Error Handling Strategy

#### Backend (FastAPI)

```python
# Returns 404 (not 403) for ownership verification
# to prevent ID enumeration attacks

if task.user_id != current_user_id:
    raise HTTPException(status_code=404)
```

#### Frontend (Next.js)

```typescript
// Result type for error handling
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

// Usage
const result = await api.createTask(data)
if (result.success) {
  // Handle success
} else {
  // Handle error
  toast.error(result.error.message)
}
```

## Workflow Preferences

### When Debugging

**IMPORTANT**: Always use the `superpowers:systematic-debugging` skill when:
- Encountering bugs or errors
- Investigating unexpected behavior
- Debugging test failures
- Troubleshooting production issues

This skill provides a structured approach to debugging:
1. Gather information about the issue
2. Form hypotheses about root causes
3. Design tests to validate hypotheses
4. Implement fixes systematically
5. Verify solutions work

**Usage**: Invoke the skill before attempting to fix any bug. The skill will guide you through proper investigation rather than jumping to conclusions.

### When Working on Backend

1. **Always read existing models first** — Check `backend/app/models.py`
2. **Use async/await throughout** — All database operations are async
3. **Return TaskPublic from endpoints** — Never expose internal fields
4. **Create audit logs** — Use `create_task_log()` for modifications
5. **Test with Swagger UI** — Available at http://localhost:8000/docs

### When Working on Frontend

1. **Server Components by default** — Only use `"use client"` when necessary
2. **Use TanStack Query for server state** — Never duplicate in Zustand
3. **Use Zustand for client UI state** — Filters, modals, toasts
4. **All API calls go through api-client** — Don't use fetch directly
5. **Form validation with Zod** — Match backend validation rules

### When Adding Features

1. **Update Phase I first** — Prove the concept in the console app
2. **Add to backend models** — Include AI-ready fields for Phase III
3. **Create backend endpoints** — With proper error handling
4. **Add to frontend API client** — Auto-fetches JWT
5. **Build UI components** — Use shadcn/ui patterns

## Important Constraints

### Security

- **Never hardcode secrets** — Use `.env` files
- **404 not 403 for ownership checks** — Prevents enumeration
- **JWT in httpOnly cookies** — Never localStorage
- **SQL injection protection** — Use parameterized queries

### Performance

- **Connection pooling** — Backend uses asyncpg pool
- **Pagination** — Default 50 items per page
- **Request timeout** — 15 seconds for API calls
- **Automatic retry** — For transient network failures

### Phase Isolation

When working on a phase, **do not modify** other phases' code unless:
1. Fixing a bug that affects all phases
2. Updating shared documentation
3. Explicitly evolving to the next phase

## Extension Points

### Extension Points

### Phase III: AI Integration ⭐ COMPLETE

**Meet Chronos — Your AI Time Guardian**

Phase III introduces a sophisticated multi-agent AI system named **Chronos** (Greek: Χρόνος, personification of time). Built with the **OpenAI Agents SDK** and **Model Context Protocol (MCP)**, Chronos represents the cutting edge of agentic AI technology.

#### Chronos's Identity

| Attribute | Value |
|-----------|-------|
| **Name** | Chronos (Time Guardian) |
| **Origin** | Greek mythology — personification of time |
| **Role** | Guardian of users' productivity and time |
| **Personality** | Warm, efficient, proactive, bilingual |
| **Core Model** | gpt-4o-mini |
| **Specialists** | PlanningAgent (weekly scheduling), QueryAgent (semantic search) |
| **Languages** | English + Urdu (اردو) with RTL support |

#### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHRONOS (Main Agent)                          │
│                   Name: Chronos (Time Guardian)                  │
├─────────────────────────────────────────────────────────────────┤
│  Personality: Warm but respectful of time, proactive             │
│  Celebrates: Task completions with encouraging messages         │
│  Balance: Encourages work-life balance and rest                 │
│  Bilingual: Detects and responds in English or Urdu (اردو)      │
├─────────────────────────────────────────────────────────────────┤
│  MCP Tools (7 total):                                             │
│    ├── add_task (with auto-tag extraction from natural language) │
│    ├── list_tasks (with status, priority filters)               │
│    ├── complete_task (with task ID validation)                  │
│    ├── update_task (modify properties, tags, priority)           │
│    ├── delete_task (with confirmation)                           │
│    ├── get_task (detailed task information)                     │
│    └── semantic_search (vector embeddings via Qdrant)           │
├─────────────────────────────────────────────────────────────────┤
│  Handoffs to Specialists:                                         │
│    ├── PlanningAgent — Weekly planning, prioritization          │
│    └── QueryAgent — Semantic search, complex filters            │
└─────────────────────────────────────────────────────────────────┘
```

#### AI-Ready Fields (Now Active)

The following pre-provisioned fields are now fully utilized:

```python
# Backend (backend/app/models.py)
task.transcription_text  # Voice input storage (Whisper API)
task.ai_summary         # LLM-generated summary (planned)
task.embedding_id       # Vector search ID (Qdrant integration active)
```

```typescript
// Frontend (types/task.ts)
export interface Task {
  transcription_text: string | null  // Transcribed voice memos
  ai_summary: string | null          // AI-generated summaries
  embedding_id: string | null        // Vector embeddings for search
}
```

#### Phase III Technologies

| Technology | Purpose | Location |
|------------|---------|----------|
| **OpenAI Agents SDK** | Multi-agent orchestration | `backend/app/ai/agents/` |
| **gpt-4o-mini** | Main chat model | OpenAI API |
| **text-embedding-3-small** | Vector embeddings (1536 dims) | Qdrant storage |
| **Whisper API (whisper-1)** | Voice transcription | `backend/app/ai/services/openai_client.py` |
| **Qdrant Cloud** | Vector database for semantic search | `backend/app/ai/services/qdrant_client.py` |
| **MCP SDK** | Model Context Protocol for tool calling | `backend/app/ai/mcp/` |
| **langdetect** | English/Urdu language detection | `backend/app/ai/utils/language.py` |
| **structlog** | Structured JSON logging | `backend/app/ai/utils/logging.py` |

#### Key Features

1. **Natural Language Task Management**: Chat with Chronos to create, complete, update, and delete tasks
2. **Semantic Search**: Find tasks by meaning using vector embeddings ("grocery items" finds "buy milk", "eggs")
3. **Voice Input**: Record voice memos (30s limit) transcribed via Whisper API
4. **Bilingual Support**: Full English and Urdu (اردو) support with RTL rendering
5. **Agent Handoffs**: Chronos delegates to PlanningAgent and QueryAgent for specialized tasks
6. **SSE Streaming**: Real-time token-by-token responses in the chat interface
7. **Auto-Tag Extraction**: Chronos automatically extracts tags (locations, categories, activities) from natural language

#### Agent Files

| File | Purpose |
|------|---------|
| `backend/app/ai/agents/todo_agent.py` | Main Chronos agent with personality |
| `backend/app/ai/agents/context.py` | Agent execution context management |
| `backend/app/ai/mcp/tools.py` | MCP tool implementations (7 tools) |
| `backend/app/ai/services/openai_client.py` | OpenAI API (chat, embeddings, Whisper) |
| `backend/app/ai/services/qdrant_client.py` | Vector database client |
| `backend/app/ai/services/runner_service.py` | Agent execution with streaming |
| `backend/app/ai/utils/language.py` | Urdu/English detection |
| `backend/routes/chat.py` | Chat API endpoints (SSE streaming) |

#### Frontend Chat Files

| File | Purpose |
|------|---------|
| `frontend/components/chat/chat-panel.tsx` | Main chat interface |
| `frontend/components/chat/chat-message.tsx` | Message display with RTL support |
| `frontend/components/chat/voice-recorder.tsx` | Whisper voice recording |
| `frontend/lib/api/chat.ts` | Chat API client with SSE parsing |
| `frontend/lib/utils/sse.ts` | Shared SSE streaming utilities |
| `frontend/lib/utils/text-direction.ts` | RTL/Urdu text detection |
| `frontend/lib/stores/chat-store.ts` | React Context for chat UI state |

### Phase IV: Kubernetes (Pending)

Helm chart structure (planned):
```
helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
```

### Phase V: Dapr Integration

Dapr sidecar patterns (planned):
- Pub/sub via Kafka
- State store for caching
- Service discovery for microservices

## Notification System Architecture

The notification system is a multi-channel, real-time notification platform built for Phase II:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Notification Dispatch                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   In-App     │  │    Push      │  │     Email       │  │
│  │   (SSE)      │  │  (Web Push)  │  │   (Resend)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    NotificationService                      │
│  - Deduplication (type-aware windows)                       │
│  - User preference filtering                                │
│  - Do Not Disturb checking                                  │
│  - Multi-channel dispatch                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Background Scheduler                      │
│  - Daily digest emails (8 AM user time)                     │
│  - Weekly summary emails (Monday 9 AM user time)            │
│  - Task due reminders (every 15 minutes)                    │
│  - Cleanup job (soft-deleted notifications)                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| `NotificationService` | `backend/app/services/notification_service.py` | CRUD, deduplication, dispatch |
| `SSEService` | `backend/app/services/sse_service.py` | Real-time streaming to frontend |
| `PushService` | `backend/app/services/push_service.py` | Web Push API with VAPID |
| `EmailService` | `backend/app/services/email_service.py` | Resend integration, templates |
| `SchedulerService` | `backend/app/services/scheduler_service.py` | Background digest jobs |
| `UnsubscribeService` | `backend/app/services/unsubscribe_service.py` | Token-based unsubscribe |

### Notification Types

```python
class NotificationType(str, Enum):
    TASK_DUE = "task_due"              # Task due soon
    TASK_OVERDUE = "task_overdue"      # Task is overdue
    TASK_COMPLETED = "task_completed"  # Task marked complete
    TASK_ASSIGNED = "task_assigned"    # Task assigned to user
    SYSTEM_UPDATE = "system_update"    # System notifications
    WELCOME = "welcome"                # Welcome email
```

### Deduplication Windows

To prevent spam, each notification type has a unique deduplication window:

| Type | Window | Rationale |
|------|--------|-----------|
| TASK_DUE | 5 minutes | Tasks can become due quickly |
| TASK_OVERDUE | 15 minutes | Less frequent, important |
| TASK_COMPLETED | 1 minute | Instant feedback |
| SYSTEM_UPDATE | 24 hours | Low priority |

### Rate Limiting

Push notifications are rate-limited to **3 per hour** per user:
- Urgent notifications (TASK_DUE, TASK_OVERDUE) are **exempt**
- Other notifications count against the limit
- Tracked in-memory with sliding window

### Digest Email Scheduling

Digest emails respect **user timezone** for accurate delivery:

```python
# Daily digest at 8 AM in user's timezone
def get_next_daily_digest_time(user_timezone: str) -> datetime:
    tz = ZoneInfo(user_timezone)
    now = datetime.now(tz)
    scheduled = datetime.combine(now.date(), time(8, 0), tzinfo=tz)
    if now >= scheduled:
        scheduled += timedelta(days=1)
    return scheduled.astimezone(ZoneInfo("UTC"))

# Weekly summary on Monday 9 AM in user's timezone
def get_next_weekly_summary_time(user_timezone: str) -> datetime:
    tz = ZoneInfo(user_timezone)
    target_weekday = 0  # Monday
    # Calculate next Monday at 9 AM...
```

### Webhook Signature Verification

Resend webhooks are verified using HMAC-SHA256:

```python
def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    # Parse: t={timestamp},v1={signature}
    # Check timestamp < 5 minutes (replay protection)
    # Verify HMAC with WEBHOOK_SECRET
    return hmac.compare_digest(expected_signature, signature_part)
```

### Frontend SSE Integration

The frontend uses EventSource to receive real-time notifications:

```typescript
// components/notifications/sse-stream-provider.tsx
const eventSource = new EventSource(
  `${API_URL}/api/notifications/stream`,
  { headers: { Authorization: `Bearer ${token}` } }
)

eventSource.addEventListener('notification', (event) => {
  const notification = JSON.parse(event.data)
  // Update UI in real-time
})
```

## Recent Changes
- **012-ai-chatbot-phase3** (Complete): ⭐ **Chronos AI Assistant** — Multi-agent system with OpenAI Agents SDK, semantic search (Qdrant), voice input (Whisper), bilingual English/Urdu support, SSE streaming
- 012-notification-system: Comprehensive multi-channel notification system with SSE, push, email
- 011-timezone-support: User timezone field for accurate digest scheduling

## Active Technologies
- **Python 3.13+** (STRICT per constitution §V.1.1) (012-ai-chatbot-phase3)
- **OpenAI Agents SDK** — Multi-agent orchestration
- **gpt-4o-mini** — Main chat model
- **Qdrant** — Vector database for semantic search
- **Whisper API** — Voice transcription

---

## ★ Insight ─────────────────────────────────────

**Chronos — A New Paradigm in AI-Powered Task Management:**

1. **Agentic Architecture**: Chronos isn't just a chatbot — it's a multi-agent system with specialized agents (PlanningAgent, QueryAgent) that coordinate through the OpenAI Agents SDK. This allows Chronos to delegate complex tasks to specialists while maintaining a coherent conversation.

2. **Semantic Understanding**: Unlike traditional keyword search, Chronos uses vector embeddings (text-embedding-3-small) stored in Qdrant to find tasks by *meaning*. When users search for "grocery items," Chronos finds tasks containing "buy milk," "eggs," "bread" — even without those exact words.

3. **Cultural & Language Sensitivity**: Chronos detects and responds in Urdu (اردو) with proper RTL rendering, including Roman Urdu support. The Whisper transcription includes Urdu biasing to prevent Devanagari output — a critical feature for Urdu speakers who often get Hindi script instead.

─────────────────────────────────────────────────────────
