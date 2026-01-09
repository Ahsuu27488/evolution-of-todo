---
name: zustand-guide
description: Fetch Zustand documentation and apply state management patterns. Use when creating stores, implementing TypeScript with selectors, using the slices pattern, adding middleware (persist, devtools), or optimizing re-render performance. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Zustand Mastery Guide

## Theoretical Foundation

Zustand is a **minimalist state management solution** for React that avoids boilerplate through:
- **Hook-based API**: No providers or context wrapping required
- **Atomic selectors**: Subscribe to specific state slices to prevent unnecessary re-renders
- **Middleware system**: Composable middleware for persistence, devtools, etc.
- **Immutability by default**: Uses `immer`-like patterns (but not required)

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  REDUX                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Action Creators ──► Dispatch ──► Reducers ──► Store ──► useSelector       │
│  (boilerplate)       (verbose)      (immutable)                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                 ZUSTAND                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Store.create() ──► useStore(selector) ──► Component                       │
│  (single file)       (fine-grained)           (auto-subscribe)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Patterns

### 1. Basic Store with TypeScript

```typescript
import { create } from 'zustand'

// Separate state and actions for better typing
type State = {
  count: number
  bears: number
}

type Actions = {
  increment: (qty: number) => void
  decrement: (qty: number) => void
  addBear: () => void
}

type BearStore = State & Actions

export const useBearStore = create<BearStore>((set) => ({
  // State
  count: 0,
  bears: 0,

  // Actions
  increment: (qty) => set((state) => ({ count: state.count + qty })),
  decrement: (qty) => set((state) => ({ count: state.count - qty })),
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
}))
```

### 2. Selector Pattern (Render Optimization)

**CRITICAL:** Always use selectors to prevent unnecessary re-renders.

```typescript
// ❌ BAD: Subscribes to entire store (re-renders on ANY change)
const Component = () => {
  const store = useBearStore()
  return <div>{store.count}</div>
}

// ✅ GOOD: Subscribes only to count (re-renders only when count changes)
const Component = () => {
  const count = useBearStore((state) => state.count)
  return <div>{count}</div>
}

// ✅ BEST: Multiple fine-grained selectors
const Component = () => {
  const count = useBearStore((state) => state.count)
  const increment = useBearStore((state) => state.increment)
  return <div onClick={increment}>{count}</div>
}
```

### 3. Slices Pattern for Large Stores

Split stores into manageable slices:

```typescript
// slices/bearSlice.ts
import { StateCreator } from 'zustand'

export type BearSlice = {
  bears: number
  addBear: () => void
  removeBear: () => void
}

export const createBearSlice: StateCreator<
  BearSlice,
  [],
  [],
  BearSlice
> = (set) => ({
  bears: 0,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
  removeBear: () => set((state) => ({ bears: Math.max(0, state.bears - 1) })),
})

// slices/fishSlice.ts
export type FishSlice = {
  fishes: number
  addFish: () => void
}

export const createFishSlice: StateCreator<
  FishSlice,
  [],
  [],
  FishSlice
> = (set) => ({
  fishes: 0,
  addFish: () => set((state) => ({ fishes: state.fishes + 1 })),
})

// store/index.ts - Combined store
import { create } from 'zustand'
import { createBearSlice, BearSlice } from './slices/bearSlice'
import { createFishSlice, FishSlice } from './slices/fishSlice'

type CombinedStore = BearSlice & FishSlice

export const useBoundStore = create<CombinedStore>((...a) => ({
  ...createBearSlice(...a),
  ...createFishSlice(...a),
}))
```

### 4. Middleware: Devtools + Persist

```typescript
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface BearState {
  bears: number
  increase: (by: number) => void
}

export const useBearStore = create<BearState>()(
  devtools(
    persist(
      (set) => ({
        bears: 0,
        increase: (by) => set((state) => ({ bears: state.bears + by })),
      }),
      {
        name: 'bear-storage', // localStorage key
        partialize: (state) => ({ bears: state.bears }), // Persist only bears
      }
    ),
    { name: 'BearStore' } // DevTools name
  )
)
```

### 5. Async Actions with Loading States

```typescript
interface TodoState {
  todos: string[]
  loading: boolean
  error: string | null
  fetchTodos: () => Promise<void>
  addTodo: (text: string) => Promise<void>
}

export const useTodoStore = create<TodoState>()((set, get) => ({
  todos: [],
  loading: false,
  error: null,

  fetchTodos: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/todos')
      const todos = await response.json()
      set({ todos, loading: false })
    } catch (error) {
      set({ error: (error as Error).message, loading: false })
    }
  },

  addTodo: async (text) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify({ text }),
      })
      const newTodo = await response.json()
      set((state) => ({
        todos: [...state.todos, newTodo],
        loading: false,
      }))
    } catch (error) {
      set({ error: (error as Error).message, loading: false })
    }
  },
}))
```

