---
name: tanstack-query-guide
description: Fetch TanStack Query v5 documentation and apply server state management patterns. Use when implementing useQuery, useMutation, cache invalidation, optimistic updates, or integrating with Next.js App Router and Server Actions. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context-docs
  - Read
  - Write
  - Edit
---

# TanStack Query v5 Mastery Guide

## Theoretical Foundation

TanStack Query (formerly React Query) manages **server state** - data that comes from an API and is controlled by a server. This is fundamentally different from **client state** (UI-only data managed by useState/Zustand).

### Server State vs Client State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVER STATE                                   │
│  (TanStack Query)                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Origin: Remote API / Database                                           │
│  • Ownership: Shared (anyone can modify)                                   │
│  • Lifecycle: Asynchronous fetching, caching, background refetching        │
│  • Concerns: Stale data, cache invalidation, loading/error states         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT STATE                                   │
│  (useState, Zustand)                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Origin: User interactions                                                │
│  • Ownership: Local (only this client)                                     │
│  • Lifecycle: Synchronous state updates                                    │
│  • Concerns: Component re-renders, state propagation                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Concepts

1. **Query**: Fetching and caching data (GET requests)
2. **Mutation**: Modifying data (POST/PUT/DELETE requests)
3. **Query Client**: Central cache manager
4. **Query Key**: Unique identifier for cached data
5. **Cache Invalidation**: Keeping cached data fresh

## Core Patterns

### 1. Query Setup with Next.js App Router

```typescript
// app/lib/query-client.ts
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            gcTime: 1000 * 60 * 10, // 10 minutes (was cacheTime in v4)
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// app/layout.tsx
import { QueryProvider } from './lib/query-client'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
```

### 2. Fetching Data with useQuery

```typescript
import { useQuery } from '@tanstack/react-query'

async function fetchTodos() {
  const response = await fetch('/api/todos')
  if (!response.ok) {
    throw new Error('Failed to fetch todos')
  }
  return response.json()
}

function TodoList() {
  const {
    data: todos,
    isLoading,
    isError,
    error,
    isFetching, // Different from isLoading - true for background refetches
  } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    staleTime: 1000 * 60, // 1 minute - consider data fresh
  })

  if (isLoading) return <div>Loading...</div>
  if (isError) return <div>Error: {(error as Error).message}</div>

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  )
}
```

### 3. Query Options Pattern

```typescript
import { queryOptions } from '@tanstack/react-query'

export const todoOptions = queryOptions({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  staleTime: 1000 * 60,
})

// Usage
function TodoList() {
  const { data, isLoading } = useQuery(todoOptions)
  // ...
}
```

