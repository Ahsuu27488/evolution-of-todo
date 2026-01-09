# Data Model: Frontend Infrastructure Stabilization

**Feature**: 001-frontend-infra
**Phase**: Phase 1 (Design & Contracts)

## Overview

This document describes the data model for the unified API client and related authentication structures. The focus is on frontend-only changes; backend models remain unchanged.

## Core Entities

### 1. Unified API Client

**Purpose**: Single source of truth for all backend HTTP communication

**Location**: `frontend/lib/api-client.ts`

**Responsibilities**:
- Authenticate requests using JWT from Better Auth session
- Handle errors with Result<T> pattern
- Implement retry logic for transient failures
- Provide typed methods for all backend endpoints

**Key Methods**:

| Method | Input | Output | Notes |
|--------|-------|--------|-------|
| `getAuthToken()` | - | `Promise<string \| null>` | Calls `/api/auth/token` |
| `getTasks()` | filters | `Promise<Result<TaskList>>` | No userId (inferred from token) |
| `getTask(id)` | taskId | `Promise<Result<Task>>` | - |
| `createTask(data)` | TaskCreate | `Promise<Result<Task>>` | - |
| `updateTask(id, data)` | taskId, TaskUpdate | `Promise<Result<Task>>` | - |
| `deleteTask(id)` | taskId | `Promise<Result<void>>` | - |
| `toggleTaskComplete(id)` | taskId | `Promise<Result<Task>>` | PATCH to /complete endpoint |
| `searchTasks(query)` | search string | `Promise<Result<TaskList>>` | - |
| `getTaskLogs(id)` | taskId | `Promise<Result<TaskLog[]>>` | Audit trail |
| `healthCheck()` | - | `Promise<Result<HealthStatus>>` | Uses `/api/health` |

### 2. Authentication Token Endpoint

**Purpose**: Expose JWT from Better Auth session for API client use

**Location**: `frontend/app/api/auth/token/route.ts`

**Request**:
```http
GET /api/auth/token
Cookie: better-auth.session_token=<session_token>
```

