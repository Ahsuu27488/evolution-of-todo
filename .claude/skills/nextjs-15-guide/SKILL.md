---
name: nextjs-15-guide
description: Fetch Next.js 15 documentation and apply App Router best practices. Use when building pages, Server/Client Components, Server Actions, middleware, data fetching, or forms in Next.js 15.x.
location: managed
version: 1.0.0
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Next.js 15 App Router Mastery Guide

## Theoretical Foundation

Next.js 15 represents the maturation of the App Router introduced in v13, with Server Components and Server Actions as first-class citizens. The framework enables **React Server Components (RSC)** by default, allowing selective client-side hydration for interactivity.

### Rendering Model Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      NEXT.JS 15 REQUEST FLOW                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Browser Request                                                              │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     Middleware (Edge)                               │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ Auth Check  │───▶│ Rewrites     │───▶│ Redirects              │  │     │
│  │  │ (cookies)   │    │ (i18n, A/B)  │    │ (protected routes)     │  │     │
│  │  └─────────────┘    └──────┬───────┘    └───────────┬─────────────┘  │     │
│  └────────────────────────────┼────────────────────────┘                 │     │
│                               ▼                                            │     │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     Next.js Server (Node)                           │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ Route Match │───▶│ React Server │───▶│ RSC Payload Generation  │  │     │
│  │  │ (file-based)│    │ Components  │    │ (serialized tree)       │  │     │
│  │  └─────────────┘    └──────┬───────┘    └───────────┬─────────────┘  │     │
│  │                            │                        │                 │     │
│  │                            │ Data Fetching          │                 │     │
│  │                            │ (async, DB, API)       │                 │     │
│  │                            ▼                        ▼                 │     │
│  │                    ┌───────────────┐      ┌───────────────┐          │     │
│  │                    │ HTML Stream   │      │ Client Bundle │          │     │
│  │                    │ (RSC + HTML)  │      │ (JS + CSS)    │          │     │
│  │                    └───────┬───────┘      └───────┬───────┘          │     │
│  └────────────────────────────┼───────────────────────┼─────────────────┘     │
│                               │                       │                       │
│  Initial HTML Response        │                       │                       │
│  (streamed to browser)        │                       │                       │
│                               ▼                       ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │              Browser Hydration (React Client)                       │     │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │     │
│  │  │  Server Components (static, interactive via Server Actions)     │ │     │
│  │  │  Client Components ("use client" - useState, useEffect)         │ │     │
│  │  └─────────────────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts in v15

| Concept | Description | Directive |
|---------|-------------|-----------|
| **Server Component** | Default; runs on server, no React hooks, direct DB access | None (default) |
| **Client Component** | Runs in browser, full React API | `"use client"` |
| **Server Action** | Callable from forms, runs on server | `"use server"` |
| **Route Group** | Organization without URL segment | `(folder)` |
| **Parallel Route** | Independent slot rendering | `@folder` |
| **Streaming** | Progressive rendering with Suspense | `<Suspense>` |

### v15.0 - v15.1 Key Features

- **useActionState**: React 19's replacement for useFormState (automatic in Next.js 15)
- **Improved Turbopack**: Faster dev builds with `--turbo`
- **Partial Prerendering (PPR)**: Stable static + dynamic rendering
- **Better Cache APIs**: `cacheTag`, `revalidateTag` improved
- **Enhanced Form Handling**: Native form validation with Server Actions

## When to Use This Skill

Activation triggers:
- Creating pages with App Router (`app/` directory)
- Implementing Server Components vs Client Components
- Using Server Actions for mutations
- Setting up middleware for authentication
- Data fetching with caching strategies
- Form handling with `useActionState` and `useFormStatus`

## Context7 Research

**Library ID**: `/vercel/next.js/v15.1.8`
**Source**: https://nextjs.org/docs
**Reputation**: High
**Code Snippets**: 2000+

### Server Component Pattern

```typescript
// app/dashboard/page.tsx - Server Component (default)
import { redirect } from "next/navigation"
import { headers } from "next/headers"
import { auth } from "@/lib/auth"
import { DashboardContent } from "@/components/dashboard-content"

export default async function DashboardPage() {
  // CRITICAL: Call headers() FIRST before any async operation
  const headersList = await headers()
  const session = await auth.api.getSession({ headers: headersList })

  if (!session?.user) {
    redirect("/login")
  }

  // Server-side data fetching
  const tasks = await fetchTasks(session.user.id)

  // Forward fetched data to Client Component
  return <DashboardContent tasks={tasks} user={session.user} />
}
```

