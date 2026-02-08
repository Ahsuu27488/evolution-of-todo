# frontend/ — Chronos Todo Web App

**Claude Code Context** for the Next.js frontend (Phase II Chronos WebApp + Phase III AI Chatbot).

## Project Purpose

Next.js 15 App Router application serving as the web interface for the Chronos Todo application with:
- User authentication via Better Auth
- Task management UI with filtering, sorting, search
- Real-time state synchronization with backend
- **AI Chatbot with natural language task management** (Phase III)
- Dark mode and responsive design

---

## ★ Insight ─────────────────────────────────────

**Key Architectural Evolution (Phase II → Phase III):**

1. **Shared Auth Token Pattern**: Phase III introduced `lib/auth/token.ts` - a centralized `getAuthToken()` utility. This eliminates code duplication across API clients (`api-client.ts`, `api/chat.ts`, `use-chat.ts`).

2. **SSE Streaming Utilities**: Phase III added `lib/utils/sse.ts` with `parseSSEStream()` - a reusable async generator for parsing Server-Sent Events. This is used by both notification streaming and chat streaming.

3. **React Context over Zustand for Chat**: The chat UI state uses React Context (`lib/stores/chat-store.ts`) instead of Zustand. This prevents infinite re-render loops that occur with Zustand object selectors in SSR/hydration scenarios.

─────────────────────────────────────────────────────────

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

## Debugging Workflow

**IMPORTANT**: Always use the `superpowers:systematic-debugging` skill when encountering bugs, errors, or unexpected behavior in the frontend.

### When to Use Systematic Debugging

Invoke this skill before attempting to fix:
- Component rendering errors
- State synchronization issues
- API call failures
- Authentication/JWT token problems
- SSE streaming issues (notifications, chat)
- Hydration errors
- Styling/layout problems

### Debugging Frontend Issues

The systematic debugging skill will help you:

1. **Gather Context**: Check browser console, Network tab, React DevTools
2. **Check State**: Verify TanStack Query cache, Zustand stores, React Context
3. **Form Hypotheses**: Based on error messages and behavior patterns
4. **Test Isolated**: Reproduce issues in minimal reproduction
5. **Implement Fix**: Make targeted changes based on evidence

**Frontend-Specific Debugging Tips**:
- Use React DevTools to inspect component state and props
- Check Network tab for API request/response details
- Verify JWT token in Application > Cookies
- For SSE issues, check EventSource connection in Network tab
- Use `console.log` with structured logging for state changes
- Check browser console for hydration warnings
- Verify `getAuthToken()` is returning valid tokens

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js App Router                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Page Routes │  │  API Routes  │  │ Server Actions   │  │
│  │  - /, /login │  │  - /api/auth │  │  - CRUD tasks    │  │
│  │  - /dashboard│  │  - /api/token│  │  - auth actions  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Component Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Notification│  │  Task Components│  │ Chat Components  ││
│  │  - Bell      │  │  - task-card │  │  - chat-panel    │  │
│  │  - Dropdown  │  │  - task-list │  │  - voice-recorder│  │
│  │  - SSE       │  │  - forms     │  │  - chat-input    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      State Management                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TanStack Query (Server State)                      │  │
│  │  - Tasks, notifications, conversations              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Context/Zustand (Client State)               │  │
│  │  - Filters, modals, toasts, chat UI state          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────┐         ┌──────────────────────────┐ │ │
│  │   API Client     │────────▶│   FastAPI Backend        │ │ │
│  │  (lib/api-client)│         │   (JWT auth)             │  │
│  └──────────────────┘         └──────────────────────────┘ │ │
│  ┌──────────────────┐         ┌──────────────────────────┐ │ │
│  │   Chat API       │────────▶│   OpenAI Agents Backend │  │ │
│  │  (lib/api/chat) │         │   (MCP tools)            │  │ │
│  └──────────────────┘         └──────────────────────────┘ │ │
│  ┌──────────────────┐         ┌──────────────────────────┐ │ │
│  │   Better Auth    │────────▶│   Neon PostgreSQL        │ │ │
│  │  (lib/auth.ts)   │         │   (user sessions)        │  │
│  └──────────────────┘         └──────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

---

## Key File Locations

### Phase II (Core Features)