**Success Response** (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response** (401):
```json
{
  "error": "No active session"
}
```

### 3. Result Type

**Purpose**: Type-safe error handling without exceptions

**Location**: `frontend/lib/errors.ts` (KEEP, no changes)

**Definition**:
```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }
```

**Helper Functions**:
- `ok<T>(data: T): Result<T>` - Create success result
- `err<E extends AppError>(error: E): Result<never, E>` - Create error result

### 4. API Error

**Purpose**: Structured error information with context

**Location**: `frontend/lib/errors.ts` (KEEP, no changes)

**Properties**:
| Property | Type | Description |
|----------|------|-------------|
| `code` | ErrorCode | Categorical error code |
| `statusCode` | number | HTTP status code |
| `endpoint` | string | API endpoint that failed |
| `method` | string | HTTP method used |
| `requestId` | string | Tracking ID for debugging |
| `message` | string | Human-readable error message |
| `timestamp` | Date | When the error occurred |

**Error Codes**:
```typescript
const ErrorCode = {
  // Authentication
  UNAUTHORIZED: "UNAUTHORIZED",
  SESSION_EXPIRED: "SESSION_EXPIRED",
  INVALID_CREDENTIALS: "INVALID_CREDENTIALS",

  // Authorization
  FORBIDDEN: "FORBIDDEN",
  NOT_OWNER: "NOT_OWNER",

  // Resources
  NOT_FOUND: "NOT_FOUND",
  ALREADY_EXISTS: "ALREADY_EXISTS",

  // Validation
  VALIDATION_ERROR: "VALIDATION_ERROR",
  INVALID_INPUT: "INVALID_INPUT",

  // Server
  SERVER_ERROR: "SERVER_ERROR",
  SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",

  // Network
  NETWORK_ERROR: "NETWORK_ERROR",
  TIMEOUT: "TIMEOUT",
  CONNECTION_REFUSED: "CONNECTION_REFUSED",

  // Unknown
  UNKNOWN: "UNKNOWN",
}
```

## State Transitions

### Authentication Flow

```
┌─────────┐     ┌──────────────┐     ┌─────────┐
│  User   │────▶│ Better Auth  │────▶│ Backend │
│ Browser │     │   Session    │     │   API   │
└─────────┘     └──────────────┘     └─────────┘
                      │
                      ▼
              ┌──────────────┐
              │ /api/auth/   │
              │    token      │
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  JWT Token   │
              │ (Bearer Auth) │
              └──────────────┘
```

1. User signs in via Better Auth → Session cookie set
2. Frontend needs to call backend API → Fetch JWT from `/api/auth/token`
3. Backend API validates JWT → Returns data

### API Request Flow with Retry

```
┌──────────┐     ┌────────────┐     ┌──────────┐
│  Client  │────▶│ API Client │────▶│ Backend  │
│  Code    │     │            │     │   API    │
└──────────┘     └────────────┘     └──────────┘
                      │
                      │ 4xx (except 408)
                      │ or timeout
                      ▼
              ┌────────────┐
              │   Retry    │
              │ (exponential│
              │  backoff)  │
              └────────────┘
                      │
                      ▼
                  Max retries
                      │
                      ▼
              ┌────────────┐
              │  Return    │
              │  Result<T> │
              └────────────┘
```

## Type Definitions

### Task Types (from backend contract)

```typescript
interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  completed: boolean
  tags: Array<{ name: string; color: string }>
  due_date: string | null
  recurrence_pattern: 'DAILY' | 'WEEKLY' | 'MONTHLY' | null
  transcription_text: string | null
  ai_summary: string | null
  embedding_id: string | null
  created_at: string
  updated_at: string
}

interface TaskCreate {
  title: string
  description?: string
  priority?: 'HIGH' | 'MEDIUM' | 'LOW'
  tags?: Array<{ name: string; color: string }>
  due_date?: string
  recurrence_pattern?: 'DAILY' | 'WEEKLY' | 'MONTHLY'
}

interface TaskUpdate {
  title?: string
  description?: string
  priority?: 'HIGH' | 'MEDIUM' | 'LOW'
  completed?: boolean
  tags?: Array<{ name: string; color: string }>
  due_date?: string
}

interface TaskList {
  tasks: Task[]
  total: number
  page: number
  per_page: number
}

interface TaskLog {
  id: number
  task_id: number
  user_id: string
  action: string
  changed_fields: Record<string, unknown>
  created_at: string
}
```

### User Types

```typescript
interface User {
  id: string
  email: string
  name: string | null
  created_at: string | null
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}
```

## Relationships

```
┌─────────────┐
│   User      │
│  (from API) │
└──────┬──────┘
       │ 1
       │ has
       │
┌──────▼──────┐     ┌─────────────┐
│    Task     │────▶│  TaskLog    │
│             │     │  (audit)    │
└─────────────┘     └─────────────┘
     │
     │ 0..*
     │
┌─────▼──────┐
│    Tag     │
│  (optional)│
└────────────┘
```

## Validation Rules

| Entity | Field | Rule | Source |
|--------|-------|------|--------|
| Task | title | Required, min length 1 | Backend |
| Task | priority | Optional, enum HIGH/MEDIUM/LOW | Backend |
| Task | completed | Boolean | Backend |
| User | email | Required, valid email format | Backend |
| User | password (create) | Required, min 8 chars | Backend |

## State Management

### Client State (TanStack Query)
- **Query Cache**: Tasks, user session
- **Mutation Cache**: Invalidates related queries on success
- **Offline Support**: None in Phase II (planned for later)

### Server State
- **Session**: Better Auth session in httpOnly cookie
- **Database**: PostgreSQL (Neon) managed by backend

---

**Status**: ✅ Ready for implementation

**Next Phase**: `/sp.tasks` to generate work units
