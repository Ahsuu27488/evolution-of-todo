# Data Model: Advanced Dashboard UI Overhaul

**Feature**: 008-dashboard-ui-overhaul
**Date**: 2026-01-10
**Source**: [spec.md](spec.md), [research.md](research.md)

## Overview

This document describes the data entities used in the Advanced Dashboard UI Overhaul. The frontend data types match the backend schema from Phase II, with all advanced features (due dates, tags, recurrence) already pre-provisioned.

## Core Entities

### Task

Represents a todo item with advanced attributes for comprehensive task management.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | `number` | ✅ | Unique task identifier | `42` |
| `user_id` | `string` | ✅ | Owner's user identifier (from JWT) | `"user_123"` |
| `title` | `string` | ✅ | Task title/name | `"Complete project report"` |
| `description` | `string \| null` | ❌ | Optional detailed description | `"Include Q4 metrics"` |
| `priority` | `Priority` | ✅ | Task urgency level | `"HIGH" \| "MEDIUM" \| "LOW"` |
| `completed` | `boolean` | ✅ | Completion status | `false` |
| `tags` | `Tag[]` | ❌ | Associated category labels | `[{name: "work", color: "#00f5ff"}]` |
| `due_date` | `string \| null` | ❌ | ISO 8601 datetime | `"2026-01-15T17:00:00Z"` |
| `recurrence_pattern` | `RecurrencePattern \| null` | ❌ | Recurrence setting | `"DAILY" \| "WEEKLY" \| "MONTHLY" \| null` |
| `created_at` | `string` | ✅ | Creation timestamp (ISO 8601) | `"2026-01-10T08:00:00Z"` |
| `updated_at` | `string` | ✅ | Last modification timestamp | `"2026-01-10T09:30:00Z"` |

**Phase III Pre-provisioned Fields** (not used in this feature):
- `transcription_text`: `string \| null` - Voice input storage
- `ai_summary`: `string \| null` - LLM-generated summary
- `embedding_id`: `string \| null` - Vector search ID

### Tag

Represents a category label with visual styling.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | `string` | ✅ | Tag identifier/name | `"work"` |
| `color` | `string` | ✅ | Hex color code for display | `"#00f5ff"` |

### FilterState

Represents the current dashboard filter and sort configuration (from ui-store).

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `status` | `'all' \| 'pending' \| 'completed'` | ✅ | `'all'` | Task completion filter |
| `priority` | `'all' \| 'HIGH' \| 'MEDIUM' \| 'LOW'` | ✅ | `'all'` | Priority level filter |
| `sortBy` | `'created_at' \| 'due_date' \| 'priority' \| 'title'` | ✅ | `'created_at'` | Sort criterion |
| `sortOrder` | `'asc' \| 'desc'` | ✅ | `'desc'` | Sort direction |
| `tag` | `string \| undefined` | ❌ | `undefined` | Tag filter (optional) |

## Type Definitions

### Priority Enum

```typescript
type Priority = 'HIGH' | 'MEDIUM' | 'LOW'
```

**Display Mapping**:
- `HIGH` → Red accent, destructive color
- `MEDIUM` → Purple accent, secondary color
- `LOW` → Gray accent, muted-foreground

### RecurrencePattern Enum

```typescript
type RecurrencePattern = 'DAILY' | 'WEEKLY' | 'MONTHLY' | null
```

**Icon Mapping** (for UI display):
- `DAILY` → Calendar with repeat arrows
- `WEEKLY` → Calendar with weekly pattern
- `MONTHLY` → Calendar with monthly pattern

## State Transitions

### Task Completion

```
┌─────────────┐  toggleTaskComplete()  ┌─────────────┐
│  completed  │ ──────────────────────▶ │  completed  │
│   = false   │                         │   = true    │
└─────────────┘                         └─────────────┘
       │                                       │
       │  (toggle again)                       │ (toggle again)
       │                                       │
       ▼                                       ▼
┌─────────────┐  toggleTaskComplete()  ┌─────────────┐
│  completed  │ ◀────────────────────── │  completed  │
│   = true    │                         │   = false   │
└─────────────┘                         └─────────────┘
```

### Recurring Tasks

When a task with `recurrence_pattern` is completed, the backend generates a new task for the next occurrence. The frontend reflects this by invalidating the task list query.

## Validation Rules

### Task Creation

| Field | Validation |
|-------|------------|
| `title` | Required, min 1 character, max 200 |
| `description` | Optional, max 1000 characters |
| `priority` | Required, must be valid Priority value |
| `due_date` | Optional, must be valid ISO 8601 datetime |
| `tags` | Optional, max 10 tags per task, unique tag names |
| `recurrence_pattern` | Optional, must be valid RecurrencePattern or null |

### Tag Names

- Must be 1-30 characters
- Cannot contain special characters `<>{}\\|[]^"`
- Case-sensitive (Work ≠ work)

## Data Flow

### Create Task Flow

```
User Input (Form)
       │
       ▼
TaskCreate DTO
       │
       ▼
api.createTask(data)
       │
       ▼
FastAPI Backend
       │
       ▼
Task (with id, timestamps)
       │
       ▼
TanStack Query Cache Update
       │
       ▼
UI Re-render (optimistic)
```

### Filter/Sort Flow

```
User Changes Filter
       │
       ▼
ui-store.setFilterStatus(priority)
       │
       ▼
Zustand State Update (persisted)
       │
       ▼
Component Re-render
       │
       ▼
Filtered Task List Computed
```

## Relationships

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ has many
       ▼
┌─────────────┐       ┌─────────────┐
│    Task     │───────┤     Tag    │
└─────────────┘ 0..*  └─────────────┘
       │
       │ belongs to
       ▼
┌─────────────┐
│  FilterState│ (transient, UI-only)
└─────────────┘
```

## Persistence

| Entity | Storage | Sync |
|--------|---------|------|
| `Task` | Neon PostgreSQL (via backend API) | TanStack Query |
| `Tag` | Embedded in Task (JSONB) | Via Task |
| `FilterState` | localStorage (Zustand persist) | Zustand |
