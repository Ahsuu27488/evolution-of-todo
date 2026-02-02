# Phase III: AI Chatbot — Complete Project Context

**Claude Code Context** for implementing the AI Chatbot feature (Phase III).

## Planning Documents Structure

This spec uses two complementary planning documents:

| Document | Purpose | Structure |
|----------|---------|-----------|
| **plan.md** | Architectural planning | 4 Milestones (Backend Core → Backend Logic → Frontend → Testing) |
| **tasks.md** | Implementation tracking | 11 Phases by User Story (feature-focused) |

**How to use them:**
- Read `plan.md` to understand the **architecture** and **why** we build it this way
- Follow `tasks.md` to track **what** to implement and **when** each feature is done

**Milestone → Phase Mapping:**
```
plan.md Milestone 1 (Backend Core & Observability) → tasks.md Phase 1-2 (Setup + Foundational)
plan.md Milestone 2 (Backend Logic & Testing)       → tasks.md Phase 3 (US1 core backend)
plan.md Milestone 3 (Frontend Implementation)       → tasks.md Phase 3 (US1 frontend)
plan.md Milestone 4 (Frontend Testing & Polish)     → tasks.md Phase 11 (Polish)
```

**Observability First**: Both documents emphasize that structured logging (correlation IDs, structlog) must be implemented **before** any AI/ML logic. See `plan.md` Milestone 1.1 and `tasks.md` T020-T021.

## Architecture Overview

### Current Phase II Foundation

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js 15 App Router + Better Auth                    │  │
│  │  - Server Components by default                          │  │
│  │  - TanStack Query for server state                       │  │
│  │  - Zustand for client UI state                           │  │
│  │  - shadcn/ui components                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SSE + JWT (Bearer)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI + Async SQLAlchemy (Neon PostgreSQL)            │  │
│  │  - JWT auth (shared secret with Better Auth)             │  │
│  │  - SSE streaming for real-time updates                   │  │
│  │  - Background scheduler (digest emails, reminders)       │  │
│  │  - Multi-channel notification system                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase III Additions

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase III Components                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ Chat UI      │  │  OpenAI      │  │   MCP Server      │     │
│  │ (FAB button) │  │  Agents SDK  │  │   (task tools)    │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │  Qdrant      │  │   Whisper    │  │   New Tables     │     │
│  │ Vector DB    │  │ Transcription│  │ conversations    │     │
│  │              │  │              │  │ messages         │     │
│  │              │  │              │  │ agent_handoffs   │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Design System

### Colors (OKLCH - Deep Space Theme)

```css
/* Dark Mode (Primary) */
--custom-background: oklch(0.08 0.01 270);     /* Deep space black */
--custom-foreground: oklch(0.95 0.01 270);     /* Near white */
--custom-primary: oklch(0.91 0.17 195);        /* Neon cyan #00f5ff */
--custom-secondary: oklch(0.65 0.26 293);      /* Neon purple #a855f7 */
--custom-muted: oklch(0.25 0.01 270);          /* Dark gray */
--custom-accent: oklch(0.70 0.20 330);         /* Pink accent */

/* Light Mode */
--custom-background: oklch(0.98 0.01 270);     /* Off white */
--custom-foreground: oklch(0.15 0.01 270);     /* Near black */
```

### Typography

- **Font**: Inter (via next/font)
- **Sizes**: `text-xs` (12px), `text-sm` (14px), `text-base` (16px), `text-lg` (18px), `text-xl` (20px)
- **Weights**: `font-normal` (400), `font-medium` (500), `font-semibold` (600), `font-bold` (700)

### UI Patterns

| Pattern | Implementation | Usage |
|---------|----------------|-------|
| **Glassmorphism** | `bg-white/10 backdrop-blur-md border border-white/20` | Cards, modals, floating elements |
| **Glow effects** | `shadow-[0_0_20px_rgba(0,245,255,0.3)]` | Primary buttons, active states |
| **Gradients** | `bg-gradient-to-r from-cyan-500 to-purple-500` | Accents, headers |
| **Transitions** | `transition-all duration-200` | Hover states, animations |

### Component Library: shadcn/ui

Base components available:
- Button, Input, Textarea, Select
- Dialog, Dropdown Menu, Popover, Toast (sonner)
- Card, Badge, Avatar, Separator
- Tabs, Scroll Area

## Key Patterns

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

### 2. API Client Pattern

```typescript
// frontend/lib/api-client.ts
class ApiClient {
  private async getAuthToken(): Promise<string | null> {
    const response = await fetch(`${this.appUrl}/api/auth/token`, {
      credentials: "include",  // Send session cookie
    })
    const data = await response.json()
    return data.token
  }

  async request<T>(endpoint: string, options?: RequestInit) {
    const token = await this.getAuthToken()
    const response = await fetch(`${this.apiUrl}${endpoint}`, {
      ...options,
      headers: {
        ...options?.headers,
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    })
    // Error handling with Result type...
  }
}
```

