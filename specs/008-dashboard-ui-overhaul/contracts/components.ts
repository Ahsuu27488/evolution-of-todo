# Component Contracts: Advanced Dashboard UI Overhaul

**Feature**: 008-dashboard-ui-overhaul
**Date**: 2026-01-10

## Overview

This document defines the contracts (props, events, behavior) for all components to be created or modified in this feature.

## New Components

### DashboardToolbar

**Purpose**: Replace basic header with comprehensive search, filter, and sort controls.

**Location**: `frontend/components/dashboard/dashboard-toolbar.tsx`

#### Props

```typescript
interface DashboardToolbarProps {
  // Search
  searchQuery: string
  onSearchChange: (query: string) => void

  // Filters
  statusFilter: FilterState['status']
  onStatusChange: (status: FilterState['status']) => void
  priorityFilter: FilterState['priority']
  onPriorityChange: (priority: FilterState['priority']) => void

  // Sort
  sortBy: FilterState['sortBy']
  onSortChange: (sortBy: FilterState['sortBy']) => void
  sortOrder: FilterState['sortOrder']
  onSortOrderToggle: () => void

  // Task counts for display
  totalCount?: number
  pendingCount?: number
  completedCount?: number
}
```

#### Behavior Contract

| User Action | Component Behavior | Expected Side Effect |
|-------------|-------------------|---------------------|
| Type in search input | Debounce 300ms, then call `onSearchChange` | Filtered tasks update |
| Click status tab | Call `onStatusChange` immediately | Tasks refetch with new filter |
| Select priority | Call `onPriorityChange` immediately | Tasks refetch with new filter |
| Select sort criterion | Call `onSortChange` immediately | Tasks reorder |
| Click sort toggle | Call `onSortOrderToggle` | Tasks reverse order |

#### Glassmorphism Requirements

- Search input: `.glass` with `.glass-strong` on focus
- Dropdowns: `.glass-strong` background
- Tabs: Semi-transparent with active state glow
- Responsive: Stack vertically on mobile (< 640px)

---

### TagInput

**Purpose**: Allow users to add/remove colored tags for tasks.

**Location**: `frontend/components/tags/tag-input.tsx`

#### Props

```typescript
interface TagInputProps {
  value: Tag[]
  onChange: (tags: Tag[]) => void
  placeholder?: string
  maxTags?: number
  disabled?: boolean
  id?: string
}
```

#### Behavior Contract

| User Action | Component Behavior | Expected Side Effect |
|-------------|-------------------|---------------------|
| Type tag name and press Enter | Add tag with random color | `onChange` called with new tags array |
| Click × on tag chip | Remove that tag | `onChange` called with tag removed |
| Type existing tag name | Prevent duplicate (show toast) | No change to tags |
| Try to add > maxTags | Prevent addition (show toast) | No change to tags |

#### Color Generation

Predefined color palette (matches Deep Space theme):
- Cyan: `#00f5ff`
- Purple: `#a855f7`
- Green: `#22c55e`
- Yellow: `#eab308`
- Pink: `#ec4899`
- Orange: `#f97316`

---

### DueDatePicker

**Purpose**: Styled datetime-local input for task due dates.

**Location**: `frontend/components/tasks/due-date-picker.tsx`

#### Props

```typescript
interface DueDatePickerProps {
  value: string | null  // ISO 8601
  onChange: (date: string | null) => void
  min?: string           // ISO 8601
  disabled?: boolean
  required?: boolean
  label?: string
}
```

#### Behavior Contract

| User Action | Component Behavior | Expected Side Effect |
|-------------|-------------------|---------------------|
| Select date/time | Format to ISO 8601, call `onChange` | Task due_date updated |
| Clear date | Call `onChange(null)` | Task due_date removed |
| Select past date | Allow (for overdue tasks) | Task marked overdue on display |

---

### SortDropdown

**Purpose**: Dropdown to select sort criterion with icon indicating direction.

**Location**: `frontend/components/dashboard/sort-dropdown.tsx`

#### Props

```typescript
interface SortDropdownProps {
  value: FilterState['sortBy']
  order: FilterState['sortOrder']
  onSortChange: (sortBy: FilterState['sortBy']) => void
  onOrderToggle: () => void
}
```

#### Sort Options Mapping

| Value | Label | Icon | Description |
|-------|-------|------|-------------|
| `created_at` | Created Date | Calendar + clock | Sort by creation time |
| `due_date` | Due Date | Calendar | Sort by deadline (nulls last) |
| `priority` | Priority | Flag | Sort by urgency |
| `title` | Title | A-Z | Sort alphabetically |

---

## Modified Components

### TaskForm

**Location**: `frontend/components/tasks/task-form.tsx`

#### New Props (No change - existing props sufficient)

