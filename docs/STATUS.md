# Project Status

> Current truth only: what works now, what doesn't, what's next. History goes in CHANGELOG.md, reasons in
> DECISIONS.md. Updated in the same commit as every code change (the commit-msg hook checks). Keep it short:
> it is loaded into every agent session.

**Last updated:** 2026-10-27 · **Code at:** branch `chore/repair-shipshape-3d-redesign`
**In one line:** Chronos (Next.js 15 + FastAPI + Neon + OpenAI Agents) builds, installs and passes its checks
again after a repair pass; the frontend is being redesigned as an immersive 3D experience on this branch.

## What works (verified)

- Frontend type check, lint, unit tests and production build: `npm run typecheck`, `npm run lint`, `npm test`
  (3 tests), `npm run build` all pass with no env vars set (2026-10-27).
- Backend installs from `requirements.txt` on Python 3.14 and the app imports with all 30 API paths
  (`tests/test_core.py::test_app_registers_all_routers`, 2026-10-27).
- Backend tests: 43 pass against a real Postgres 16 (`TEST_DATABASE_URL`, 2026-10-27); without one, 9 DB-free
  tests pass and the 34 MCP tool tests skip.
- Route protection: `/dashboard`, `/profile`, `/settings/*` redirect to `/login` without the `auth_token`
  cookie (`frontend/lib/routes.test.ts`; the old middleware treated every path as public).

## In progress

- `chore/repair-shipshape-3d-redesign` - repairs (done, committed), shipshape adoption (this commit), then the
  3D frontend redesign (landing, auth, dashboard, chat). Not merged; lands through a pull request.

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
4. `datetime.utcnow()` and Pydantic class-based `Config` deprecation warnings in the backend.
5. Root `CLAUDE.md` and `backend/CLAUDE.md` contain long phase-era notes that partly predate the code.

## Next

1. Finish and review the 3D redesign on this branch, then open the PR (human merges; see Live state).
2. Add a Postgres service to CI so the MCP tool tests run on every PR.
3. Confirm the frontend host builds with npm after the lockfile change.

## How to run and check

- Frontend: `cd frontend && npm ci && npm run dev` (needs `NEXT_PUBLIC_API_URL`, see `.env.example`)
- Frontend checks: `npm run typecheck && npm run lint && npm test && npm run build`
- Backend: `cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt pytest pytest-asyncio`
  then `uvicorn app.main:app --reload` (needs `DATABASE_URL`, `BETTER_AUTH_SECRET`)
- Backend tests: `cd backend && .venv/Scripts/python -m pytest -q` (43 passing with `TEST_DATABASE_URL`, e.g.
  `postgresql+asyncpg://postgres@127.0.0.1:<port>/test_todo`; 9 passing + 34 skipped without)
- No local Postgres? `py -3.12 -m pip install pgserver` gives an embedded one; append `?sslmode=disable` to a
  local `DATABASE_URL` (Neon URLs keep SSL required).
