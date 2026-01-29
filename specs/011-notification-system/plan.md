# Implementation Plan: Notification System

**Branch**: `011-notification-system` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-notification-system/spec.md`

## Summary

Full-fledged multi-channel notification system with three delivery channels: in-app (SSE real-time), browser push (Web Push API with VAPID), and email (Resend with React templates). Features include notification preferences per channel/type, Do Not Disturb hours, email digest scheduling, and Deep Space glassmorphism UI theming.

**From**: research.md - Technologies selected via Context7 documentation
- Web Push: `web-push` npm library (97.1 benchmark score)
- Email: Resend Node.js SDK with React templates
- Real-time: SSE Starlette for FastAPI (92.4 benchmark score)
- UI: Radix UI DropdownMenu with Badge, Framer Motion animations

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend) per Constitution §V.1.1
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, sse-starlette, web-push, resend
- Frontend: Next.js 15, Radix UI, Framer Motion, TanStack Query
- Email: Resend (React Email templates)

**Storage**: Neon PostgreSQL (PostgreSQL 16+) - existing Phase II database
**Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- In-app notifications: <500ms response (SC-001)
- Push delivery: <10 seconds (SC-002)
- Email delivery: <30 seconds (SC-003)
- Unread badge update: <200ms (SC-005)
- Concurrent deliveries: 10,000 without degradation (SC-011)

**Constraints**:
- Push notifications: 3/hour per user, urgent exempt (FR-020)
- Notification retention: 30 days active, then archive (Assumptions & Decisions)
- Deep Space theme: 100% adherence required (SC-012)

**Scale/Scope**:
- 4 new database tables
- 15+ new API endpoints
- 3 notification channels
- 6 notification types

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Context7 Primary Source Mandate (Constitution §III.1)

**Status**: ✅ COMPLIED

All technical decisions in this plan are based on Context7 documentation:

| Technology | Context7 Source | Documentation Retrieved |
|-------------|------------------|------------------------|
| Web Push | `/web-push-libs/web-push` | VAPID keys, sendNotification, subscription handling |
| Resend Email | `/resend/resend-node` | React templates, webhooks, bounce handling |
| SSE | `/sysid/sse-starlette` | EventSourceResponse, disconnect detection |
| Radix UI | `/radix-ui/website` | DropdownMenu, Badge patterns |

### Phase Isolation (Constitution §IV.1)

**Status**: ✅ COMPLIED

This feature extends **Phase II** (Full-Stack Web) without introducing Phase III+ concepts:

| Allowed | Not Allowed | Status |
|----------|-------------|--------|
| In-app notifications (SSE) | AI chatbot (Phase III) | ✅ OK |
| Browser push (Web Push) | Kubernetes (Phase IV) | ✅ OK |
| Email (Resend) | Kafka/Dapr (Phase V) | ✅ OK |
| PostgreSQL | New database technologies | ✅ OK |

### Spec-Driven Development (Constitution §I)

**Status**: ✅ COMPLIED

- All code will reference Task IDs: `[Task]: T-XXX`
- All code will reference spec sections: `[From]: spec.md §X.X, plan.md §X.X`
- Context7 used as primary source for all external libraries

### Python Version (Constitution §V.1.1)

**Status**: ✅ COMPLIED

- Python 3.13+ required for backend
- TypeScript 5+ for frontend

---

## Project Structure

### Documentation (this feature)

```text
specs/011-notification-system/
├── spec.md              # Feature specification (WHAT)
├── plan.md              # This file (HOW)
├── research.md          # Phase 0: Technology research (Context7-based)
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: API contracts
│   └── api.yaml        # OpenAPI specification
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── notification.py         # New: Notification, NotificationPreference
│   │   ├── push_subscription.py    # New: PushSubscription
│   │   └── email_delivery_log.py   # New: EmailDeliveryLog
│   ├── services/
│   │   ├── notification_service.py # New: Notification creation logic
│   │   ├── push_service.py        # New: Web Push send logic
│   │   ├── email_service.py       # New: Resend email logic
│   │   └── sse_service.py         # New: SSE streaming logic
│   ├── api/
│   │   └── notifications.py        # New: Notification endpoints
│   ├── emails/
│   │   └── task_overdue.tsx        # New: React Email template
│   └── webhooks/
│       └── resend.py              # New: Resend webhook handler
└── tests/
    └── test_notifications.py       # New: API tests

