# Quickstart: Notification System Implementation

**Feature**: 011-notification-system
**Date**: 2026-01-27

## Prerequisites

### Environment Variables

```bash
# Backend (.env)
VAPID_PUBLIC_KEY=BGtkbcjrO12YMoDuq2sCQeHlu47uPx3SHTgFKZFYiBW8Qr0D9vgyZSZPdw6_4ZFEI9Snk1VEAj2qTYI1I1YxBXE
VAPID_PRIVATE_KEY=I0_d0vnesxbBSUmlDdOKibGo6vEXRO-Vu88QlSlm5j0
RESEND_API_KEY=re_xxxxxxxxxxxxxx
RESEND_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxx
```

### Backend Dependencies

```bash
# backend/
uv add web-push
uv add resend
uv add sse-starlette
```

### Frontend Dependencies

```bash
# frontend/
npm install @radix-ui/react-dropdown-menu
npm install framer-motion
```

---

## Step 1: Backend Setup (FastAPI)

### 1.1 Create Database Models

```python
# backend/app/models/notification.py

from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    TASK_DUE = "task_due"
    TASK_OVERDUE = "task_overdue"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_REMINDER = "task_reminder"
    SYSTEM_UPDATE = "system_update"

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    type: NotificationType = Field(index=True)
    title: str
    message: str
    data: dict = Field(sa_type=JSON, default={})
    related_task_id: Optional[int] = Field(foreign_key="task.id", index=True)
    read_status: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_channels: list[str] = Field(sa_type=JSON, default=[])
    deleted_at: Optional[datetime] = Field(default=None)
```

### 1.2 Create Push Notification Service

```python
# backend/app/services/push_service.py

import webpush
from fastapi import HTTPException

VAPID_PUBLIC_KEY = "..."
VAPID_PRIVATE_KEY = "..."

webpush.setVapidDetails(
    "mailto:notifications@chronos-todo.app",
    VAPID_PUBLIC_KEY,
    VAPID_PRIVATE_KEY
)

async def send_push_notification(subscription: dict, payload: dict):
    """Send push notification via web-push library."""
    try:
        response = await webpush.sendNotification(
            subscription,
            JSON.dumps(payload),
            {"TTL": 3600, "urgency": "high"}
        )
        return {"success": True, "response": response}
    except webpush.WebPushException as e:
        if e.statusCode in (404, 410):
            # Subscription expired, remove from DB
            return {"success": False, "expired": True}
        return {"success": False, "error": str(e)}
```

### 1.3 Create SSE Stream Endpoint

```python
# backend/app/api/notifications.py

from sse_starlette import EventSourceResponse
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

async def notification_stream(request: Request):
    """Stream notifications via SSE."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            # Check for new notifications
            # yield {"data": notification, "event": "notification"}
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
```

---

## Step 2: Frontend Setup (Next.js)

### 2.1 Create Notification Bell Component

```tsx
// frontend/components/notifications/notification-bell.tsx

"use client"

import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { Bell } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { motion, AnimatePresence } from "framer-motion"

export function NotificationBell({ unreadCount }: { unreadCount: number }) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="relative p-2 rounded-md hover:bg-muted">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs bg-destructive">
              {unreadCount}
            </Badge>
          )}
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content className="w-80 glass-modal">
        <DropdownMenu.Label>Notifications</DropdownMenu.Label>
        <DropdownMenu.Separator />
        {/* Notification items */}
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  )
}
```

### 2.2 Setup Service Worker

```javascript
// public/sw.js

self.addEventListener('push', (event) => {
  const data = event.data.json()

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icon.png',
      badge: '/badge.png',
      data: { url: data.url }
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/dashboard')
  )
})
```

---

## Step 3: Email Templates

### 3.1 Create React Email Template

```tsx
// backend/app/emails/task_overdue.tsx

import { jsx } from "react/jsx-runtime"

interface TaskOverdueEmailProps {
  taskTitle: string
  taskUrl: string
}

export function TaskOverdueEmail({ taskTitle, taskUrl }: TaskOverdueEmailProps) {
  return jsx('div', {
    style: {
      backgroundColor: '#0a0a14',
      color: '#f8f8f8',
      fontFamily: 'sans-serif',
      padding: '40px',
      borderRadius: '12px'
    },
    children: [
      jsx('h1', {
        style: { color: '#00f5ff', fontSize: '24px' },
        children: 'Task Overdue'
      }),
      jsx('p', {
        style: { fontSize: '16px', margin: '20px 0' },
        children: taskTitle
      }),
      jsx('a', {
        href: taskUrl,
        style: {
          backgroundColor: '#00f5ff',
          color: '#000',
          padding: '12px 24px',
          borderRadius: '6px',
          textDecoration: 'none',
          display: 'inline-block'
        },
        children: 'Complete Task'
      })
    ]
  })
}
```

---

## Step 4: Database Migration

```bash
# Create Alembic migration
uv run alembic revision --autogenerate -m "Add notification system tables"

# Apply migration
uv run alembic upgrade head
```

---

## Step 5: Testing

### 5.1 Test In-App Notifications

```bash
# Create test notification
curl -X POST http://localhost:8000/api/notifications/test \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "task_overdue", "title": "Test", "message": "Test notification"}'
```

### 5.2 Test Push Notifications

1. Open browser DevTools → Application → Service Workers
2. Click "Push" to send test notification
3. Verify notification appears with correct styling

### 5.3 Test Email

```bash
# Send test email
curl -X POST http://localhost:8000/api/notifications/email/test \
  -H "Authorization: Bearer $TOKEN"
```

---

## Development Workflow

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Run Migrations**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Generate VAPID Keys** (one-time):
   ```python
   from webpush import generateVAPIDKeys
   keys = generateVAPIDKeys()
   print(keys)
   ```

---

## Verification Checklist

- [ ] Bell icon displays with unread count badge
- [ ] Clicking bell opens glassmorphism dropdown
- [ ] Notifications have cyan glow indicator
- [ ] Clicking notification marks as read
- [ ] "Mark all as read" button works
- [ ] Push permission modal appears on enable
- [ ] Push notifications arrive when tab is backgrounded
- [ ] Emails have Deep Space dark theme styling
- [ ] Unsubscribe link works in emails
- [ ] Bounced emails disable future sends

---

## Next Steps

After quickstart:
1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to begin implementation
3. Reference `plan.md` for detailed architecture
