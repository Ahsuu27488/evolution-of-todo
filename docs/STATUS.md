# Project Status

> Current truth only: what works now, what doesn't, what's next. History goes in CHANGELOG.md, reasons in
> DECISIONS.md. Updated in the same commit as every code change (the commit-msg hook checks). Keep it short:
> it is loaded into every agent session.

**Last updated:** 2026-10-27 · **Code at:** branch `chore/repair-shipshape-3d-redesign`
**In one line:** Chronos (Next.js 15 + FastAPI + Neon + OpenAI Agents) builds, installs and passes its checks
again after a repair pass, and the frontend has a new "night observatory" design with a 3D orrery (D-007).

## What works (verified)

- Frontend type check, lint, unit tests and production build: `npm run typecheck`, `npm run lint`, `npm test`
  (5 tests), `npm run build` all pass with no env vars set (2026-10-27).
- Redesign checked in the browser against the local backend (2026-10-27): landing (orrery hero, scroll-to-dial,
  bento), login/signup, dashboard (orbit panel updates live when a task is completed), chat panel, light mode,
  320 and 375 px with no horizontal scroll (theme toggle reachable on phones). Before/after screenshots in
  `docs/design/`.
- Fresh-eyes review (shipshape-reviewer) run on the whole branch; its 5 findings are fixed (CHANGELOG).
- Backend installs from `requirements.txt` on Python 3.14 and the app imports with all 30 API paths
  (`tests/test_core.py::test_app_registers_all_routers`, 2026-10-27).
- Sign-up, sign-in and `/api/auth/me` work end to end (`tests/test_auth_routes.py`, and in the browser), thanks to
  the `sqlmodel<0.0.45` pin (the test fails on 0.0.48).
- Backend tests: 44 pass against a real Postgres 16 (`TEST_DATABASE_URL`, 2026-10-27); without one, 9 DB-free
  tests pass and the 35 DB tests skip.
- Route protection: `/dashboard`, `/profile`, `/settings/*` redirect to `/login` without the `auth_token`
  cookie (`frontend/lib/routes.test.ts`; the old middleware treated every path as public).

## In progress

- `chore/repair-shipshape-3d-redesign` - repairs, shipshape adoption and the 3D redesign, all committed.
  Not pushed or merged; lands through a pull request.

## Live state

- Frontend live at https://chronos.ahsandev.site (README). Host not recorded in the repo (likely Vercel).
- Backend: `.github/workflows/deploy-hf.yml` pushes `backend/` to the Hugging Face Space
  `Ahsuu27488/evolution-of-todo-api` on **every push to main that touches `backend/`**. Merging this branch
  deploys the dependency pins and the models refactor to that Space.
- Helm chart (`helm/chronos-todo`) and Phase IV/V docs exist; whether a cluster is running is not recorded.

## Known gaps

1. CI runs backend tests without Postgres, so the MCP tool tests skip there (add a Postgres service to ci.yml).
2. Vercel's package manager may change: `pnpm-lock.yaml` was removed (npm + `package-lock.json` only, D-004).
3. Many specs/docs still describe Better Auth; the live auth is the backend JWT in the `auth_token` cookie (D-003).
4. ~40 `datetime.utcnow()` call sites write naive datetimes; they block upgrading past `sqlmodel<0.0.45` (D-005).
   Pydantic class-based `Config` deprecation warnings too.
5. Root `CLAUDE.md` and `backend/CLAUDE.md` contain long phase-era notes that partly predate the code.
6. Redesign not yet covered: profile and notification-settings pages got the new tokens and headings but no
   layout pass; Lighthouse and a real-phone test of the orrery have not been run.

## Next

1. Review the branch and open the PR (human merges; merging deploys the backend, see Live state).
2. Add a Postgres service to CI so the MCP tool tests run on every PR.
3. Confirm the frontend host builds with npm after the lockfile change.

## How to run and check

- Frontend: `cd frontend && npm ci && npm run dev` (needs `NEXT_PUBLIC_API_URL`, see `.env.example`)
- Frontend checks: `npm run typecheck && npm run lint && npm test && npm run build`
- Backend: `cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt pytest pytest-asyncio`
  then `uvicorn app.main:app --reload` (needs `DATABASE_URL`, `BETTER_AUTH_SECRET`)
- Backend tests: `cd backend && .venv/Scripts/python -m pytest -q` (44 passing with `TEST_DATABASE_URL`, e.g.
  `postgresql+asyncpg://postgres@127.0.0.1:<port>/test_todo`; 9 passing + 35 skipped without)
- No local Postgres? `py -3.12 -m pip install pgserver` gives an embedded one; append `?sslmode=disable` to a
  local `DATABASE_URL` (Neon URLs keep SSL required).
