# Architecture (as built)

> The map of what actually exists. Update it whenever modules, data, interfaces, commands or flows change.
> Only real paths and names: every one here must exist in the code. Deeper backend notes:
> `docs/backend-architecture.md`, `backend/ARCHITECTURE.md`.

## Runtime

```
Browser ──► Next.js 15 app (frontend/, :3000)
   │          ├─ server components + server actions (app/actions/*) call the backend with the JWT
   │          ├─ GET /api/auth/token  → returns the auth_token cookie value to client code
   │          └─ middleware.ts         → redirects signed-out users away from app routes
   │
   └──(fetch, Authorization: Bearer)──► FastAPI (backend/app/main.py, :8000 / HF Space :7860)
                                          ├─ Neon PostgreSQL via SQLModel + asyncpg (app/db.py)
                                          ├─ OpenAI Agents SDK + in-process MCP tools (app/ai/)
                                          ├─ Qdrant (semantic task search, optional)
                                          ├─ Resend email, Web Push (VAPID), SSE stream
                                          └─ scheduler loop for reminders/digests (services/scheduler_service.py)
```

Phase I lives separately in `phase1/` (in-memory Python CLI). Kubernetes: `helm/chronos-todo`, Dockerfiles in
`frontend/` and `backend/`, Dapr client stubs in `backend/app/dapr/` and `frontend/lib/dapr/`.

## Code map

| Path | Responsibility |
|---|---|
| `frontend/app/` | App Router pages: `/` landing, `(auth)/login`, `(auth)/signup`, `/dashboard`, `/profile`, `/settings/notifications` |
| `frontend/app/actions/` | Server actions: `auth.ts` (sign in/up/out, `getSession`, `requireAuth`), `tasks.ts` |
| `frontend/middleware.ts`, `frontend/lib/routes.ts` | Route protection rules (`isPublicPath`, `isAuthPage`) |
| `frontend/lib/api-client.ts`, `lib/auth/token.ts`, `lib/config/api.ts` | Typed backend client, token fetch, `API_URL` |
| `frontend/components/` | UI: `landing/`, `auth/`, `dashboard/`, `tasks/`, `chat/`, `notifications/`, `layout/`, shadcn `ui/` (restyled on the tokens, plus `callout.tsx`); settings cards in `notifications/settings-section.tsx` |
| `frontend/scripts/capture-ui.py`, `backend/scripts/render_emails.py` | Design review: screenshot every page, dialog, menu and state (Playwright), and render every email template |
| `frontend/components/three/` | `orrery.tsx` (poster, lazy load, capability + reduced-motion checks, theme palette) and `orrery-scene.tsx` (R3F scene: core shader, orbits, instanced moons, stars) |
| `frontend/lib/orbits.ts` | `orbitCounts()`: open tasks bucketed into today / this week / later, plus done (feeds `dashboard/orbit-panel.tsx`) |
| `frontend/app/globals.css` | Design tokens (OKLCH palette for dark and light, type scale, motion, radius) and the glass / surface utilities; see `docs/design/README.md` |
| `frontend/hooks/` | TanStack Query + chat/notification/push hooks |
| `frontend/lib/stores/` | Chat UI context (`chat-store.ts`), task event bus, Zustand UI store |
| `backend/app/main.py` | App factory, CORS, middleware, lifespan (DB tables, Qdrant, scheduler), `/api/health` |
| `backend/app/routes/` | `auth.py`, `tasks.py`, `notifications.py` (incl. SSE `/stream`), `chat.py` (SSE chat, transcribe) |
| `backend/app/models/` | SQLModel tables: `core.py` (Task, TaskLog, User), `notification.py`, `push_subscription.py`, `email_delivery_log.py` |
| `backend/app/ai/` | Agents (`agents/todo_agent.py`), Kairos prompts and time helpers (`agents/prompts.py`), MCP tools (`mcp/tools.py` `TaskTools`), `services/runner_service.py`, Qdrant |
| `frontend/app/` file metadata | `icon.svg`, `favicon.ico`, `apple-icon.png`, `opengraph-image.tsx`, `manifest.ts`; PNG icons from `frontend/scripts/make-icons.py` |
| `backend/app/services/` | Email, push, notifications, SSE fan-out, scheduler, migrations |
| `backend/app/simple_auth.py` | JWT create/verify, password hashing, `get_current_user_id` dependency |
| `backend/alembic/` | Migrations (tables are also created on startup by `create_db_and_tables`) |

## Data

Tables (Postgres): `users`, `tasks`, `task_logs`, `notifications`, `notification_preferences`,
`push_subscriptions`, `email_delivery_logs`, `conversations`, `messages`, `conversation_preferences`,
`agent_handoffs`. Every task row is scoped by `user_id` (the JWT `sub`). Migrations: `cd backend && alembic
upgrade head`. Qdrant holds task embeddings for semantic search.

## Interfaces

Backend (all under `/api`, Bearer JWT except signin/signup/health): `auth/{signup,signin,signout,me}`,
`tasks` (CRUD, `search`, `{id}/complete`, `{id}/logs`, `{id}/summary/regenerate`), `notifications` (list,
read, settings, email prefs, push subscribe, `stream` SSE, Resend webhook), `chat` (POST SSE stream,
`conversations`, `transcribe`), `health`. Frontend route handler: `GET /api/auth/token`.

## How a request flows

Chat: `components/chat/chat-panel.tsx` → `hooks/use-chat.ts` POST `{API_URL}/api/chat` (Bearer from
`/api/auth/token`) → `routes/chat.py:chat` → `RunnerService.stream_chat` → `create_todo_agent` → MCP
`TaskTools` → DB → SSE events back; `lib/utils/sse.ts:parseSSEStream` parses them and task events update the
TanStack Query cache. Live notifications: `components/notifications/sse-stream-provider.tsx` streams
`{API_URL}/api/notifications/stream` with fetch (EventSource cannot send the Bearer header).

## Configuration

Backend (names only): `DATABASE_URL`, `BETTER_AUTH_SECRET` (required), `CORS_ORIGINS`, `OPENAI_API_KEY`,
`OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_WHISPER_MODEL`, `QDRANT_URL`, `QDRANT_API_KEY`,
`RESEND_API_KEY`, `RESEND_WEBHOOK_SECRET`, `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`,
`NEXT_PUBLIC_APP_URL`, `PHASE_III_ENABLED`, `DAPR_*`, `DEBUG`, `MAX_*` limits. Tests: `TEST_DATABASE_URL`.
Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_VAPID_PUBLIC_KEY`, `NEXT_PUBLIC_DAPR_*`.

## Commands

```
cd frontend && npm run dev                      # run frontend
cd frontend && npm run typecheck && npm run lint && npm test && npm run build
cd backend && uvicorn app.main:app --reload     # run backend
cd backend && python -m pytest -q               # backend tests
```