## Common UI State Patterns

### Modal State

```typescript
interface ModalState {
  isOpen: boolean
  modalType: 'login' | 'signup' | 'settings' | null
  openModal: (type: ModalState['modalType']) => void
  closeModal: () => void
}

export const useModalStore = create<ModalState>()((set) => ({
  isOpen: false,
  modalType: null,

  openModal: (modalType) => set({ isOpen: true, modalType }),
  closeModal: () => set({ isOpen: false, modalType: null }),
}))

// Usage
const Modal = () => {
  const { isOpen, modalType, closeModal } = useModalStore(
    (state) => ({
      isOpen: state.isOpen,
      modalType: state.modalType,
      closeModal: state.closeModal,
    })
  )

  if (!isOpen) return null
  return <div>{modalType} modal content</div>
}
```

### Filter State

```typescript
interface FilterState {
  filters: {
    status: 'all' | 'active' | 'completed'
    search: string
    sortBy: 'date' | 'name' | 'priority'
  }
  setFilter: <K extends keyof FilterState['filters']>(
    key: K,
    value: FilterState['filters'][K]
  ) => void
  resetFilters: () => void
}

export const useFilterStore = create<FilterState>()((set) => ({
  filters: {
    status: 'all',
    search: '',
    sortBy: 'date',
  },

  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),

  resetFilters: () =>
    set({
      filters: {
        status: 'all',
        search: '',
        sortBy: 'date',
      },
    }),
}))
```

### Toast Notification State

```typescript
export type Toast = {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

interface ToastState {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
}

export const useToastStore = create<ToastState>()((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = Math.random().toString(36).substring(7)
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }))

    // Auto-remove after duration
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }))
    }, toast.duration || 3000)
  },

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}))
```

## Performance Best Practices

### 1. Shallow Comparison for Objects

```typescript
import { shallow } from 'zustand/shallow'

// ❌ BAD: Creates new object on every render
const { bears, fishes } = useBearStore((state) => ({
  bears: state.bears,
  fishes: state.fishes,
}))

// ✅ GOOD: Uses shallow comparison
const { bears, fishes } = useBearStore(
  (state) => ({ bears: state.bears, fishes: state.fishes }),
  shallow
)
```

### 2. Action Selectors (Stable References)

```typescript
// Actions are stable references - won't cause re-renders
const addTodo = useTodoStore((state) => state.addTodo)
const removeTodo = useTodoStore((state) => state.removeTodo)
```

## Code Standards

### Store File Organization

```
stores/
├── index.ts          # Export all stores
├── useTodoStore.ts   # Individual store file
├── slices/
│   ├── filterSlice.ts
│   └── uiSlice.ts
└── types.ts          # Shared types
```

### Naming Conventions

```typescript
// ✅ Store name: use + PascalCase + Store
useBearStore
useTodoStore
useModalStore

// ✅ State: lowercase
bears
todos
isOpen

// ✅ Actions: verb + noun
addBear
fetchTodos
openModal
```

## Common Pitfalls

### Pitfall 1: Subscribing to Entire Store

**Symptom:** Component re-renders on every state change.

**Solution:** Use selectors to subscribe only to needed state.

### Pitfall 2: Mutating State Directly

**Symptom:** State changes don't trigger re-renders.

**Solution:** Always use `set()` function. Zustand enforces immutability.

### Pitfall 3: Middleware on Slices

**Symptom:** Persistence or devtools not working with slices pattern.

**Solution:** Apply middleware to the combined store, not individual slices.

### Pitfall 4: Async Actions Without Error Handling

**Symptom:** Unhandled promise rejections, broken UI state.

**Solution:** Always wrap async actions in try/catch and update error state.

## When to Use Context7

For advanced scenarios:
- Middleware composition patterns
- TypeScript complex types with generics
- Store testing patterns
- Zustand v5 features (computed state, subscribe selectors)

Query `/pmndrs/zustand` for official documentation.

---

**Activation Trigger:** Use this skill when:
- Managing UI state (modals, filters, toasts)
- Creating state stores with TypeScript
- Implementing the slices pattern
- Adding persistence or devtools
- Optimizing component re-renders