| File | Purpose | Key Details |
|------|---------|-------------|
| `app/layout.tsx` | Root layout | Font config (Geist, Noto Nastaliq Urdu), Providers wrapper |
| `app/providers.tsx` | App providers | TanStack Query, ThemeProvider, Toaster, ChatProvider |
| `lib/auth.ts` | Better Auth config | JWT plugin, Neon DB connection |
| `lib/api-client.ts` | Backend client | JWT token fetching, retry logic, error handling |
| `lib/auth-client.ts` | Client auth helpers | Sign in/up with backend integration |
| `lib/stores/ui-store.ts` | Zustand store | Filters, modals, toasts, command state |
| `lib/errors.ts` | Error utilities | ApiError class, error codes, Result type |
| `app/actions/tasks.ts` | Task server actions | CRUD operations with JWT from cookies |
| `app/actions/auth.ts` | Auth server actions | Sign in/up/sign out |
| `app/actions/notifications.ts` | Notification actions | Mark read, delete, preferences |
| `app/api/auth/token/route.ts` | Token endpoint | Returns JWT from session cookie |
| `middleware.ts` | Auth middleware | Protects routes, redirects |
| `types/task.ts` | TypeScript interfaces | Task, TaskCreate, TaskUpdate |
| `types/notification.ts` | Notification types | Notification, NotificationType, Preferences |
| `hooks/use-notifications.ts` | Notification hooks | Queries, mutations, unread count |
| `components/notifications/notification-bell.tsx` | Bell icon | Unread badge, Dropdown trigger |
| `components/notifications/notification-dropdown.tsx` | Dropdown | Notification list, filters, actions |
| `components/notifications/sse-stream-provider.tsx` | SSE client | EventSource connection, cache updates |
| `components/notifications/email-preferences.tsx` | Email settings | Per-channel toggles, test email |
| `components/notifications/push-settings.tsx` | Push settings | Subscribe/unsubscribe, test |
| `components/notifications/push-permission-modal.tsx` | Permission modal | User-friendly permission request |

### Phase III (AI Chatbot)

| File | Purpose | Key Details |
|------|---------|-------------|
| `lib/config/api.ts` | API configuration | Centralized `API_URL` constant |
| `lib/auth/token.ts` | Auth token utilities | Shared `getAuthToken()` function |
| `lib/utils/sse.ts` | SSE parsing utilities | `parseSSEStream()`, event handlers |
| `lib/utils/text-direction.ts` | Text direction utilities | `isUrduText()`, `getTextDirection()` for RTL support |
| `lib/api/chat.ts` | Chat API client | SSE streaming, conversations, transcription |
| `hooks/use-chat.ts` | Chat hooks | `useConversations()`, `useSendMessage()` |
| `lib/stores/chat-store.ts` | Chat UI state | React Context for chat panel, messages, streaming |
| `types/chat.ts` | Chat types | Message, Conversation, SSE events |
| `components/chat/chat-panel.tsx` | Chat interface | Floating panel, conversation list |
| `components/chat/chat-input.tsx` | Message input | Auto-expanding textarea, voice button |
| `components/chat/chat-message.tsx` | Message display | User/assistant styling, RTL support |
| `components/chat/voice-recorder.tsx` | Voice recording | MediaRecorder API, Whisper transcription |
| `components/chat/task-card.tsx` | Task cards in chat | Inline task display for AI-created tasks |

---

## Architecture Patterns

### Better Auth + JWT Flow

```
1. User signs in → Better Auth creates session + JWT
2. JWT stored in session (accessible server-side)
3. API Client fetches JWT via /api/auth/token
4. JWT sent to FastAPI in Authorization header
5. FastAPI verifies with shared BETTER_AUTH_SECRET
```

**Implementation** (Phase III refactored):

```typescript
// lib/auth/token.ts - Shared auth token utility
import { getAuthToken } from "@/lib/auth/token";

// Used in all API clients
const token = await getAuthToken();
```

### SSE Integration Pattern

Real-time notifications use Server-Sent Events:

```typescript
// components/notifications/sse-stream-provider.tsx
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

**Important**: SSE provider must be imported with `{ ssr: false }`:

```typescript
const SSEStreamProvider = dynamic(
  () => import("@/components/notifications/sse-stream-provider"),
  { ssr: false }
)
```

### Chat SSE Streaming (Phase III)

Chat responses use SSE streaming with the new shared utilities:

```typescript
// lib/api/chat.ts
import { parseSSEStream } from "@/lib/utils/sse";

