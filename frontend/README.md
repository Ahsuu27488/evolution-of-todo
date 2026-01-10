# Todo App — Next.js Frontend

[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.2.3-blue)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-blue)](https://typescriptlang.org)
[![Phase](https://img.shields.io/badge/Phase-II-Chronos_WebApp-success)](https://github.com/panaversity)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Phase II** frontend for the Chronos Todo Full-Stack Web Application — A modern Next.js App Router application with Better Auth, TanStack Query, and shadcn/ui components.

## Features

- User authentication with Better Auth (email/password)
- Task CRUD operations with real-time updates
- Task filtering by status, priority, and tags
- Task sorting and search
- Recurring task support with auto-creation
- Dark mode support with next-themes
- Smooth animations with Framer Motion
- Responsive design with Tailwind CSS v4
- Error boundaries and toast notifications

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
│   │   └── signup-form.tsx
│   ├── dashboard/           # Dashboard components
│   │   └── dashboard-content.tsx
│   ├── layout/              # Layout components
│   │   ├── header.tsx
│   │   ├── user-nav.tsx
│   │   ├── brand-logo.tsx
│   │   └── theme-toggle.tsx
│   ├── tasks/              # Task components
│   │   ├── task-card.tsx
│   │   ├── task-list.tsx
│   │   ├── task-form.tsx
│   │   ├── task-actions.tsx
│   │   └── empty-state.tsx
│   ├── ui/                 # shadcn/ui components
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

### Authentication

- **Better Auth** configured with Neon PostgreSQL and JWT plugin
- JWT tokens issued with HS256 (shared secret with backend)
- Session stored in httpOnly cookies
- Token accessible via `/api/auth/token` endpoint

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
