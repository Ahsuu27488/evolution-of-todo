# Todo App — Next.js Frontend

[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.2.3-blue)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-blue)](https://typescriptlang.org)
[![Phase](https://img.shields.io/badge/Phase-II--success)](https://github.com/panaversity)
[![Phase](https://img.shields.io/badge/Phase_III-AI_Chatbot-success)](https://github.com/panaversity)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Phase II + Phase III** frontend for the Chronos Todo Full-Stack Web Application — A modern Next.js App Router application with Better Auth, TanStack Query, shadcn/ui components, and AI Chatbot integration.

---

## 🎯 Features Overview

### Phase II: Core Task Management (Complete)
- ✅ **User Authentication** — Better Auth with email/password (JWT-based)
- ✅ **Enhanced User Profile** — firstName/lastName fields with mononym support
- ✅ **Task CRUD Operations** — Create, read, update, delete with real-time updates
- ✅ **Task Organization** — Priorities (HIGH/MEDIUM/LOW), colored tags, due dates
- ✅ **Recurring Tasks** — Daily, weekly, monthly patterns with auto-creation
- ✅ **Task Filtering** — Filter by status, priority, tags
- ✅ **Task Sorting** — Sort by created date, due date, priority
- ✅ **Task Search** — Real-time full-text search
- ✅ **Dark Mode** — Deep Space theme with glassmorphism design
- ✅ **Light Mode** — Slate/blue color scheme with proper contrast

### Phase III: AI Chatbot (Complete)
- ✅ **Natural Language Task Management** — Conversational interface via AI
- ✅ **SSE Streaming Responses** — Real-time token streaming
- ✅ **Voice Input** — Whisper API transcription with 30-second recording
- ✅ **Urdu Language Support** — RTL rendering with Noto Nastaliq Urdu font
- ✅ **Conversation History** — Persistent chat conversations
- ✅ **Tool Calling Display** — Visual feedback for AI agent actions
- ✅ **Agent Handoff Notifications** — Show when AI agents switch

### Multi-Channel Notification System
- ✅ **In-App Notifications** — Real-time notification center with unread badge
- ✅ **SSE Streaming** — Server-Sent Events for instant updates
- ✅ **Push Notifications** — Web Push API with browser notifications
- ✅ **Email Notifications** — Per-channel preferences, digest emails
- ✅ **Push Permission Modal** — User-friendly permission request flow

---

## 🏗️ Architecture

```
frontend/
├── app/
│   ├── (auth)/              # Auth route group (login, signup)
│   │   ├── layout.tsx       # Auth layout with public access
│   │   ├── login/           # Login page
│   │   └── signup/          # Signup page with firstName/lastName
│   ├── dashboard/          # Main app page
│   │   ├── page.tsx         # Dashboard (task list)
│   │   └── loading.tsx     # Loading state with dual-ring spinner
│   ├── settings/           # Settings pages
│   │   └── notifications/  # Notification settings
│   ├── profile/            # User profile page
│   ├── actions/            # Server actions (auth, tasks, notifications)
│   ├── api/auth/           # Better Auth API routes + JWT token endpoint
│   ├── layout.tsx          # Root layout with fonts and providers
│   ├── providers.tsx       # App providers (TanStack Query, Theme, Chat)
│   ├── page.tsx            # Landing page
│   ├── error.tsx           # Error page
│   └── globals.css         # Global styles with Deep Space theme
├── components/
│   ├── auth/               # Authentication components
│   │   ├── login-form.tsx
│   │   ├── signup-form.tsx  # With firstName/lastName fields
│   │   └── profile-form.tsx # User profile editing
│   ├── chat/               # Phase III: AI Chatbot components
│   │   ├── chat-panel.tsx   # Main floating chat interface
│   │   ├── chat-input.tsx   # Message input with voice button
│   │   ├── chat-message.tsx # Message display with RTL support
│   │   ├── voice-recorder.tsx  # Whisper transcription
│   │   └── task-card.tsx    # Inline task cards in chat
│   ├── dashboard/          # Dashboard components
│   │   ├── dashboard-content.tsx    # Main content area
│   │   ├── dashboard-toolbar.tsx    # Filters, search, sort
│   │   ├── loading-error-card.tsx  # Inline error handling
│   │   └── sort-dropdown.tsx        # Sort options
│   ├── layout/             # Layout components
│   │   ├── header.tsx       # Top nav with notification bell
│   │   ├── user-nav.tsx     # User menu with displayName
│   │   ├── brand-logo.tsx
│   │   ├── theme-toggle.tsx # Dark/light mode switch
│   │   └── adblock-warning.tsx
│   ├── notifications/      # Notification system
│   │   ├── notification-bell.tsx       # Bell icon with unread badge
│   │   ├── notification-dropdown.tsx   # Notification list dropdown
│   │   ├── notification-item.tsx       # Individual notification
│   │   ├── notification-tabs.tsx       # Filter tabs (All, Unread)
│   │   ├── notifications-client.tsx    # Client wrapper
│   │   ├── sse-stream-provider.tsx     # SSE connection manager
│   │   ├── push-permission-modal.tsx   # Push permission request
│   │   ├── push-settings.tsx           # Push subscription management
│   │   ├── email-preferences.tsx       # Email preferences UI
│   │   └── notification-empty-state.tsx # Empty state illustration
│   ├── tasks/              # Task components
│   │   ├── task-list.tsx    # Staggered animations
│   │   ├── task-card.tsx    # Individual task with actions
│   │   ├── task-form.tsx    # Create/edit modal with glassmorphism
│   │   ├── task-actions.tsx # Complete, edit, delete actions
│   │   ├── due-date-picker.tsx   # DateTime picker with formatting
│   │   └── empty-state.tsx  # Empty state illustration
│   ├── tags/               # Tag components
│   │   └── tag-input.tsx    # Colored tag input with Enter to add
│   ├── landing/            # Landing page components
│   │   ├── hero-header.tsx
│   │   └── hero-section.tsx
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── badge.tsx
│   │   ├── dual-ring-spinner.tsx  # Custom dual-ring loading animation
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── textarea.tsx
│   │   ├── select.tsx
│   │   ├── calendar.tsx
│   │   ├── tabs.tsx
│   │   ├── switch.tsx
│   │   ├── checkbox.tsx
│   │   ├── alert-dialog.tsx
│   │   ├── popover.tsx
│   │   ├── label.tsx
│   │   ├── card.tsx
│   │   ├── sonner.tsx
│   │   └── skeleton.tsx
│   ├── confetti.tsx        # Celebration effects (canvas-confetti)
│   └── error-boundary.tsx   # Error boundary wrapper
├── lib/
│   ├── auth.ts             # Better Auth configuration
│   ├── auth-client.ts      # Client-side auth helpers (displayName)
│   ├── auth/token.ts       # Shared JWT token utility (Phase III)
│   ├── api-client.ts       # Backend API client (auto-fetches JWT)
│   ├── api/chat.ts          # Chat API client with SSE streaming (Phase III)
│   ├── config/api.ts        # Centralized API URL config (Phase III)
│   ├── errors.ts           # Error handling utilities (ApiError, Result type)
│   ├── validations/        # Zod schemas
│   │   ├── task.ts         # Task validation schemas
│   │   └── auth.ts         # Auth validation schemas
│   ├── utils/
│   │   ├── sse.ts          # SSE parsing utilities (Phase III)
│   │   ├── text-direction.ts  # RTL/Urdu text detection (Phase III)
│   │   ├── tag-utils.ts    # Tag color generation
│   │   └── adblock-detector.ts
│   ├── hooks/
│   │   ├── use-task-filters.ts  # Task filter hook
│   │   └── use-debounce.ts      # Debounce hook
│   ├── stores/
│   │   ├── ui-store.ts     # Zustand UI state (filters, modals)
│   │   └── chat-store.ts    # React Context for chat UI (Phase III)
│   └── animations.ts       # Framer Motion animation variants
├── hooks/
│   ├── use-notifications.ts    # Notification queries & mutations
│   ├── use-notification-stream.ts  # SSE stream hook
│   ├── use-push-subscription.ts  # Push subscription hook
│   └── use-chat.ts          # Chat queries & mutations (Phase III)
├── types/
│   ├── task.ts             # TypeScript interfaces (Task, TaskCreate, TaskUpdate)
│   ├── notification.ts      # Notification types
│   └── chat.ts             # Chat types (Phase III)
├── middleware.ts            # Auth middleware for protected routes
└── public/                  # Static assets
    ├── sw.js               # Service worker for push notifications
    └── favicon.png
```

---

## 🛠️ Technology Stack

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| **Framework** | Next.js | 15.2.8 | App Router, React Server Components |
| **UI Library** | React | 19.2.3 | Component framework |
| **Language** | TypeScript | 5+ | Type safety |
| **Styling** | Tailwind CSS | v4 | Utility-first CSS with @theme directive |
| **Animations** | Framer Motion | 12.24.7 | Page transitions, micro-interactions |
| **Animations** | tw-animate-css | 1.4.0 | Pre-built CSS animations |
| **State** | TanStack Query | 5.90.16 | Server state management |
| **State** | Zustand | 5.0.9 | Client UI state (filters, modals) |
| **State** | React Context | — | Chat UI state (avoids SSR issues) |
| **Auth** | Better Auth | 1.4.9 | Authentication with JWT plugin |
| **Database** | @neondatabase/serverless | 1.0.2 | Neon PostgreSQL WebSocket driver |
| **AI SDK** | @ai-sdk/react | 1.2.4 | Vercel AI SDK React hooks |
| **AI SDK** | @ai-sdk/openai | 1.3.2 | OpenAI provider for Vercel AI SDK |
| **Forms** | React Hook Form | 7.69.0 | Form validation |
| **Validation** | Zod | 4.2.1 | Schema validation |
| **Toasts** | Sonner | 2.0.7 | Toast notifications |
| **Transitions** | next-view-transitions | 0.3.5 | SPA-like navigation |
| **Markdown** | react-markdown | 10.1.0 | Markdown rendering in chat |
| **Icons** | Lucide React | 0.562.0 | Icon library |
| **Calendar** | react-day-picker | 9.13.0 | Date picker for due dates |
| **Confetti** | canvas-confetti | 1.9.4 | Celebration effects |
| **SSE Parsing** | eventsource-parser | 3.0.2 | Server-Sent Events parsing |
| **WebSocket** | ws | 8.19.0 | WebSocket for real-time features |
│
| **Component Libraries** | | | |
| **Primitives** | Radix UI | — | Accessible UI primitives |
| **Components** | shadcn/ui | — | Styled component collection |
| **DevTools** | @tanstack/react-query-devtools | 5.91.2 | Query debugging (dev only) |

---

## 📦 Installation

### Prerequisites
- **Node.js** 20+
- **npm**, **yarn**, or **pnpm**

### Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

---

## ⚙️ Configuration

Create a `.env.local` file:

```bash
# Neon PostgreSQL Database (same as backend)
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Better Auth Secret (MUST match backend, ≥32 characters)
BETTER_AUTH_SECRET=your-32-character-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# App URL (for auth redirects)
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# OpenAI API (for AI chatbot in Phase III)
OPENAI_API_KEY=your-openai-api-key-here
```

---

## 🚀 Usage

### Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

---

## 🔐 Authentication Flow

```
┌─────────────┐     Sign In/Up      ┌──────────────┐
│   Frontend  │─────────────────────▶│  Better Auth│
└─────────────┘                     └──────────────┘
      │                                     │
      │  1. Creates session cookie          │
      │  2. Generates JWT token             │
      ▼                                     │
┌─────────────┐                             │
│   API Client│─────────────────────────────┘
│             │
└─────────────┘
      │
      │  3. Gets JWT from /api/auth/token
      │  4. Sends with API requests
      ▼
┌──────────────┐
│  FastAPI     │
│  Backend     │
└──────────────┘
```

### JWT Token Handling

The frontend automatically fetches JWT tokens via `/api/auth/token`:

```typescript
// lib/auth/token.ts - Shared utility
import { getAuthToken } from "@/lib/auth/token";

// Used in all API clients
const token = await getAuthToken();
```

This shared utility is used by:
- `lib/api-client.ts` — Task/Notification API calls
- `lib/api/chat.ts` — Chat API calls
- `hooks/use-chat.ts` — Chat mutations

---

## 🤖 AI Chatbot (Phase III)

### Features

| Feature | Description |
|---------|-------------|
| **Natural Language Interface** | Talk to the AI to manage tasks |
| **SSE Streaming** | Real-time token-by-token responses |
| **Voice Input** | Whisper API transcription (30s limit) |
| **Urdu Language** | Full RTL support with Noto Nastaliq Urdu font |
| **Conversation History** | Persistent chat sessions |
| **Tool Calling** | Visual feedback when AI uses task tools |
| **Agent Handoffs** | Notifications when AI agents switch |

### Chat Components

| Component | File | Purpose |
|-----------|------|---------|
| Chat Panel | `chat-panel.tsx` | Floating chat interface |
| Message Input | `chat-input.tsx` | Text input with voice button |
| Message Display | `chat-message.tsx` | User/assistant messages with RTL |
| Voice Recorder | `voice-recorder.tsx` | Audio recording with transcription |
| Task Cards | `task-card.tsx` | Inline task display in chat |

### Chat SSE Events

| Event | Data | Action |
|-------|------|--------|
| `message_start` | `{ conversationId, correlationId }` | Initialize streaming |
| `token` | `{ content }` | Append to message |
| `tool_call` | `{ tool, arguments }` | Show tool indicator |
| `tool_result` | `{ tool, output }` | Show tool result |
| `agent_handoff` | `{ from_agent, to_agent }` | Show handoff |
| `message_done` | `{ finalOutput, agent }` | Finalize message |
| `error` | `{ message }` | Show error |

---

## 🔔 Notification System

### Notification Types

| Type | Description |
|------|-------------|
| `TASK_DUE` | Task due soon |
| `TASK_OVERDUE` | Task is overdue |
| `TASK_COMPLETED` | Task marked complete |
| `TASK_ASSIGNED` | Task assigned to user |
| `SYSTEM_UPDATE` | System notifications |

### Channels

| Channel | Description |
|---------|-------------|
| **In-App** | Real-time via SSE |
| **Push** | Web Push API (browser notifications) |
| **Email** | Resend integration with digest options |

### SSE Events

| Event | Data | Action |
|-------|------|--------|
| `notification` | Notification object | Add to list, increment unread |
| `notification_read` | `{ id }` | Mark as read, decrement unread |
| `ping` | `{ timestamp }` | Keep connection alive |

---

## 🎨 Styling

### Theme System

**Tailwind CSS v4** with `@theme` directive:

```css
@import "tailwindcss";

@theme {
  /* Colors reference CSS custom properties */
  --color-primary: var(--custom-primary); /* Neon cyan #00f5ff */
  --color-secondary: var(--custom-secondary); /* Neon purple #a855f7 */
}
```

### Deep Space Color Theme

**Dark Mode (Default)**:
- Background: `oklch(0.08 0.01 270)` — Deep space black
- Primary: `oklch(0.91 0.17 195)` — Neon cyan
- Secondary: `oklch(0.65 0.26 293)` — Neon purple
- Destructive: `oklch(0.60 0.25 25)` — Red

**Light Mode**:
- Background: `oklch(0.98 0.005 270)` — Near-white
- Same brand colors (cyan/purple) maintained

### Glassmorphism Utilities

```css
.glass { /* Glass card effect */ }
.glass-strong { /* Stronger glass effect */ }
.glass-modal { /* Modal glass effect */ }
.glow-cyan { /* Neon cyan glow */ }
.glow-purple { /* Neon purple glow */ }
```

### Typography

| Font | Usage |
|------|-------|
| Geist Sans | Body text |
| Geist Mono | Code, numbers |
| Noto Nastaliq Urdu | Urdu script rendering |

---

## 📱 Key Components

### Loading States

**DualRingSpinner** (`components/ui/dual-ring-spinner.tsx`):
- Pure CSS dual-ring animation (no JS overhead)
- Outer ring: Neon cyan, clockwise rotation
- Inner ring: Neon purple, counter-clockwise rotation
- Minimum display duration (400ms) to prevent flash
- Fade-out transition (300ms) for smooth UX

### Task Form

**Glassmorphism Modal** (`components/tasks/task-form.tsx`):
- Slides in from bottom with backdrop blur
- Fields: Title, Description, Priority, Due Date, Tags, Recurrence
- Tag input with Enter to add, × to remove
- DateTime picker for due dates
- Recurrence pattern selector (Daily, Weekly, Monthly)

### Notification Bell

**Animated Badge** (`components/notifications/notification-bell.tsx`):
- Framer Motion animations (scale, spring transitions)
- Displays "9+" for counts > 9
- Integrates with Radix UI DropdownMenu
- Real-time unread count updates via SSE

---

## 🔧 Development Patterns

### Type-Safe API Calls

All API calls use `Result<T>` pattern:

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

// Usage
const result = await api.getTasks()
if (result.success) {
  const tasks = result.data
} else {
  toast.error(result.error.message)
}
```

### Shared Utilities (Phase III)

**Always use shared utilities instead of duplicating code:**

```typescript
// ✅ Good - Use shared utility
import { getAuthToken } from "@/lib/auth/token";
import { parseSSEStream } from "@/lib/utils/sse";
import { getTextDirection } from "@/lib/utils/text-direction";

// ❌ Bad - Duplicate implementation
async function getAuthToken() { /* ... */ }
```

### Component Patterns

- **Server Components by default** — No "use client" unless needed
- **Client Components only for interactivity** — State, event handlers
- `"use client"` directive at top of client files

---

## 📊 State Management

| State Type | Library | Examples |
|------------|---------|----------|
| **Server State** | TanStack Query | Tasks, notifications, conversations |
| **Client State** | Zustand | Filters, modals, toasts |
| **Chat State** | React Context | Messages, streaming, UI state |

### When to Use Which

- Use **TanStack Query** for data from API
- Use **Zustand** for persistent client-side preferences
- Use **React Context** for interactive component state (chat, modals)
- Never persist server state in client stores

---

## 🚀 Deployment

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (≥32 chars) |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `BETTER_AUTH_URL` | No | App URL for auth (defaults to APP_URL) |
| `NEXT_PUBLIC_APP_URL` | No | Public app URL |
| `OPENAI_API_KEY` | Yes | OpenAI API key for chatbot |

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

## 📄 License

MIT License — see [LICENSE](../LICENSE) for details.