// Parse SSE stream from chat API
for await (const { eventType, data } of parseSSEStream(reader, handlers)) {
  // Events handled by handlers: onToken, onToolCall, onAgentHandoff, etc.
}
```

### Shared Utilities (Phase III)

**Location**: `frontend/lib/utils/` and `frontend/lib/config/`

| Utility | Purpose | Export |
|---------|---------|--------|
| `lib/config/api.ts` | API URL config | `API_URL` |
| `lib/auth/token.ts` | JWT token fetching | `getAuthToken()` |
| `lib/utils/sse.ts` | SSE stream parsing | `parseSSEStream()`, `SSEEventHandlers` |
| `lib/utils/text-direction.ts` | RTL support | `isUrduText()`, `getTextDirection()` |

**Usage example**:

```typescript
// Import shared utilities
import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";
import { getTextDirection } from "@/lib/utils/text-direction";
import { parseSSEStream } from "@/lib/utils/sse";

// Use in components
const direction = getTextDirection(text);
const token = await getAuthToken();
```

### Server Actions Pattern

Server Actions read JWT from cookies and call backend:

```typescript
// app/actions/notifications.ts
export async function markAsRead(
  notificationId: number
): Promise<ActionResult<void>> {
  const authData = await getAuthData()  // Reads JWT from cookie
  if (!authData) return { success: false, error: {...} }

  return apiCall(`/api/notifications/${notificationId}/read`, authData, {
    method: "PUT",
  })
}
```

### API Client Pattern

The API Client auto-fetches JWT for every request:

```typescript
class ApiClient {
  private async getAuthToken(): Promise<string | null> {
    const response = await fetch(`${this.appUrl}/api/auth/token`, {
      credentials: "include",  // Send session cookie
    })
    return data.token
  }

  async request<T>(endpoint: string) {
    const token = await this.getAuthToken()
    // ... fetch with Authorization header
  }
}
```

---

## Coding Conventions

### Type-Safe API Calls

All API calls use `Result<T>` pattern:

```typescript
// lib/errors.ts (or types/chat.ts for chat-specific)
export type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

// Usage
const result = await api.getNotifications()
if (result.success) {
  const notifications = result.data
} else {
  handleError(result.error)
}
```

### Shared Utility Pattern (Phase III)

**Always use shared utilities instead of duplicating code:**

```typescript
// ✅ Good - Use shared utility
import { getAuthToken } from "@/lib/auth/token";

// ❌ Bad - Duplicate implementation
async function getAuthToken() { /* ... */ }
```

### Component Patterns

- Server Components by default (no "use client")
- Client Components only when needed (interactivity)
- `"use client"` directive at top of client files

### File Naming

- Pages: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`
- Server Actions: `*.ts` in `app/actions/`
- API Routes: `route.ts` in `app/api/`
- Components: `*.tsx` with kebab-case filenames
- Hooks: `use-*.ts` in `hooks/`
- Utilities: `*.ts` in `lib/utils/`
- Config: `*.ts` in `lib/config/`

---

## Notification System Architecture

### Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `NotificationBell` | Bell icon with badge | Animated unread count, Framer Motion |
| `NotificationDropdown` | Notification list | Filter tabs, mark read, delete |
| `SSEStreamProvider` | Real-time updates | Auto-reconnect, cache updates |
| `PushPermissionModal` | Permission request | User-friendly request flow |
| `PushSettings` | Push management | Subscribe/unsubscribe, test |
| `EmailPreferences` | Email settings | Per-channel toggles, test email |

### Notification Types

```typescript
enum NotificationType {
  TASK_DUE = "task_due"           // Task due soon
  TASK_OVERDUE = "task_overdue"   // Task is overdue
  TASK_COMPLETED = "task_completed" // Task marked complete
  TASK_ASSIGNED = "task_assigned" // Task assigned to user
  SYSTEM_UPDATE = "system_update" // System notifications
}
```

### SSE Events

| Event | Data | Action |
|-------|------|--------|
| `notification` | Notification object | Add to list, increment unread |
| `notification_read` | `{ id: number }` | Mark as read, decrement unread |
| `ping` | `{ timestamp: string }` | Keep connection alive |

