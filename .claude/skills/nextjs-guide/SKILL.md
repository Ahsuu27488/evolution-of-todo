---
name: nextjs-guide
description: Fetch Next.js documentation and apply React/frontend best practices. Use when building pages, components, or frontend features (Phase II+).
version: 2.0.0
---

# Next.js App Router Mastery Skill

## Theoretical Foundation

Next.js is a React framework that extends React with:
- **App Router**: File-based routing with React Server Components (RSC)
- **Server Actions**: Direct server function calls from forms
- **Streaming**: Progressive rendering with Suspense boundaries
- **Hydration**: Client-side interactivity where needed

### Rendering Model Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      NEXT.JS REQUEST FLOW                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Browser Request                                                              │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     Next.js Server                                 │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ Middleware  │───▶│ Route Match  │───▶│ React Rendering         │  │     │
│  │  │ (auth,      │    │ (file-based) │    │ (Server Components)     │  │     │
│  │  │  redirects) │    │              │    │                         │  │     │
│  │  └─────────────┘    └──────┬───────┘    └───────────┬─────────────┘  │     │
│  │                            │                        │                 │     │
│  │                            │ Data Fetching          │                 │     │
│  │                            │ (async, DB, API)       │                 │     │
│  │                            ▼                        ▼                 │     │
│  │                    ┌───────────────┐      ┌───────────────┐          │     │
│  │                    │ HTML Stream   │      │ Client Bundle │          │     │
│  │                    │ (RSC Payload) │      │ (JS + CSS)    │          │     │
│  │                    └───────┬───────┘      └───────┬───────┘          │     │
│  └────────────────────────────┼───────────────────────┼─────────────────┘     │
│                               │                       │                       │
│  Initial HTML Response        │                       │                       │
│  (with RSC payload)           │                       │                       │
│                               │                       │                       │
│  ┌────────────────────────────┼───────────────────────┼─────────────────┐     │
│  │              Browser Hydration (React Client)       │                 │     │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │     │
│  │  │  Server Components (static, interactive via Server Actions)     │ │     │
│  │  │  Client Components (useState, useEffect, event handlers)        │ │     │
│  │  └─────────────────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Server Component (Default)**: No `"use client"`, runs on server, no React hooks
2. **Client Component**: Has `"use client"`, runs in browser, full React API
3. **Server Action**: `"use server"` function, callable from forms, runs on server
4. **Route Groups**: `(folder)` for organization without URL path
5. **Parallel Routes**: `@folder` for independent slot rendering
6. **Streaming**: Progressive rendering with `<Suspense>`

## When to Use This Skill

Activation triggers:
- Creating pages with App Router
- Implementing Server Components vs Client Components
- Using Server Actions for mutations
- Setting up middleware for auth
- Data fetching and caching strategies

## Context7 Research Results

**Library ID**: `/vercel/next.js`
**Source**: https://nextjs.org/docs
**Reputation**: High
**Code Snippets**: 2103+
**Latest Version**: v16.1.0

### Server Component Pattern (from Context7)

```typescript
// app/page.tsx - Server Component (default)
import HomePage from './home-page'

async function getPosts() {
  const res = await fetch('https://...')
  const posts = await res.json()
  return posts
}

export default async function Page() {
  // Fetch data directly in Server Component
  const recentPosts = await getPosts()
  // Forward fetched data to Client Component
  return <HomePage recentPosts={recentPosts} />
}
```

### Server Action Pattern (from Context7)

```typescript
// app/actions.ts - Server Function
'use server'

export async function createPost() {}

// components/button.tsx - Client Component
'use client'

import { createPost } from '@/app/actions'

export function Button() {
  return <button formAction={createPost}>Create</button>
}
```

### Form with Server Action (from Context7)

```typescript
"use client";

import { useFormState, useFormStatus } from "react-dom";
import { createTodo } from "@/app/actions";

const initialState = { message: "" };

function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? 'Adding...' : 'Add'}</button>;
}

export function AddForm() {
  const [state, formAction] = useFormState(createTodo, initialState);

  return (
    <form action={formAction}>
      <input type="text" id="todo" name="todo" required />
      <SubmitButton />
      <p>{state?.message}</p>
    </form>
  );
}
```

## Implementation Guidelines

### 1. App Router Structure

```
app/
├── (auth)/              # Route group (no URL segment)
│   ├── login/
│   │   └── page.tsx
│   └── signup/
│       └── page.tsx
├── dashboard/
│   ├── page.tsx         # Server Component
│   ├── loading.tsx      # Suspense loading UI
│   └── error.tsx        # Error boundary
├── layout.tsx           # Root layout
├── page.tsx             # Home page
├── globals.css
├── actions/             # Server Actions
│   └── tasks.ts
└── api/                 # Route handlers
    └── auth/
        └── [...all]/
            └── route.ts
```

### 2. Server Component with Data Fetching

```typescript
// app/dashboard/page.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { DashboardContent } from "@/components/dashboard-content"

export default async function DashboardPage() {
  // Call headers() FIRST for auth
  const headersList = await headers()
  const session = await auth.api.getSession({ headers: headersList })

  if (!session?.user) {
    redirect("/login")
  }

  // Server-side data fetching
  const tasks = await fetchTasks(session.user.id)

  return <DashboardContent tasks={tasks} user={session.user} />
}
```

### 3. Client Component with Interactivity