frontend/
├── components/
│   └── notifications/
│       ├── notification-bell.tsx   # New: Bell icon with badge
│       ├── notification-dropdown.tsx # New: Dropdown with notifications
│       ├── notification-item.tsx    # New: Single notification item
│       └── push-permission-modal.tsx # New: Permission request modal
├── hooks/
│   ├── use-notifications.ts       # New: TanStack Query for notifications
│   └── use-notification-stream.ts # New: SSE stream hook
├── lib/
│   └── api-client.ts              # Modified: Add notification endpoints
├── app/
│   └── layout.tsx                 # Modified: Add notification bell to header
└── public/
    └── sw.js                       # New: Service worker for push
```

**Structure Decision**: Web application structure (Option 2) - uses existing `backend/` and `frontend/` directories from Phase II. No new projects created.

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ Notification │  │ Push Permission│  │ SSE Stream Hook    │  │
│  │ Bell/Dropdown│  │ Modal         │  │ (useNotifications)  │  │
│  └──────┬──────┘  └───────┬───────┘  └──────────┬──────────┘  │
│         │                 │                      │              │
│         │                 ▼                      ▼              │
│  ┌──────▼─────────────────────────────────────────────────────┐│
│  │                   TanStack Query Cache                   ││
│  └────────────────────────────┬────────────────────────────┘│
└───────────────────────────────│──────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    API Client         │
                    └───────────┬────────────┘
                                │ HTTP/WebSocket
┌───────────────────────────────▼───────────────────────────────┐
│                      Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              /api/notifications/*                        │ │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐ │ │
│  │  │ List/Read   │  │ Push Subscribe│  │ SSE Stream       │ │ │
│  │  │ Endpoints   │  │ Endpoints    │  │ Endpoint         │ │ │
│  │  └──────┬─────┘  └──────┬───────┘  └─────┬──────────────┘ │ │
│  └─────────┼───────────────┼───────────────────┼──────────────┘ │
│            │               │                   │               │
│  ┌─────────▼───────────┐   │                   │               │
│  │ Notification       │   │                   │               │
│  │ Service            │   │                   │               │
│  └─────────┬──────────┘   │                   │               │
│            │               │                   │               │
│  ┌─────────▼────────┐   ▼                   ▼               │
│  │  Push Service   │ Resend API        SSE              │
│  │  (web-push)      │                   │                   │
│  └─────────┬────────┘                   │                   │
│            │                            │                   │
│  ┌─────────▼────────┐                   │                   │
│  │  PostgreSQL DB  │                   │                   │
│  │  notifications  │                   │                   │
│  │  prefs          │                   │                   │
│  │  push_subscriptions                 │                   │
│  └────────────────┘                   │                   │
└───────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   User Browser          │
                    │  ┌─────────────────┐    │
                    │  │  Service Worker  │    │
                    │  │  (Push Receiver) │    │
                    │  └─────────────────┘    │
                    └──────────────────────────┘
```

### Data Flow

#### In-App Notification Flow
```
Task Due Check → NotificationService → Notification DB
                                            ↓
                              SSE Stream → Frontend (Real-time update)
```

#### Push Notification Flow
```
Task Due Check → NotificationService → Notification DB
                                            ↓
                              PushService → web-push → Push Service → Browser
```

#### Email Flow
```
Task Due Check → NotificationService → Notification DB
                                            ↓
                              EmailService → Resend API → User Inbox
                                            ↓
                              Webhook → EmailDeliveryLog
```

---

## Implementation Phases

### Phase 0: Research ✅ COMPLETED

**Artifact**: `research.md`

| Technology | Decision | Context7 Source |
|------------|----------|------------------|
| Web Push | `web-push` library | `/web-push-libs/web-push` |
| Email | Resend Node.js SDK | `/resend/resend-node` |
| Real-time | SSE Starlette | `/sysid/sse-starlette` |
| UI | Radix UI DropdownMenu | `/radix-ui/website` |

---

### Phase 1: Design ✅ COMPLETED

**Artifacts**: `data-model.md`, `contracts/api.yaml`, `quickstart.md`

**Data Model**:
- 4 new tables: `notifications`, `notification_preferences`, `push_subscriptions`, `email_delivery_logs`
- Relationships with existing `users` and `tasks` tables
- JSONB columns for flexible data storage

**API Contracts**:
- 15+ endpoints across 3 domains: notifications, push, settings
- SSE streaming endpoint for real-time updates
- Webhook endpoint for Resend events

---

### Phase 2: Implementation (Next: `/sp.tasks`)