#### New Fields to Add

| Field | Type | Component | Validation |
|-------|------|-----------|------------|
| `due_date` | `string \| null` | DueDatePicker | Optional |
| `tags` | `Tag[]` | TagInput | Optional, max 10 |
| `recurrence_pattern` | `RecurrencePattern` | Select (shadcn) | Optional |

#### Updated Submit Behavior

```typescript
interface TaskCreateInput {
  title: string
  description?: string
  priority?: Priority
  due_date?: string        // NEW
  tags?: Tag[]            // NEW
  recurrence_pattern?: RecurrencePattern  // NEW
}
```

---

### TaskCard

**Location**: `frontend/components/tasks/task-card.tsx`

#### New Display Elements

| Element | Condition | Rendering |
|---------|-----------|------------|
| Due date | `due_date != null` | Format: "Jan 15, 2026 5:00 PM" |
| Overdue badge | `due_date < now && !completed` | Red glow, "Overdue:" prefix |
| Due soon badge | `due_date < now + 24h && !completed` | Orange warning |
| Tags | `tags.length > 0` | Colored pills using tag.color |
| Recurrence icon | `recurrence_pattern != null` | Repeat icon with tooltip |

#### Due Date Color Logic

```typescript
function getDueDateColor(dueDate: string, completed: boolean): string {
  if (completed) return "text-muted-foreground"
  if (new Date(dueDate) < new Date()) return "text-destructive"  // Overdue
  if (new Date(dueDate) < new Date(Date.now() + 86400000)) return "text-orange-500"  // Due soon
  return "text-muted-foreground"
}
```

---

### DashboardContent

**Location**: `frontend/components/dashboard/dashboard-content.tsx`

#### Structural Changes

**Before**:
```
Header (text only)
├── Title
└── Task count
Task List
```

**After**:
```
DashboardToolbar (NEW)
├── Search bar
├── Status tabs (All/Pending/Completed)
├── Priority dropdown
├── Sort dropdown
└── Sort toggle
Task List (unchanged)
```

#### New Props (from store)

```typescript
interface DashboardContentProps extends DashboardToolbarProps {
  tasks: Task[]
  isLoading?: boolean
  isAuthenticated: boolean
}
```

---

## Event Flow Contracts

### Task Creation Flow

```
┌─────────────┐
│  TaskForm   │
└──────┬──────┘
       │ onSubmit(data: TaskCreateInput)
       ▼
┌─────────────────────┐
│  createTask()       │  Server Action
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  api.createTask()   │
└──────┬──────────────┘
       │ result: Result<Task>
       ▼
┌─────────────────────┐
│  TanStack Query     │  invalidateQueries(['tasks'])
│  Cache Invalidation │
       │
       ▼
┌─────────────────────┐
│  UI Update          │  Toast + List refresh
└─────────────────────┘
```

### Filter Change Flow

```
┌─────────────────────┐
│ DashboardToolbar    │
│ (Filter Button)      │
└──────┬──────────────┘
       │ onClick
       ▼
┌─────────────────────┐
│ ui-store            │
│ setFilterStatus()   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ useTasks Hook       │  Reacts to filter state
│ (useQuery)          │
       │
       ▼
┌─────────────────────┐
│ api.getTasks()      │  With filter params
└─────────────────────┘
```

### Search Flow

```
┌─────────────────────┐
│ Search Input        │
│ (debounced 300ms)   │
└──────┬──────────────┘
       │ onSearchChange
       ▼
┌─────────────────────┐
│ Component State     │  setSearchQuery()
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ useEffect           │  Watch searchQuery
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ api.searchTasks()   │  OR filter locally
└─────────────────────┘
```

---

## Responsive Breakpoints

| Component | Mobile (< 640px) | Tablet (640-1024px) | Desktop (> 1024px) |
|-----------|-------------------|---------------------|-------------------|
| DashboardToolbar | Stacked vertical | 2 rows | Single row |
| Search bar | Full width | 50% | 300px fixed |
| Filter tabs | Scrollable horizontal | Full width | Full width |
| TagInput | Full width | Full width | Inline with form |
| TaskCard | Single column | Single column | Single column |

---

## Animation Contracts

### Task List Entry

```typescript
const staggerList = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,  // 50ms per item
      delayChildren: 0.1,      // 100ms initial delay
    }
  }
}

const taskItem = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1 }
}
```

### Filter Transition

```typescript
// Smooth fade when filter changes
const filterTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.3
}
```

### Completion Glow

```typescript
const completionGlow = {
  glow: {
    boxShadow: "0 0 20px rgba(0, 245, 255, 0.5)",
    borderColor: "rgb(0 245 255)"
  },
  normal: {
    boxShadow: "none",
    borderColor: "transparent"
  }
}
```
