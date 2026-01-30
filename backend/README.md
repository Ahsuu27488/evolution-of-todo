---
title: Evolution of Todo API
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Evolution of Todo Backend

FastAPI backend for the Evolution of Todo hackathon project with comprehensive notification system.

## Features

### Core Features
- JWT Authentication with Better Auth
- Task CRUD with filtering, sorting, search
- Recurring tasks with auto-scheduling
- Audit logging for all modifications
- Async PostgreSQL with Neon
- User profile with timezone support

### Notification System
- **In-App Notifications** — Real-time SSE streaming
- **Push Notifications** — Web Push API (VAPID)
- **Email Notifications** — Resend integration with templates
- **Digest Emails** — Daily (8 AM) and weekly (Monday 9 AM) with timezone support
- **Notification Preferences** — Per-channel settings
- **Do Not Disturb Hours** — Time-based silence
- **One-Click Unsubscribe** — Token-based email unsubscribe
- **Webhook Tracking** — Email delivery status updates
- **Background Scheduler** — Async job processing

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration (with firstName, lastName)
- `POST /api/auth/signin` - User login
- `GET /api/auth/me` - Get current user (includes displayName, timezone)
- `PUT /api/auth/me` - Update user profile (firstName, lastName, timezone)

**User Schema (v2)**:
- `firstName` (string, required): User's first name
- `lastName` (string, optional): User's last name (supports mononyms)
- `displayName` (string, computed): "First Last" or "First" or legacy name
- `email` (string): User email address
- `timezone` (string): IANA timezone (default: "UTC")
- `created_at` (datetime): Account creation timestamp

### Tasks
- `GET /api/tasks` - List tasks (with filters/sort/pagination)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `GET /api/tasks/search` - Search tasks
- `GET /api/tasks/{id}/logs` - Get audit logs

### Notifications
- `GET /api/notifications` - List notifications with unread count
- `PUT /api/notifications/{id}/read` - Mark as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `DELETE /api/notifications/{id}` - Soft delete notification
- `GET /api/notifications/stream` - SSE stream for real-time updates
- `GET /api/notifications/settings` - Get notification preferences
- `PUT /api/notifications/settings` - Update notification preferences

### Push Notifications
- `POST /api/notifications/push/subscribe` - Subscribe to push notifications
- `DELETE /api/notifications/push/unsubscribe` - Unsubscribe from push
- `GET /api/notifications/push/status` - Get subscription status
- `POST /api/notifications/push/test` - Send test push notification

### Email Notifications
- `GET /api/notifications/email/preferences` - Get email preferences
- `PUT /api/notifications/email/preferences` - Update email preferences
- `POST /api/notifications/email/test` - Send test email
- `POST /api/notifications/email/webhook` - Resend webhook handler

### Health
- `GET /api/health` - System health check

## Notification System Architecture

### Services

| Service | File | Description |
|---------|------|-------------|
| NotificationService | `app/services/notification_service.py` | CRUD, deduplication, multi-channel dispatch |
| SSEService | `app/services/sse_service.py` | Server-Sent Events for real-time updates |
| PushService | `app/services/push_service.py` | Web Push API with VAPID, rate limiting |
| EmailService | `app/services/email_service.py` | Resend integration, HTML templates |
| SchedulerService | `app/services/scheduler_service.py` | Background digest jobs |
| UnsubscribeService | `app/services/unsubscribe_service.py` | Token-based unsubscribe |

### Notification Types

- `TASK_DUE` — Task due soon (within 1 hour)
- `TASK_OVERDUE` — Task is overdue
- `TASK_COMPLETED` — Task marked complete
- `TASK_ASSIGNED` — Task assigned to user
- `SYSTEM_UPDATE` — System notifications
- `WELCOME` — Welcome email for new users

### Deduplication Windows

| Type | Window | Purpose |
|------|--------|---------|
| TASK_DUE | 5 minutes | Tasks can become due quickly |
| TASK_OVERDUE | 15 minutes | Less frequent, important |
| TASK_COMPLETED | 1 minute | Instant feedback |
| SYSTEM_UPDATE | 24 hours | Low priority |

### Rate Limiting

- Push notifications: **3 per hour** per user
- Urgent notifications (TASK_DUE, TASK_OVERDUE) are **exempt**
- Tracked in-memory with sliding window

### Digest Schedule

- **Daily Digest**: 8:00 AM in user's timezone
- **Weekly Summary**: Monday 9:00 AM in user's timezone
- Task reminders: Every 15 minutes
- Cleanup job: Every 24 hours (soft-deleted notifications older than 30 days)

## Data Migration

### Legacy User Name Migration

The backend includes a migration service for migrating legacy single-name users to the new first_name/last_name schema:

**Migration Script**:
```bash
# Check migration status
python backend/scripts/migrate_users.py --status

# Preview changes (dry-run)
python backend/scripts/migrate_users.py --dry-run

# Run migration
python backend/scripts/migrate_users.py
```

**Migration Strategy**:
- Legacy `name` value becomes `first_name`
- `last_name` set to `NULL` (supports mononyms)
- Batch processing (100 users per batch)
- Zero-downtime with rollback safety
- Progress monitoring and integrity checks

**Migration Service** (`app/services/migration.py`):
- `get_migration_progress()`: Get migration statistics
- `migrate_user_names()`: Execute batch migration
- `verify_migration_integrity()`: Check data consistency

## Tech Stack

- **Framework**: FastAPI
- **Database**: Neon PostgreSQL (asyncpg)
- **Authentication**: JWT (shared secret with frontend)
- **Deployment**: Hugging Face Spaces (Docker SDK)