**Backend Tasks** (Phase II - FastAPI):

1. **Database Models** (`backend/app/models/`)
   - Create `notification.py` with Notification, NotificationPreference models
   - Create `push_subscription.py` with PushSubscription model
   - Create `email_delivery_log.py` with EmailDeliveryLog model
   - Add relationships to existing User and Task models

2. **Services** (`backend/app/services/`)
   - `notification_service.py`: Create, list, mark read, delete notifications
   - `push_service.py`: Send push via web-push, manage subscriptions
   - `email_service.py`: Send via Resend, React templates
   - `sse_service.py`: Event stream for real-time updates

3. **API Routes** (`backend/app/api/`)
   - `notifications.py`: CRUD endpoints, SSE stream
   - Settings management endpoints

4. **Email Templates** (`backend/app/emails/`)
   - React Email templates matching Deep Space theme
   - Task overdue, daily digest, weekly summary

5. **Webhooks** (`backend/app/webhooks/`)
   - Resend webhook handler for bounce detection

**Frontend Tasks** (Phase II - Next.js):

1. **Components** (`frontend/components/notifications/`)
   - `notification-bell.tsx`: Bell icon with Badge, DropdownMenu trigger
   - `notification-dropdown.tsx`: Glassmorphism dropdown with animations
   - `notification-item.tsx`: Single notification with hover/dismiss
   - `push-permission-modal.tsx`: Styled permission request modal

2. **Hooks** (`frontend/hooks/`)
   - `use-notifications.ts`: TanStack Query for notification CRUD
   - `use-notification-stream.ts`: SSE connection management

3. **Service Worker** (`frontend/public/sw.js`)
   - Push event handler
   - Notification click handler

4. **Integration**
   - Add bell to header in `app/layout.tsx`
   - Add notification endpoints to API client

---

## Quality Assurance

### Testing Strategy

| Type | Tool | Coverage |
|------|------|----------|
| Unit | pytest | All services, models |
| Integration | pytest + TestClient | API endpoints |
| E2E | Playwright | Full notification flows |
| Load | Locust | 10k concurrent deliveries |

### Performance Monitoring

| Metric | Target | Measurement |
|--------|--------|------------|
| API response time | <500ms p95 | SC-001 |
| Push delivery | <10s | SC-002 |
| Email delivery | <30s | SC-003 |
| Badge update | <200ms | SC-005 |

---

## Dependencies

### Backend New Dependencies

```bash
# Add to backend/pyproject.toml
web-push = "^1.9"        # Web Push API library
resend = "^3.0"          # Resend email SDK
sse-starlette = "^2.0"   # SSE for FastAPI
```

### Frontend New Dependencies

```bash
# Add to frontend/package.json
# Already installed (shadcn/ui):
@radix-ui/react-dropdown-menu
# Already installed:
framer-motion
```

---

## Success Criteria Mapping

| Spec Criteria | Implementation |
|---------------|----------------|
| SC-001: <500ms response | Indexed queries, pagination |
| SC-002: <10s push delivery | Async push service with queue |
| SC-003: <30s email delivery | Resend API with webhook tracking |
| SC-004: 95% enable rate | Frictionless permission modal |
| SC-005: <200s badge update | SSE real-time stream |
| SC-006: Mark all read | Batch update endpoint |
| SC-007: Smooth scrolling | Virtualization for 100+ items |
| SC-008: >40% email open rate | Deep Space themed emails |
| SC-009: >25% push CTR | Action buttons in notifications |
| SC-010: No spam | User control over all types |
| SC-011: 10k concurrent | Connection pooling, async processing |
| SC-012: Deep Space theme | Strict color/animation adherence |

---

## Open Questions

**None** - All clarifications from spec resolved:
- Q1: Urgent = task_overdue + task_due within 1 hour (Option B)
- Q2: Email service = Resend (Option A)
- Q3: Retention = 30 days (Option A)

---

## Next Steps

1. ✅ **Phase 0 (Research)**: Completed via Context7
2. ✅ **Phase 1 (Design)**: Completed - data-model, contracts, quickstart
3. ⏭️ **Phase 2 (Tasks)**: Run `/sp.tasks` to generate implementation tasks
4. ⏭️ **Phase 3 (Implement)**: Run `/sp.implement` to execute tasks

---

## Complexity Tracking

> **No violations** - All work extends existing Phase II (web application) without introducing additional projects or architectural patterns beyond the current tech stack.