### 4. Mutations with Invalidation

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreateTodoForm() {
  const queryClient = useQueryClient()

  const createTodo = useMutation({
    mutationFn: async (text: string) => {
      const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      return response.json()
    },
    // Invalidate and refetch after success
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        const formData = new FormData(e.currentTarget)
        createTodo.mutate(formData.get('text') as string)
      }}
    >
      <input name="text" />
      <button disabled={createTodo.isPending}>
        {createTodo.isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  )
}
```

### 5. Optimistic Updates

The most powerful pattern for UX:

```typescript
function TodoItem({ todo }) {
  const queryClient = useQueryClient()

  const toggleTodo = useMutation({
    mutationFn: async ({ id, completed }: { id: string; completed: boolean }) => {
      const response = await fetch(`/api/todos/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed }),
      })
      return response.json()
    },

    // Called before mutation - update cache optimistically
    onMutate: async ({ id, completed }) => {
      // Cancel outgoing refetches to avoid overwriting
      await queryClient.cancelQueries({ queryKey: ['todos'] })

      // Snapshot previous value for rollback
      const previousTodos = queryClient.getQueryData(['todos'])

      // Optimistically update cache
      queryClient.setQueryData(['todos'], (old) =>
        old?.map((t) => (t.id === id ? { ...t, completed } : t))
      )

      // Return context for onError
      return { previousTodos }
    },

    // Rollback on error
    onError: (err, variables, context) => {
      if (context?.previousTodos) {
        queryClient.setQueryData(['todos'], context.previousTodos)
      }
    },

    // Always refetch after error or success
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  return (
    <label>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={(e) =>
          toggleTodo.mutate({ id: todo.id, completed: e.target.checked })
        }
      />
      {todo.title}
    </label>
  )
}
```

### 6. Dependent Queries

```typescript
function UserSettings({ userId }) {
  // First query - get user
  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then((r) => r.json()),
    enabled: !!userId, // Only run if userId exists
  })

  // Second query - depends on first query's data
  const { data: settings } = useQuery({
    queryKey: ['user-settings', user?.id],
    queryFn: () => fetch(`/api/users/${user.id}/settings`).then((r) => r.json()),
    enabled: !!user, // Only run if user exists
  })

  if (!user || !settings) return <div>Loading...</div>
  return <div>{settings.theme}</div>
}
```

### 7. Infinite Queries (Pagination)

```typescript
import { useInfiniteQuery } from '@tanstack/react-query'

function PaginatedTodos() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['todos', 'infinite'],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await fetch(`/api/todos?page=${pageParam}`)
      return response.json()
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })

  return (
    <div>
      {data?.pages.map((page) => (
        <div key={page.cursor}>
          {page.todos.map((todo) => (
            <div key={todo.id}>{todo.title}</div>
          ))}
        </div>
      ))}
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? 'Loading more...' : 'Load more'}
        </button>
      )}
    </div>
  )
}
```

## Next.js Server Actions Integration

TanStack Query pairs with Server Actions for type-safe data fetching:

```typescript
// app/actions.ts
'use server'

export async function getTodos() {
  const todos = await db.todo.findMany()
  return todos
}

export async function createTodo(text: string) {
  const todo = await db.todo.create({ data: { text } })
  revalidatePath('/')
  return todo
}

// components/TodoList.tsx
'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { getTodos, createTodo } from '@/app/actions'

function TodoList() {
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: () => getTodos(),
  })

  const mutation = useMutation({
    mutationFn: createTodo,
    onSuccess: () => {
      // No need to invalidate - revalidatePath handles it
      // Or manually: queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  // ...
}
```

## Performance Best Practices

### 1. Appropriate staleTime

```typescript
// Data that changes rarely (user profile, settings)
useQuery({
  staleTime: 1000 * 60 * 30, // 30 minutes
  queryKey: ['user'],
  queryFn: fetchUser,
})

// Data that changes frequently (notifications, live data)
useQuery({
  staleTime: 0, // Always consider stale
  refetchInterval: 1000 * 30, // Refetch every 30 seconds
  queryKey: ['notifications'],
  queryFn: fetchNotifications,
})
```

### 2. Selectors for Derived Data

```typescript
const { completedTodos } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data) => data.filter((t) => t.completed),
})
```

### 3. Prevent Unnecessary Refetches

```typescript
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  refetchOnWindowFocus: false, // Don't refetch on tab switch
  refetchOnMount: false, // Don't refetch if already in cache
  refetchOnReconnect: false, // Don't refetch on reconnect
})
```

## Code Standards

### Query Key Convention

```typescript
// ✅ Hierarchical keys
['todos']                    // All todos
['todos', { status: 'done' }] // Filtered todos
['todo', id]                 // Single todo
['user', userId]             // User by ID
['user', userId, 'settings'] // User settings

// ❌ Avoid flat keys without hierarchy
['allTodos']
['userSettings']
```

### Naming Conventions

```typescript
// Query functions: noun + verb
fetchTodos
getUser
getSettings

// Mutation functions: verb + noun
createTodo
updateUser
deletePost
```

## Common Pitfalls

### Pitfall 1: Not Using Query Keys for Invalidation

**Symptom:** Cache doesn't update after mutations.

**Solution:** Always use consistent query keys and invalidate them.

### Pitfall 2: Fetching in useEffect Instead of useQuery

**Symptom:** Duplicate requests, race conditions, no caching.

**Solution:** Always use useQuery for server data fetching.

### Pitfall 3: Over-fetching with No staleTime

**Symptom:** Excessive API calls on every component mount.

**Solution:** Set appropriate staleTime based on data volatility.

### Pitfall 4: Not Handling Loading/Error States

**Symptom:** Broken UI during fetch, poor UX.

**Solution:** Always handle isLoading, isError, and error states.

## When to Use Context7

For advanced scenarios:
- Complex cache invalidation strategies
- Query cancellation patterns
- Hydration/dehydration patterns for SSR
- WebSocket integration for real-time updates

Query `/websites/tanstack_query` for v5 documentation.

---

**Activation Trigger:** Use this skill when:
- Implementing server state management
- Fetching and caching API data
- Handling loading/error states
- Managing cache invalidation
- Integrating with Next.js App Router