---

## Chat System Architecture (Phase III)

### Chat Flow

```
User Input → ChatPanel → ChatInput/VoiceRecorder
    │
    ▼
Chat API (SSE Stream) → FastAPI Backend
    │
    ▼
OpenAI Agents SDK → MCP Tools → Task CRUD
    │
    ▼
SSE Events → Real-time UI Updates
```

### Chat SSE Events

| Event | Data | Action |
|-------|------|--------|
| `message_start` | `{ conversationId, correlationId }` | Initialize streaming |
| `token` | `{ content }` | Append to message |
| `tool_call` | `{ tool, arguments }` | Show tool indicator |
| `tool_result` | `{ tool, output }` | Show tool result |
| `agent_handoff` | `{ from_agent, to_agent }` | Show handoff notification |
| `message_done` | `{ final_output, agent }` | Finalize message |
| `error` | `{ message }` | Show error |

### Chat State Management

Uses React Context (not Zustand) for chat UI state to avoid SSR/hydration issues:

```typescript
// lib/stores/chat-store.ts
export function useChatStore() {
  const context = useContext(ChatContext)
  if (!context) throw new Error("useChatStore must be used within ChatProvider")
  return context
}
```

### Voice Input (Phase III)

```typescript
// components/chat/voice-recorder.tsx
- MediaRecorder API for audio capture
- 30-second recording limit
- Whisper API transcription via /api/chat/transcribe
- Ambiguity confirmation for unclear transcriptions
```

### Urdu Language Support

```typescript
// lib/utils/text-direction.ts
- isUrduText(): Unicode range detection
- getTextDirection(): Returns "rtl" or "ltr"
- Applied to chat messages and input placeholders
```

---

## Auth Configuration

### Better Auth JWT Settings

```typescript
// lib/auth.ts
jwt({
  jwt: {
    expirationTime: "7d",
    issuer: APP_URL,
    audience: [API_URL],
  },
})
```

### Shared Secret

`BETTER_AUTH_SECRET` MUST match between:
1. Frontend (Better Auth signing)
2. Backend (FastAPI verification)

---

## State Management Split

| State Type | Library | Examples |
|------------|---------|----------|
| **Server State** | TanStack Query | Tasks, notifications, conversations, mutations |
| **Client State** | React Context/Zustand | Filter selections, modal open/close, chat UI |

### When to Use Which

- Use TanStack Query for data from API
- Use React Context for interactive component state (chat, modals)
- Use Zustand for persistent client-side preferences (filters)
- Never persist server state in client stores

---

### Dual State Management Pattern (Phase 013 - AI Chat UI Redesign)

**Overview**: Phase 013 introduced a dual state management architecture that combines React Context for chat UI state with Zustand for task mutation events. This pattern enables real-time task synchronization between AI actions and the dashboard.

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     SSE Stream (Backend)                         │
│  - tool_call events (AI invoked action)                          │
│  - tool_result events (Action completed)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend SSE Parser (lib/api/chat.ts)              │
│  - Parse tool_result events                                      │
│  - Extract task mutation data                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Chat Store (React Context) + Task Events (Zustand)       │
│  - triggerTaskUpdate() action                                    │
│  - setTaskMutation() action                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              TanStack Query Cache Update                         │
│  - queryClient.setQueryData(['tasks', id], updatedTask)         │
│  - queryClient.invalidateQueries(['tasks']) // Background       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Components                          │
│  - Task lists auto-re-render with updated data                   │
│  - Celebration animation plays on task completion                │
└─────────────────────────────────────────────────────────────────┘
```

**State Store Responsibilities**:

| Store | Type | Responsibility | Location |
|-------|------|----------------|----------|
| `ChatUIState` | React Context | Chat panel open/close, messages, streaming, language | `lib/stores/chat-store.ts` |
| `TaskEventStore` | Zustand | Task mutation events from AI (create, complete, update, delete) | `lib/stores/task-events.ts` |

**Why React Context for Chat UI?**
- Prevents infinite re-render loops with Zustand object selectors in SSR/hydration
- Chat UI state is transient (doesn't need persistence)
- Context naturally follows component tree structure

**Why Zustand for Task Events?**
- Task mutations affect dashboard (outside chat component tree)
- Zustand persists state across component unmounts
- Enables cross-component communication without prop drilling

**Key Interfaces**:

```typescript
// lib/stores/task-events.ts (Zustand)
interface TaskMutation {
  type: 'create' | 'complete' | 'update' | 'delete'
  taskId: number | null
  timestamp: number
  data?: Partial<Task>
  success?: boolean
  error?: string
}

