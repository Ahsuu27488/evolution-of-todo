# frontend/ — Chronos Todo Web App

**Claude Code Context** for the Next.js frontend (Phase II Chronos WebApp).

## Project Purpose

Next.js 15 App Router application serving as the web interface for the Chronos Todo application with:
- User authentication via Better Auth
- Task management UI with filtering, sorting, search
- Real-time state synchronization with backend
- Comprehensive notification system (SSE, push, email)
- Dark mode and responsive design

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
│  │  Notification│  │  Task Components│  │ Layout Components││
│  │  - Bell      │  │  - task-card │  │  - header        │  │
│  │  - Dropdown  │  │  - task-list │  │  - user-nav      │  │
│  │  - SSE       │  │  - forms     │  │  - theme-toggle  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      State Management                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TanStack Query (Server State)                      │  │
│  │  - Tasks, notifications, user session               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Zustand (Client State)                              │  │
│  │  - Filters, modals, toasts                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │   API Client     │────────▶│   FastAPI Backend        │ │
│  │  (lib/api-client)│         │   (JWT auth)             │ │
│  └──────────────────┘         └──────────────────────────┘ │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │   SSE Stream     │────────▶│   SSE Endpoint           │ │
│  │  (notifications) │         │   (/api/notifications/stream)│
│  └──────────────────┘         └──────────────────────────┘ │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │   Better Auth    │────────▶│   Neon PostgreSQL        │ │
│  │  (lib/auth.ts)   │         │   (user sessions)        │ │
│  └──────────────────┘         └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key File Locations

| File | Purpose | Key Details |
|------|---------|-------------|
| `app/layout.tsx` | Root layout | Font config, Providers wrapper, ViewTransitions |
| `app/providers.tsx` | App providers | TanStack Query, ThemeProvider, Toaster |
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

## Architecture Patterns

### Better Auth + JWT Flow

```
1. User signs in → Better Auth creates session + JWT
2. JWT stored in session (accessible server-side)
3. API Client fetches JWT via /api/auth/token
4. JWT sent to FastAPI in Authorization header
5. FastAPI verifies with shared BETTER_AUTH_SECRET
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

## Coding Conventions

### Type-Safe API Calls

All API calls use `Result<T>` pattern:

```typescript
// lib/errors.ts
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

### Notification Hooks

Custom hooks using TanStack Query:

```typescript
// hooks/use-notifications.ts
export function useNotifications(options?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: notificationKeys.list(options),
    queryFn: () => fetchNotifications(options),
    staleTime: 1000 * 30, // 30 seconds
  })
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: fetchUnreadCount,
    refetchInterval: 1000 * 60, // Every minute
  })
}
```

### Server Actions Signatures

```typescript
"use server"  // Required directive

export async function actionName(
  data: InputType
): Promise<ActionResult<OutputType>> {
  // ...
  return { success: true, data: ... }
}
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

### Push Notification Flow

```
1. User clicks bell → PushPermissionModal shown
2. User accepts → Notification.requestPermission()
3. Subscription created → POST /api/notifications/push/subscribe
4. Push received → Service worker displays notification
5. User clicks → Navigate to relevant task
```

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

## State Management Split

| State Type | Library | Examples |
|------------|---------|----------|
| **Server State** | TanStack Query | Tasks, notifications, user session, mutations |
| **Client State** | Zustand | Filter selections, modal open/close, toasts |

### When to Use Which

- Use TanStack Query for data from API
- Use Zustand for transient UI state
- Never persist server state in Zustand

## Styling Conventions

### Tailwind v4

Uses `@theme` directive instead of v3 config:

```css
@theme {
  --color-primary-50: oklch(0.95 0.01 264);
  --color-primary: oklch(var(--primary));
}
```

### Color System

- Uses OKLCH for better color manipulation
- CSS variables for theme values
- Dark mode via `dark:` prefix
- Deep Space theme (dark mode)
- Slate/blue theme (light mode)

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

## Extension Points for Phase III

### AI Chat Interface

Pre-provisioned fields ready for Phase III:

```typescript
// types/task.ts
export interface Task {
  transcription_text: string | null  // Voice input
  ai_summary: string | null          // LLM summary
  embedding_id: string | null        // Vector search
}
```

### Voice Input Integration

```typescript
// Phase III: Add voice recording
const startRecording = () => {
  // Use Web Speech API or OpenAI Whisper
}
```

## Important Constraints

- **All API calls must go through api-client** — Don't use fetch directly
- **Server Actions require "use server"** — First line of file
- **JWT never stored in localStorage** — Always fetched from session
- **Filters persist in localStorage** — Via Zustand persist
- **TanStack Query for server state** — Never duplicate in Zustand
- **SSE provider must use { ssr: false }** — EventSource is browser-only
- **Push notifications require user permission** — Show permission modal first
