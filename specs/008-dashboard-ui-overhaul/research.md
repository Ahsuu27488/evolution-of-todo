# Research: Advanced Dashboard UI Overhaul

**Feature**: 008-dashboard-ui-overhaul
**Date**: 2026-01-10
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technical decisions for implementing the Advanced Dashboard UI Overhaul. The goal is to transform the dashboard into a high-fidelity "Deep Space" glassmorphism interface matching the landing page, while implementing missing UI controls for advanced features (due dates, tags, recurrence, search, filter, sort).

## Technology Stack (Actual Versions)

| Technology | Version | Source |
|------------|---------|--------|
| Next.js | 15.2.8 | package.json |
| React | 19.2.3 | package.json |
| Framer Motion | 12.24.7 | package.json |
| TanStack Query | 5.90.16 | package.json |
| Zustand | 5.0.9 | package.json |
| Tailwind CSS | 4.x | package.json |
| shadcn/ui | Radix components | package.json |

## Research Findings

### 1. Staggered List Animations with Framer Motion

**Decision**: Use Framer Motion's `staggerChildren` variant pattern for task list animations.

**Rationale**:
- Already used in the project (see `lib/animations.ts`)
- Provides smooth cascading entry animations
- Clean declarative API with variants
- Zero additional dependencies

**Implementation Pattern** (from Context7):
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,  // 50ms delay between items
      delayChildren: 0.1,      // Initial delay
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

// Usage
<motion.ul variants={container} initial="hidden" animate="show">
  {items.map((item) => (
    <motion.li key={item.id} variants={item}>
      {item.content}
    </motion.li>
  ))}
</motion.ul>
```

**Alternatives Considered**:
- CSS animations with delays: Less flexible, harder to maintain
- Manual setTimeout: Imperative, not declarative
- React Spring: Additional dependency, Framer Motion already installed

### 2. Debounced Search Input

**Decision**: Implement custom debounce hook using React's `setTimeout` and `useEffect`.

**Rationale**:
- Simple implementation, no additional dependencies
- Full control over delay duration
- Easy to test and debug

**Implementation Pattern**:
```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// Usage in search component
const [searchTerm, setSearchTerm] = useState("")
const debouncedSearch = useDebounce(searchTerm, 300)

useEffect(() => {
  if (debouncedSearch) {
    api.searchTasks(debouncedSearch)
  }
}, [debouncedSearch])
```

**Alternatives Considered**:
- lodash.debounce: Additional 24KB minified
- react-use's useDebounce: Would require new dependency

### 3. Tag Input Management

**Decision**: Build custom tag input using keyboard event handlers and state management.

**Rationale**:
- Full control over UX (Enter to add, click × to remove)
- Can integrate color picker if needed
- Matches existing glassmorphism aesthetic

**Implementation Pattern**:
```tsx
const [tags, setTags] = useState<Tag[]>([])
const [inputValue, setInputValue] = useState("")

const addTag = () => {
  if (inputValue && !tags.find(t => t.name === inputValue)) {
    const color = getRandomColor() // or user-selected
    setTags([...tags, { name: inputValue, color }])
    setInputValue("")
  }
}

const removeTag = (name: string) => {
  setTags(tags.filter(t => t.name !== name))
}

// Handle Enter key
onKeyDown={(e) => {
  if (e.key === "Enter") {
    e.preventDefault()
    addTag()
  }
}}
```

### 4. Date/Time Picker Component

**Decision**: Use native HTML `datetime-local` input styled with Tailwind, enhanced with shadcn/ui popover if needed.

**Rationale**:
- Native browser support, no additional dependencies
- Consistent behavior across platforms
- Can be styled to match glassmorphism theme

**Alternatives Considered**:
- react-datepicker: Additional 60KB dependency, may conflict with dark theme
- @radix-ui/react-calendar: Would need to build custom datetime picker

### 5. Filter/Sort State Management

**Decision**: Use existing Zustand store (`lib/stores/ui-store.ts`) which already has FilterState infrastructure.

**Rationale**:
- Already implemented with persistence
- Type-safe with TypeScript
- Minimal changes needed

**Existing FilterState Structure** (from ui-store.ts):
```tsx
export interface FilterState {
  status: 'all' | 'pending' | 'completed'
  priority: 'all' | 'HIGH' | 'MEDIUM' | 'LOW'
  sortBy: 'created_at' | 'due_date' | 'priority' | 'title'
  sortOrder: 'asc' | 'desc'
  tag?: string
}
```

### 6. API Integration Patterns

**Decision**: Use existing `api-client.ts` methods with TanStack Query for data fetching.

**Available Methods** (from api-client.ts):
- `getTasks(filters?)` - Supports status, priority filters
- `searchTasks(query)` - Full-text search
- `createTask(data)` - Creates with tags, due_date, recurrence_pattern
- `updateTask(id, data)` - Updates all fields
- `deleteTask(id)` - Removes task
- `toggleTaskComplete(id)` - Flips completion status

**Rationale**: All required functionality already exists, zero backend changes needed.

### 7. Glassmorphism Design Tokens

**Decision**: Use existing CSS utilities from `globals.css`.

**Available Utilities** (from globals.css):
```css
.glass         /* Standard glass effect */
.glass-strong  /* Stronger blur for modals */
.glass-modal   /* Heavy blur with shadows */
.glow-cyan     /* Cyan neon glow */
.glow-purple   /* Purple neon glow */
.glow-green    /* Green success glow */
```

**Design Tokens** (from globals.css):
```css
--color-primary: oklch(0.91 0.17 195)     /* Neon Cyan #00f5ff */
--color-secondary: oklch(0.65 0.26 293)   /* Neon Purple #a855f7 */
--color-destructive: oklch(0.60 0.25 25)  /* Red #ef4444 */
--color-background: oklch(0.08 0.01 270) /* Deep space black */
```

## Implementation Approach Summary

1. **Component Structure**:
   - Update `TaskForm` with new fields (due_date, tags, recurrence)
   - Create new `DashboardToolbar` component
   - Enhance `TaskCard` with new attribute displays
   - Update `dashboard-content.tsx` for new layout

2. **State Management**:
   - Use existing `ui-store.ts` FilterState
   - Add search query state (or reuse ui-store)

3. **Data Layer**:
   - Use existing `api-client.ts` methods
   - TanStack Query for fetching/mutations
   - Optimistic updates for better UX

4. **Styling**:
   - Reuse existing glassmorphism utilities
   - Match hero section animations (fadeInUp variants)
   - Maintain mobile responsiveness

## No NEEDS CLARIFICATION Items

All technical decisions are clear based on:
- Existing codebase analysis
- Package.json dependency versions
- Context7 documentation research
- Existing design tokens in globals.css

## Next Steps

1. Create `data-model.md` documenting Task and FilterState entities
2. Create component contracts in `/contracts/` directory
3. Create `quickstart.md` for development setup
4. Update agent context with new technologies