```typescript
// components/task-card.tsx
"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Task } from "@/types"

interface TaskCardProps {
  task: Task
  onComplete: (id: number) => Promise<void>
}

export function TaskCard({ task, onComplete }: TaskCardProps) {
  const [isCompleting, setIsCompleting] = useState(false)

  async function handleToggle() {
    setIsCompleting(true)
    try {
      await onComplete(task.id)
    } finally {
      setIsCompleting(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Interactive UI */}
    </motion.div>
  )
}
```

### 4. Server Action with Error Handling

```typescript
// app/actions/tasks.ts
"use server"

import { revalidatePath } from "next/cache"
import { headers, cookies } from "next/headers"
import { auth } from "@/lib/auth"
import type { TaskCreate, TaskUpdate } from "@/types"

interface ActionResult<T> {
  success: boolean
  data?: T
  error?: { message: string }
}

export async function createTask(data: TaskCreate): Promise<ActionResult<Task>> {
  // Get authenticated session
  const headersList = await headers()
  const session = await auth.api.getSession({ headers: headersList })

  if (!session?.user) {
    return { success: false, error: { message: "Unauthorized" } }
  }

  try {
    // Call backend API
    const response = await fetch(`${process.env.API_URL}/api/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Get JWT from session
        "Authorization": `Bearer ${await getJWT(session)}`
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error("Failed to create task")
    }

    const task = await response.json()

    // Revalidate cached data
    revalidatePath("/dashboard")

    return { success: true, data: task }
  } catch (error) {
    return { success: false, error: { message: "Failed to create task" } }
  }
}
```

### 5. Middleware for Authentication

```typescript
// middleware.ts (Next.js 15.2.0+)
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { headers } from "next/headers"
import { auth } from "@/lib/auth"

export async function middleware(request: NextRequest) {
  // Skip API routes - handled separately
  if (request.nextUrl.pathname.startsWith("/api")) {
    return NextResponse.next()
  }

  // Check session
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  const publicRoutes = ["/", "/login", "/signup"]
  const isPublicRoute = publicRoutes.includes(request.nextUrl.pathname)

  if (!isPublicRoute && !session) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  runtime: "nodejs",
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}
```

## Code Standards

### Component Rules

| Rule | Description |
|------|-------------|
| **Default to Server** | No `"use client"` unless you need interactivity |
| **Client for Hooks** | Add `"use client"` for useState, useEffect, event handlers |
| **Server for Data** | Fetch data in Server Components, not Client Components |
| **Actions for Mutations** | Use Server Actions instead of POST to API routes |
| **Suspense for Loading** | Wrap slow components with `<Suspense>` |

### File Organization

```
✅ GOOD - Clear separation
app/
  dashboard/page.tsx      # Server Component (data fetching)
  components/
    dashboard-content.tsx  # Client Component (interactivity)
  actions/tasks.ts         # Server Actions

❌ BAD - Mixed concerns
app/
  dashboard/page.tsx       # Has "use client" + data fetching
  components/data.tsx      # Client Component fetching data
```

### Import Patterns

```typescript
// ✅ GOOD - Grouped imports
import { type Task } from "@/types/task"
import { Card } from "@/components/ui/card"
import { formatDate } from "@/lib/utils"

import { TaskActions } from "./task-actions"

// ❌ BAD - Scattered imports
import { Task } from "@/types/task"
import { Card } from "@/components/ui/card"
import { formatDate } from "@/lib/utils"
import { TaskActions } from "./task-actions"
```

## Common Pitfalls

### 1. Using Client Component for Data Fetching
**Symptom**: "use server" error, slow initial load
**Fix**: Move data fetching to Server Component, pass props to Client Component

### 2. Forgetting `"use server"` in Actions
**Symptom**: "use client" directive required error
**Fix**: Add `"use server"` at top of action file

### 3. Not Calling `headers()` First
**Symptom**: Auth fails in Server Components
**Fix**: Call `await headers()` before any other async operation

### 4. Missing `revalidatePath()` After Mutations
**Symptom**: Stale data after updates
**Fix**: Call `revalidatePath()` in Server Actions after mutations

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| App Router | "App Router server components client components routing" |
| Server Actions | "Server Actions useFormState useFormStatus mutations" |
| Data Fetching | "fetch caching revalidate async await server components" |
| Middleware | "middleware authentication redirect headers runtime" |
| Forms | "form actions useFormState error handling loading state" |
| Suspense | "Suspense loading.tsx streaming progressive rendering" |

## Performance Best Practices

1. **Server Components by Default**: Reduce client JavaScript
2. **Dynamic Imports**: Use `dynamic()` for heavy client components
3. **Image Optimization**: Always use `next/image`
4. **Font Optimization**: Use `next/font/google` with subsets
5. **Script Loading**: Use `next/script` with appropriate loading strategy

```typescript
import dynamic from "next/dynamic"
import Image from "next/image"
import { Geist } from "next/font/google"

// Dynamic import for heavy component
const HeavyChart = dynamic(() => import("./heavy-chart"), {
  loading: () => <p>Loading chart...</p>,
  ssr: false,
})

// Optimized font
const geist = Geist({ subsets: ["latin"] })

// Optimized image
<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority
/>
```

## References

- **Documentation**: https://nextjs.org/docs
- **App Router**: https://nextjs.org/docs/app
- **Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
- **Context7 ID**: `/vercel/next.js`