### 3. State Management Split

| State Type | Library | Examples | Persistence |
|------------|---------|----------|-------------|
| **Server State** | TanStack Query | Tasks, notifications, chat messages | API + cache |
| **Client State** | Zustand | Filter selections, modal open/close | localStorage |

**Rule**: Never duplicate server state in Zustand.

### 4. SSE Streaming Pattern

```typescript
// Frontend SSE client
const eventSource = new EventSource("/api/notifications/stream")

eventSource.addEventListener("notification", (event) => {
  const notification = JSON.parse(event.data)

  // Update TanStack Query cache instantly
  queryClient.setQueryData(notificationKeys.list(), (old) => ({
    ...old,
    items: [notification, ...old.items],
    unread_count: old.unread_count + 1,
  }))
})
```

**Backend SSE broadcast**:
```python
# backend/app/services/sse_service.py
await SSEService.broadcast_to_user(user_id, {
    "event": "message_created",
    "data": message.model_dump()
})
```

### 5. Error Handling

```typescript
// Result type pattern
export type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

// Usage
const result = await api.createTask(data)
if (result.success) {
  const task = result.data
} else {
  toast.error(result.error.message)
}
```

### 6. Server Actions Pattern

```typescript
// app/actions/tasks.ts
"use server"  // Required directive

export async function createTask(
  data: TaskCreate
): Promise<ActionResult<Task>> {
  const authData = await getAuthData()  // Reads JWT from cookie
  if (!authData) return { success: false, error: {...} }

  return apiCall("/api/tasks", authData, {
    method: "POST",
    body: JSON.stringify(data),
  })
}
```

## Database Schema (Current + New)

### Existing Tables (Phase II)

```sql
-- Tasks with AI-ready fields pre-provisioned
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
  completed BOOLEAN DEFAULT FALSE,
  tags JSONB DEFAULT '[]',
  due_date TIMESTAMP WITH TIME ZONE,
  recurrence_pattern TEXT CHECK (recurrence_pattern IN ('DAILY', 'WEEKLY', 'MONTHLY')),
  -- Phase III fields (ready to use)
  transcription_text TEXT,
  ai_summary TEXT,
  embedding_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications
CREATE TABLE notifications (
  id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT,
  data JSONB,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### New Tables (Phase III)

```sql
-- Chat conversations
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id TEXT NOT NULL,
  title TEXT DEFAULT 'New Conversation',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat messages