interface TaskEventStore {
  lastMutation: TaskMutation | null
  setTaskMutation: (mutation: TaskMutation) => void
  clearMutation: () => void
}

// lib/stores/chat-store.ts (React Context)
interface ChatUIState {
  // UI State
  isOpen: boolean
  isMinimized: boolean
  messages: Message[]
  isStreaming: boolean
  streamedContent: string
  currentConversationId: string | null
  languagePreference: "auto" | "en" | "ur"

  // Actions
  toggleOpen: () => void
  toggleMinimized: () => void
  addMessage: (message: Message) => void
  clearMessages: () => void
  sendMessage: (content: string, isVoice?: boolean) => Promise<void>
  startStreaming: () => void
  resetStreamState: () => void
  appendStreamedContent: (content: string) => void
  setConversationId: (id: string | null) => void

  // Cache Update Action (Phase 013)
  triggerTaskUpdate: (taskId: number, mutation: TaskMutation) => void
}
```

**Usage Example**:

```typescript
// In chat-panel.tsx - When AI completes a task via tool_result
import { useChatStore } from '@/lib/stores/chat-store'
import { useTaskEventStore } from '@/lib/stores/task-events'

const { triggerTaskUpdate } = useChatStore()
const setTaskMutation = useTaskEventStore(s => s.setTaskMutation)

// Parse SSE tool_result event
if (tool === 'complete_task' && output.success) {
  const taskId = output.data.id

  // Update both stores
  triggerTaskUpdate(taskId, {
    type: 'complete',
    taskId,
    timestamp: Date.now(),
    data: { completed: true }
  })

  setTaskMutation({
    type: 'complete',
    taskId,
    timestamp: Date.now(),
    data: { completed: true },
    success: true
  })
}
```

**Best Practices**:

1. **TanStack Query for Server State**: Always use TanStack Query for API data - never duplicate in Zustand/Context
2. **React Context for Component State**: Use for UI state that's local to a component subtree
3. **Zustand for Cross-Component Events**: Use when state needs to be accessed across unrelated components
4. **Cache Updates via queryClient**: Always update TanStack Query cache immediately for optimistic UI
5. **Background Refetch**: After optimistic updates, invalidate queries for background sync

---

## Styling Conventions

### Tailwind v4

Uses `@theme` directive instead of v3 config:

```css
@theme {
  --color-primary-50: oklch(0.95 0.01 264);
  --color-primary: oklch(var(--primary));
}
```

### Color System (Deep Space Theme)

- Uses OKLCH for better color manipulation
- CSS variables for theme values
- Dark mode via `dark:` prefix
- Primary: `oklch(0.91 0.17 195)` (Neon cyan)
- Secondary: `oklch(0.65 0.26 293)` (Neon purple)

### Component Variants

Uses `class-variance-authority`:

```typescript
const buttonVariants = cva(
  "base-classes",
  {
    variants: {
      variant: {
        default: "default-classes",
        destructive: "destructive-classes",
      },
    },
  }
)
```

---

## Error Handling

### Error Hierarchy

```typescript
ApiError
├── ErrorCode (enum)
├── getUserMessage()  // User-friendly message
├── statusCode       // HTTP status
├── endpoint         // Where it occurred
├── requestId        // For debugging
```

### Toast Notifications

Use `sonner` for user feedback:

```typescript
import { toast } from "sonner"

toast.success("Task created")
toast.error("Failed to create task")
```

---

## Important Constraints

- **All API calls must use shared utilities** — Use `getAuthToken()` from `@/lib/auth/token`
- **Server Actions require "use server"** — First line of file
- **JWT never stored in localStorage** — Always fetched from session
- **Filters persist in localStorage** — Via Zustand persist
- **TanStack Query for server state** — Never duplicate in client stores
- **SSE provider must use { ssr: false }** — EventSource is browser-only
- **Push notifications require user permission** — Show permission modal first
- **Use shared utilities for common operations** — Don't duplicate `getAuthToken()`, SSE parsing, or text detection
