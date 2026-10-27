# Changelog

> Newest first. Each entry: date, commit (or "uncommitted"), what changed, and for fixes the root cause.
> This is the history; STATUS.md holds only the current truth.

## 2026-10-27 · feat(frontend): "night observatory" redesign with a 3D orrery

- New design tokens (OKLCH ink/starlight palette, sun-gold accent, Funnel Display + Hanken Grotesk, motion,
  radius) and Liquid Glass limited to the floating layer (D-007, `docs/design/README.md`).
- `components/three/`: WebGL orrery (React Three Fiber + three) with a CSS poster, lazy loading, off-screen
  pause, reduced-motion still frame and low-power fallback.
- Landing rebuilt: pinned orrery hero that flattens into a dial on scroll, product bento with a labelled
  example conversation, closing call to action, footer. Auth pages split with a calm orrery. Dashboard:
  "Your orbits" panel (`lib/orbits.ts`, unit-tested), date-led heading, solid wrapping toolbar, compact task
  cards with friendly dates. Chat panel moved onto theme tokens (light mode works) with a labelled button.
- Removed gradient text and all hard-coded neon cyan/purple; larger touch targets on Button/Input; labels on
  icon-only buttons (account menu, task actions, add task).

## 2026-10-27 · fix(backend): signup failed on current sqlmodel

- Sign-up raised "Datetime values must have timezone information": sqlmodel 0.0.45+ makes datetime columns
  timezone-aware and rejects naive values, and `User.created_at` defaulted to `datetime.utcnow()`. Default is
  now `datetime.now(timezone.utc)`; `sqlmodel<0.0.45` pinned because ~40 other `utcnow()` call sites still
  write naive datetimes. Regression test `tests/test_auth_routes.py` (signup, signin, /me) fails on the old
  code with sqlmodel 0.0.48 and passes now.

## 2026-10-27 · fix(backend): MCP tool calls and local Postgres

- `app/ai/mcp/server.py`: `_execute_tool_call` passed a removed `autocommit=` argument to `TaskTools`
  (every MCP `call_tool` raised TypeError), used `get_session()` (a FastAPI generator dependency) as a context
  manager, and referenced `ToolResponse` without importing it. Fixed; the caller now commits.
- `app/db.py:ssl_mode`: `sslmode=disable` in `DATABASE_URL` turns SSL off (SSL stays required by default).
- Tests: test engine uses `NullPool` (pooled asyncpg connections broke across per-test event loops); ownership
  tests assert the structured `error` field instead of message wording. 43/43 pass on Postgres 16.

## 2026-10-27 · shipshape adoption

- Project memory and workflow set up with shipshape (D-001): docs/, AGENTS.md, .shipshape/, .githooks/, CI
  (`.github/workflows/ci.yml` runs frontend and backend checks plus the docs gate), PR template.

## 2026-10-27 · 405e3a1 fix(backend)

- Dependencies install again: removed the `contextvars` backport (its `immutables` dep fails to build),
  added `sqlalchemy[asyncio]` (greenlet), pinned `mcp<2` / `openai<3` / `openai-agents<0.9` (mcp 2.x removed
  `Server.list_tools()` and crashed app import). Synced `pyproject.toml` + `uv.lock` (D-005).
- `postgres://` URLs became the nonexistent `postgres+asyncpg` dialect; fixed in `app/db.py:to_async_url`.
- Test harness repaired (`Base` import, removed `event_loop` fixture, one-time DB probe); new `tests/test_core.py`.

## 2026-10-27 · 92d242c refactor(backend)

- `app/models.py` → `app/models/core.py`; removed the importlib shadowing hack (D-006).

## 2026-10-27 · 7a8a974 fix(frontend)

- Route protection: `"/"` matched every path via `startsWith`, so app routes were public. Fixed in
  `lib/routes.ts` with regression tests.
- Build: removed the unused Better Auth stack that threw without `DATABASE_URL` during `next build` (D-003).
- Live notifications: SSE hit the Next origin without a token and was gated on localStorage; now streams from
  the backend with fetch + Bearer. Email preferences' `/api/auth/me` call fixed the same way.
- Lint errors fixed, ESLint ignores `.next/`, `test`/`typecheck` scripts, single npm lockfile (D-004).

## Earlier history

- Phases I-V delivered Jan-Feb 2026 (console app → full-stack → AI chatbot → K8s/Helm → Oracle OKE); see
  `git log` and `history/prompts/` for the spec-driven record.
