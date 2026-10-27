# Changelog

> Newest first. Each entry: date, commit (or "uncommitted"), what changed, and for fixes the root cause.
> This is the history; STATUS.md holds only the current truth.

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