CREATE TABLE messages (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  conversation_id INTEGER NOT NULL,
  role TEXT CHECK (role IN ('user', 'assistant', 'system')) NOT NULL,
  content TEXT NOT NULL,
  tool_calls JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Agent handoff tracking
CREATE TABLE agent_handoffs (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  conversation_id INTEGER NOT NULL,
  from_agent TEXT NOT NULL,
  to_agent TEXT NOT NULL,
  reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
```

## Backend Patterns

### Dependency Injection for Auth

```python
# All protected endpoints use this pattern
@router.get("/api/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),  # ← Injects user_id from JWT
    session: AsyncSession = Depends(get_session),  # ← Injects DB session
) -> TaskList:
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return TaskList(tasks=result.scalars().all())
```

### Async Database Sessions

```python
# db.py
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Usage in endpoint
@router.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    task = Task(**task_data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Ownership Verification (404 not 403)

```python
async def get_task_or_404(task_id: int, user_id: str, session: AsyncSession) -> Task:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await session.execute(statement)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404)  # Not 403 — prevents enumeration
    return task
```

## Frontend Patterns

### Server vs Client Components

```typescript
// Server Component (default) - no "use client"
export default async function DashboardPage() {
  const tasks = await getTasks()  // Direct DB call via Server Action
  return <TaskList tasks={tasks} />
}

// Client Component - interactive
"use client"
export function TaskCard({ task }: { task: Task }) {
  const [isOpen, setIsOpen] = useState(false)
  return <div onClick={() => setIsOpen(!isOpen)}>...</div>
}
```

### TanStack Query Hooks

```typescript
// hooks/use-tasks.ts
export function useTasks(options?: { filter?: string }) {
  return useQuery({
    queryKey: taskKeys.list(options),
    queryFn: () => fetchTasks(options),
    staleTime: 1000 * 30, // 30 seconds
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: TaskCreate) => createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
      toast.success("Task created")
    },
  })
}
```

### Dynamic Import for Browser-Only Code

```typescript
// SSE provider must use { ssr: false }
const SSEStreamProvider = dynamic(
  () => import("@/components/notifications/sse-stream-provider"),
  { ssr: false }
)
```

## Phase 3 Implementation Plan

**See `tasks.md` for the complete task breakdown by user story.**

### Quick Reference

| What | Where |
|------|-------|
| **Task Checklist** | `tasks.md` - 130 tasks across 11 phases |
| **Architecture** | `plan.md` - 4 milestones with technical details |
| **Data Models** | `data-model.md` - Complete entity definitions |
| **API Contracts** | `contracts/chat-api.yaml` - OpenAPI specification |
| **Getting Started** | `quickstart.md` - Setup instructions |

### User Story Priorities

| Priority | User Story | Tasks | Bonus |
|----------|------------|-------|-------|
| **P1** 🎯 MVP | Natural Language Task Management | T026-T049 | - |
| P2 | Conversational Context Memory | T050-T056 | - |
| P3 | Semantic Task Search | T057-T067 | - |
| P4 | Urdu Language Support | T068-T079 | +100 |
| P5 | Voice Command Input | T080-T092 | +200 |
| P6 | AI Task Summarization | T093-T099 | - |
| P7 | MCP Tool Integration | T100-T105 | - |
| P8 | Agent Handoffs | T106-T113 | +200 |

### MVP Path (Fastest to Working Chatbot)

```
Phase 1: Setup (T001-T007)        → Environment ready
    ↓
Phase 2: Foundational (T008-T025) → Database, clients, middleware
    ↓
Phase 3: US1 Only (T026-T049)     → Working chatbot!
    ↓
STOP → Test and Demo
```

### Incremental Delivery (Recommended)

```
MVP → US3 (Search) → US4 (Urdu +100) → US5 (Voice +200) → US8 (Handoffs +200)
Total Bonus Potential: +500 points
```

### Environment Variables

```bash
# Required for Phase III
OPENAI_API_KEY=sk-proj-...               # OpenAI API key (Agents + Whisper + embeddings)
QDRANT_URL=https://...                   # Qdrant Cloud URL (get from https://cloud.qdrant.io)
QDRANT_API_KEY=eyJ...                    # Qdrant Cloud API key

# Existing (must match frontend/backend)
BETTER_AUTH_SECRET=...                   # ≥32 chars, shared secret
DATABASE_URL=postgresql://...            # Neon connection string
FRONTEND_URL=http://localhost:3000
```

## Important Constraints

### Security

- **404 not 403** for ownership checks — Prevents enumeration
- **JWT in httpOnly cookies** — Never localStorage
- **CORS strict** — Only allow frontend origin
- **Rate limiting** — Chat endpoints need rate limiting

### Performance

- **Connection pooling** — Reuse database connections
- **Streaming responses** — Use SSE for chat, not polling
- **Vector search** — Cache embeddings when possible
- **Pagination** — Limit conversation history

### Phase Isolation

- **Do not modify** Phase I (src/) or Phase II core features
- **Additive only** — New tables, new routes, new components
- **Backward compatible** — Existing features must work unchanged

## Extension Points

### Task AI Fields (Pre-provisioned)

```typescript
// Already in Task model - ready to use
export interface Task {
  transcription_text: string | null  // ← Store voice transcription
  ai_summary: string | null          // ← Store LLM-generated summary
  embedding_id: string | null        // ← Store vector ID for search
}
```

### Agent Tool Examples

```python
# MCP tools the agent can call
@mcp_tool
async def create_task(title: str, description: str, user_id: str) -> Task:
    """Create a new task"""
    ...

@mcp_tool
async def search_tasks(query: str, user_id: str) -> list[Task]:
    """Search tasks semantically"""
    embedding = await embed_query(query)
    results = await qdrant.search(embedding, filter={"user_id": user_id})
    ...

@mcp_tool
async def get_upcoming_tasks(user_id: str) -> list[Task]:
    """Get tasks due in the next 7 days"""
    ...
```

## File Structure

```
backend/app/
├── models.py                 # ← Add Conversation, Message, AgentHandoff
├── routes/
│   ├── chat.py              # ← NEW: Chat endpoints
│   ├── tasks.py             # Existing (keep unchanged)
│   └── auth.py              # Existing (keep unchanged)
├── services/
│   ├── agent_service.py     # ← NEW: OpenAI Agents SDK
│   ├── mcp_server.py        # ← NEW: MCP tools
│   ├── vector_service.py    # ← NEW: Qdrant integration
│   ├── transcription_service.py  # ← NEW: Whisper
│   └── sse_service.py       # Existing (reuse for chat streaming)
└── db.py                     # ← Update for new models

frontend/
├── app/
│   ├── layout.tsx           # ← Add Chat FAB + Provider
│   └── actions/
│       └── chat.ts          # ← NEW: Chat server actions
├── components/
│   └── chat/                # ← NEW: Chat UI components
│       ├── chat-fab.tsx
│       ├── chat-panel.tsx
│       ├── chat-message.tsx
│       ├── chat-input.tsx
│       └── voice-recorder.tsx
├── hooks/
│   ├── use-chat.ts          # ← NEW: Chat state
│   ├── use-conversations.ts # ← NEW: Conversations
│   └── use-voice-input.ts   # ← NEW: Voice recording
├── lib/
│   ├── api-client.ts        # ← Add chat methods
│   └── stores/
│       └── ui-store.ts      # ← Add chat UI state
└── types/
    └── chat.ts              # ← NEW: Chat interfaces
```
