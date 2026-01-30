# Todo App — Next.js Frontend

[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.2.3-blue)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-blue)](https://typescriptlang.org)
[![Phase](https://img.shields.io/badge/Phase-II-Chronos_WebApp-success)](https://github.com/panaversity)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Phase II** frontend for the Chronos Todo Full-Stack Web Application — A modern Next.js App Router application with Better Auth, TanStack Query, and shadcn/ui components.

## Features

### Core Task Management
- User authentication with Better Auth (email/password)
- **Enhanced signup** with firstName/lastName fields (supports mononyms)
- **Dual-ring loading spinner** with smooth fade transitions
- **Error cards** with retry functionality
- Task CRUD operations with real-time updates
- Task filtering by status, priority, and tags
- Task sorting and search
- Recurring task support with auto-creation

### User Experience
- Dark mode support with next-themes (Deep Space theme)
- Light mode support with slate/blue color scheme
- Smooth animations with Framer Motion
- Responsive design with Tailwind CSS v4
- Error boundaries and toast notifications

### Notification System
- **In-App Notifications** — Real-time notification center with unread badge
- **SSE Streaming** — Server-Sent Events for instant updates
- **Push Notifications** — Web Push API with browser notifications
- **Push Permission Modal** — User-friendly permission request
- **Email Preferences** — Per-channel enable/disable settings
- **Push Settings** — Manage push subscriptions and test notifications

## Architecture

```
frontend/
├── app/
│   ├── (auth)/              # Auth route group
│   │   ├── login/           # Login page
│   │   ├── signup/          # Signup page
│   │   └── layout.tsx       # Auth layout
│   ├── api/auth/           # Better Auth API routes
│   │   ├── [...all]/route.ts
│   │   └── token/route.ts   # JWT token endpoint for API client
│   ├── dashboard/          # Main app page
│   │   ├── page.tsx         # Dashboard (task list)
│   │   └── loading.tsx
│   ├── actions/            # Server actions
│   │   ├── auth.ts          # Auth server actions
│   │   └── tasks.ts         # Task CRUD server actions
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   ├── error.tsx            # Error page
│   └── providers.tsx        # App providers
├── components/
│   ├── auth/                # Auth components
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx  # Now with firstName/lastName fields
│   ├── dashboard/           # Dashboard components
│   │   ├── dashboard-content.tsx  # Integrated with DualRingSpinner
│   │   ├── loading-error-card.tsx # Inline error handling
│   ├── layout/              # Layout components
│   │   ├── header.tsx       # Top navigation bar with notification bell
│   │   ├── user-nav.tsx     # User menu with displayName
│   │   ├── brand-logo.tsx
│   │   └── theme-toggle.tsx
│   ├── notifications/       # Notification components
│   │   ├── notification-bell.tsx       # Bell icon with unread badge
│   │   ├── notification-dropdown.tsx   # Notification list dropdown
│   │   ├── notification-item.tsx       # Individual notification
│   │   ├── notification-tabs.tsx       # Filter tabs (All, Unread)
│   │   ├── notifications-client.tsx    # Client wrapper for notifications
│   │   ├── sse-stream-provider.tsx     # SSE connection manager
│   │   ├── push-permission-modal.tsx   # Push permission request
│   │   ├── push-settings.tsx           # Push subscription settings
│   │   └── email-preferences.tsx       # Email preferences UI
│   ├── tasks/              # Task components
│   │   ├── task-card.tsx
│   │   ├── task-list.tsx
│   │   ├── task-form.tsx
│   │   ├── task-actions.tsx
│   │   └── empty-state.tsx
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── badge.tsx
│   │   └── dual-ring-spinner.tsx
│   ├── confetti.tsx
│   └── error-boundary.tsx
├── lib/
│   ├── auth.ts             # Better Auth configuration
│   ├── auth-client.ts      # Client-side auth helpers
│   ├── api-client.ts       # Backend API client
│   ├── errors.ts           # Error handling utilities
│   ├── stores/
│   │   └── ui-store.ts     # Zustand UI state
│   ├── validations/        # Zod schemas
│   └── utils.ts            # Utility functions
├── hooks/
│   └── use-notifications.ts # Notification queries & mutations
├── types/
│   └── task.ts             # TypeScript interfaces
├── middleware.ts           # Auth middleware
├── tailwind.config.ts      # Tailwind v4 config
└── package.json
```

## Tech Stack

| Category | Library | Purpose |
|----------|---------|---------|
| **Framework** | Next.js 15.2.8 | App Router, React Server Components |
| **UI Library** | React 19.2.3 | Component framework |
| **Language** | TypeScript 5+ | Type safety |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | shadcn/ui + Radix UI | Accessible UI primitives |
| **Animations** | Framer Motion 12+ | Page transitions, micro-interactions |
| **State** | TanStack Query 5+ | Server state management |
| **State** | Zustand 5+ | Client UI state |
| **Auth** | Better Auth 1.4.9 | Authentication with JWT plugin |
| **Database** | @neondatabase/serverless | Neon PostgreSQL WebSocket driver |
| **Forms** | React Hook Form 7+ | Form validation |
| **Validation** | Zod 4+ | Schema validation |
| **Toasts** | Sonner 2+ | Toast notifications |
| **Page Transitions** | next-view-transitions | Smooth SPA-like navigation |

## Installation

### Prerequisites
- Node.js 20+
- npm, yarn, or pnpm

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

## Configuration

Create a `.env.local` file:

```bash
# Neon PostgreSQL Database (same as backend)
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Better Auth Secret (MUST match backend)
BETTER_AUTH_SECRET=your-32-character-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# App URL (for auth redirects)
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Usage

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

## Authentication Flow

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
      │  4. Stores in memory
      │  5. Sends with API requests
      ▼
┌──────────────┐
│  FastAPI     │
│  Backend     │
└──────────────┘
```

## Key Components

### Notification System

The frontend includes a comprehensive notification system with multi-channel support:

**Notification Bell** (`components/notifications/notification-bell.tsx`):
- Bell icon with animated Badge showing unread count
- Framer Motion animations (scale, spring transitions)
- Integrates with Radix UI DropdownMenu
- Displays "9+" for counts > 9

**Notification Dropdown** (`components/notifications/notification-dropdown.tsx`):
- Full-featured dropdown with notification list
- Filter tabs: All / Unread
- Mark as read functionality
- Delete notifications
- Mark all as read action
- Empty state with helpful message

**SSE Stream Provider** (`components/notifications/sse-stream-provider.tsx`):
- Client-only component (must be imported with `{ ssr: false }`)
- Manages EventSource connection to `/api/notifications/stream`
- Auto-reconnect with exponential backoff (max 5 attempts)
- Updates TanStack Query cache for instant UI refresh
- Handles notification and notification_read events

**Push Permission Modal** (`components/notifications/push-permission-modal.tsx`):
- User-friendly browser notification permission request
- Explains benefits of push notifications
- Shows permission status (granted/denied/default)
- Allows re-requesting permission

**Push Settings** (`components/notifications/push-settings.tsx`):
- Current subscription status display
- Unsubscribe from push notifications
- Send test push notification
- Links to browser notification settings

**Email Preferences** (`components/notifications/email-preferences.tsx`):
- Per-channel enable/disable toggles
- Task notifications (due, overdue, completed)
- System notifications
- Digest settings (daily, weekly)
- Send test email button

### Loading States

The app uses custom loading components for better UX:

**DualRingSpinner** (`components/ui/dual-ring-spinner.tsx`):
- Pure CSS dual-ring animation (no JS overhead)
- Outer ring: neon cyan, clockwise rotation
- Inner ring: neon purple, counter-clockwise rotation
- Minimum display duration (400ms) to prevent flash
- Fade-out transition (300ms) for smooth UX

**LoadingErrorCard** (`components/dashboard/loading-error-card.tsx`):
- Inline error display with retry button
- Accessible error handling (role="alert")
- Automatic retry functionality
- User-friendly error messages

**Integration** (`components/dashboard/dashboard-content.tsx`):
- Conditional rendering: loading → error → success
- 15-second timeout with error fallback
- Debounce logic for rapid tab switches

### Authentication

- **Better Auth** configured with Neon PostgreSQL and JWT plugin
- JWT tokens issued with HS256 (shared secret with backend)
- Session stored in httpOnly cookies
- Token accessible via `/api/auth/token` endpoint

**User Profile** (`lib/auth-client.ts`):
- `firstName` (string, required): User's first name
- `lastName` (string, optional): User's last name
- `displayName` (string, computed): "First Last" or "First" or email fallback
- `getDisplayName()` helper: Fallback logic for inclusive name display

**Signup Form** (`components/auth/signup-form.tsx`):
- Separate firstName (required) and lastName (optional) fields
- 50-character limit per field
- XSS prevention validation (HTML tag rejection)
- Whitespace trimming
- Supports mononyms (first name only)

### API Client

The `lib/api-client.ts` module handles all backend communication:
- Automatic JWT token retrieval
- Request timeout handling (15s default)
- Automatic retry for transient failures
- Comprehensive error handling

### State Management

- **Server State**: TanStack Query for tasks, user session
- **Client State**: Zustand for filters, modals, toasts

### Forms

- React Hook Form for form state
- Zod schemas for validation
- Server actions for mutations

## Styling

### Theme

The app uses Tailwind CSS v4 with CSS variables for theming:

```css
@theme {
  --color-primary: oklch(var(--primary));
  --color-background: oklch(var(--background));
  /* ... more variables */
}
```

### Dark Mode

Dark mode is handled by `next-themes`:
- Persists user preference
- Avoids FOUC (flash of unstyled content)
- Toggle in header user menu

## Deployment

### Environment Variables

Ensure all required environment variables are set:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (≥32 chars) |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `BETTER_AUTH_URL` | No | App URL for auth (defaults to APP_URL) |
| `NEXT_PUBLIC_APP_URL` | No | Public app URL |

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## Contributing

See the main [README](../README.md) for contribution guidelines.

## License

MIT License — see [LICENSE](../LICENSE) for details.