### Server Action with Form Handling

```typescript
// app/actions/tasks.ts - Server Action
"use server"

import { revalidatePath } from "next/cache"
import { headers } from "next/headers"
import { auth } from "@/lib/auth"

interface ActionResult<T = void> {
  success: boolean
  data?: T
  error?: string
}

export async function createTask(formData: FormData): Promise<ActionResult> {
  // Get authenticated session
  const headersList = await headers()
  const session = await auth.api.getSession({ headers: headersList })

  if (!session?.user) {
    return { success: false, error: "Unauthorized" }
  }

  const title = formData.get("title") as string
  if (!title || title.trim().length === 0) {
    return { success: false, error: "Title is required" }
  }

  try {
    // Create task via API
    const response = await fetch(`${process.env.API_URL}/api/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({ title }),
    })

    if (!response.ok) throw new Error("Failed to create task")

    // Invalidate cached data
    revalidatePath("/dashboard")

    return { success: true }
  } catch (error) {
    return { success: false, error: "Failed to create task" }
  }
}
```

### Client Component Form with useActionState

```typescript
// components/task-form.tsx - Client Component
"use client"

import { useActionState } from "react"
import { createTask } from "@/app/actions/tasks"

const initialState = {
  message: "",
}

export function TaskForm() {
  const [state, formAction, pending] = useActionState(createTask, initialState)

  return (
    <form action={formAction}>
      <input type="text" name="title" placeholder="Task title" required />
      <button type="submit" disabled={pending}>
        {pending ? "Adding..." : "Add Task"}
      </button>
      {state?.error && <p className="error">{state.error}</p>}
    </form>
  )
}
```

### Submit Button with useFormStatus

```typescript
// components/submit-button.tsx - Client Component
"use client"

import { useFormStatus } from "react-dom"

export function SubmitButton({ children }: { children: React.ReactNode }) {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending} aria-disabled={pending}>
      {pending ? "Submitting..." : children}
    </button>
  )
}
```

### Middleware for Authentication

```typescript
// middleware.ts - Next.js 15 middleware
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { auth } from "@/lib/auth"

export async function middleware(request: NextRequest) {
  // Skip API routes - handled separately
  if (request.nextUrl.pathname.startsWith("/api")) {
    return NextResponse.next()
  }

  // Check session using Better Auth
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
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}
```

## Code Standards

### Component Rules

| Rule | Description |
|------|-------------|
| **Default to Server** | No `"use client"` unless you need interactivity |
| **Client for Hooks** | Add `"use client"` for useState, useEffect, event handlers |
| **Server for Data** | Fetch data in Server Components, pass props to Client |
| **Actions for Mutations** | Use Server Actions instead of POST to API routes |
| **Suspense for Loading** | Wrap slow components with `<Suspense>` |
| **headers() First** | Always call `await headers()` before other async operations in Server Components |

### File Organization

```
✅ GOOD - Clear separation
app/
  dashboard/page.tsx      # Server Component (data fetching, auth)
  components/
    dashboard-content.tsx  # Client Component (interactivity)
  actions/
    tasks.ts              # Server Actions

❌ BAD - Mixed concerns
app/
  dashboard/page.tsx       # Has "use client" + data fetching
  components/data.tsx      # Client Component fetching data
```

### Server Action Standards

```typescript
// ✅ GOOD - Proper error handling and types
"use server"

import { revalidatePath } from "next/cache"
import { headers } from "next/headers"

interface ActionResult<T = void> {
  success: boolean
  data?: T
  error?: { message: string }
}

export async function createAction(data: FormData): Promise<ActionResult> {
  const headersList = await headers()
  const session = await auth.api.getSession({ headers: headersList })

  if (!session) {
    return { success: false, error: { message: "Unauthorized" } }
  }

  // ... mutation logic
  revalidatePath("/dashboard")
  return { success: true }
}

// ❌ BAD - No error handling, no types
"use server"

export async function createAction(data: FormData) {
  await db.create(data)
}
```

## Common Pitfalls

### Pitfall 1: Using Client Component for Data Fetching

**Symptom**: Slow initial load, waterfalls, unnecessary client JS

**Fix**: Move data fetching to Server Component, pass props to Client Component

```typescript
// ❌ WRONG
"use client"
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetch("/api/data").then(setData) }, [])
  return <Display data={data} />
}

// ✅ CORRECT
export default async function Page() {
  const data = await fetch("/api/data").then(r => r.json())
  return <Display data={data} />
}
```

### Pitfall 2: Forgetting headers() First

**Symptom**: Auth fails, `headers() was called after` error

**Fix**: Always call `await headers()` before any other async operation

```typescript
// ❌ WRONG
export default async function Page() {
  const data = await fetchData()  // Async operation first!
  const headersList = await headers()
  // ...
}

// ✅ CORRECT
export default async function Page() {
  const headersList = await headers()  // First!
  const session = await auth.api.getSession({ headers: headersList })
  const data = await fetchData()
  // ...
}
```

### Pitfall 3: Missing revalidatePath After Mutations

**Symptom**: Stale data after updates

**Fix**: Call `revalidatePath()` in Server Actions

```typescript
// ❌ WRONG
export async function updateTask(id: string, data: FormData) {
  await db.update(id, data)
  // No revalidation - stale data persists
}

// ✅ CORRECT
export async function updateTask(id: string, data: FormData) {
  await db.update(id, data)
  revalidatePath("/dashboard")
  revalidatePath("/tasks")
}
```

### Pitfall 4: Using useFormState (React 18) in v15

**Symptom**: Unnecessary import, using deprecated pattern

**Fix**: Use React 19's `useActionState` (built into Next.js 15)

```typescript
// ❌ WRONG - React 18 pattern
import { useFormState } from "react-dom"

// ✅ CORRECT - React 19 pattern (default in Next.js 15)
import { useActionState } from "react"
```

## Data Fetching & Caching

### Caching Strategies

| Strategy | Use Case | Syntax |
|----------|----------|--------|
| **force-cache** | Static data, rarely changes | `fetch(url, { cache: "force-cache" })` |
| **no-store** | Always fresh, real-time data | `fetch(url, { cache: "no-store" })` |
| **revalidate** | Fresh data after interval | `fetch(url, { next: { revalidate: 60 } })` |
| **tags** | On-demand revalidation | `fetch(url, { next: { tags: ["posts"] } })` |

### Tag-Based Revalidation

```typescript
// Fetch with tag
export async function getPosts() {
  const res = await fetch("https://api.example.com/posts", {
    next: { tags: ["posts"] },
  })
  return res.json()
}

// Revalidate from Server Action
"use server"
import { revalidateTag } from "next/cache"

export async function createPost() {
  // ... create post
  revalidateTag("posts")
}
```

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| App Router | "App Router server components client components routing architecture" |
| Server Actions | "Server Actions useActionState useFormStatus mutations forms error handling" |
| Data Fetching | "fetch caching revalidate revalidateTag force-cache no-store server components" |
| Middleware | "middleware authentication redirect headers cookies runtime matcher" |
| Forms | "form actions useActionState error handling validation loading state pending" |
| Suspense | "Suspense loading.tsx streaming progressive rendering boundaries" |

## Performance Best Practices

1. **Server Components by Default**: Reduces client JavaScript bundle
2. **Dynamic Imports**: Use `dynamic()` for heavy client components
3. **Image Optimization**: Always use `next/image` for automatic optimization
4. **Font Optimization**: Use `next/font/google` with `subsets`
5. **Script Loading**: Use `next/script` with appropriate strategy

```typescript
import dynamic from "next/dynamic"
import Image from "next/image"
import { Inter } from "next/font/google"

// Dynamic import for heavy component (code splitting)
const HeavyChart = dynamic(() => import("./heavy-chart"), {
  loading: () => <p>Loading chart...</p>,
  ssr: false,
})

// Optimized font (self-hosting, no flash)
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
})

// Optimized image (automatic WebP, lazy loading, responsive)
<Image
  src="/hero.png"
  alt="Hero"
  width={1200}
  height={600}
  priority  // For above-fold images
/>
```

## References

- **Documentation**: https://nextjs.org/docs
- **App Router**: https://nextjs.org/docs/app
- **Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
- **Context7 ID**: `/vercel/next.js/v15.1.8`
