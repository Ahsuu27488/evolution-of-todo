# Decision Log

> Each entry: what was decided, **why**, and where it lives in the code. Numbering is permanent: never
> renumber or delete an entry. When a decision changes, add a new entry and mark the old heading
> *(superseded by D-NNN)*. A decision here beats anything that contradicts it elsewhere.
> Older design records live in `history/adr/` and `specs/`; entries below are the ones that still hold.

**D-001 Project memory and workflow set up with shipshape.** (2026-10-27)
Docs in `docs/` (STATUS, DECISIONS, ARCHITECTURE, CHANGELOG) are the project's memory and are loaded at every
session start; code commits must update STATUS and CHANGELOG (`.githooks/commit-msg`); work happens on branches
and lands through pull requests; the default branch is protected by `.githooks/pre-push`.
*Why:* AI coding sessions start with no memory; without written state and reasons, settled decisions get
re-made and working code gets broken. *Where:* `AGENTS.md`, `.shipshape/`, `.githooks/`, `docs/`.

**D-002 Spec-driven development with Spec-Kit Plus stays.** (recovered; in use since the start)
Features are specified in `specs/NNN-name/` (spec, plan, tasks) with prompt history in `history/prompts/`
and ADRs in `history/adr/`, driven by the `.claude/commands/sp.*` commands.
*Why:* the hackathon's core requirement ("Spec-Driven Development", `docs/Hackathon.md`). shipshape docs add
the current-state memory on top; they do not replace specs. *Where:* `specs/`, `history/`, `.specify/`.

**D-003 Auth is the backend JWT in an httpOnly cookie; Better Auth is not used.** (2026-10-27)
The FastAPI backend issues an HS256 JWT signed with `BETTER_AUTH_SECRET` (`backend/app/simple_auth.py`). The
`signInAction`/`signUpAction` server actions store it in the `auth_token` httpOnly cookie
(`frontend/app/actions/auth.ts`); client code gets it from `GET /api/auth/token` and sends `Authorization:
Bearer`. The unused Better Auth server (`lib/auth.ts`, `/api/auth/[...all]`) and the localStorage auth client
were removed. *Why:* the login flow already ran on the backend JWT; the Better Auth module threw at import
without `DATABASE_URL`, breaking `next build` and the Docker image, and the localStorage helpers silently
disabled live notifications. The env var keeps its historical name. *Where:* files above, `frontend/types/user.ts`.

**D-004 npm with `package-lock.json` is the frontend package manager.** (2026-10-27)
`pnpm-lock.yaml` was removed. *Why:* two lockfiles drifted apart; the Dockerfile runs `npm ci`. *Where:*
`frontend/package-lock.json`, `frontend/Dockerfile`.

**D-005 `requirements.txt` is the backend's install source; AI SDK majors are pinned.** (2026-10-27)
Docker and the Hugging Face Space install from `backend/requirements.txt`; `pyproject.toml` mirrors it for uv
and must be kept in sync (`uv lock` after changes). `mcp<2`, `openai<3`, `openai-agents<0.9`, `sqlmodel<0.0.45`
(0.0.45+ rejects naive datetimes, which the code still writes in ~40 places).
*Why:* unpinned, a fresh install pulled mcp 2.x (removed `Server.list_tools()`, crashing app import) and newer
openai/agents majors the code was not written for. Raise the pins deliberately, with the chat flow tested.
*Where:* `backend/requirements.txt`, `backend/pyproject.toml`, `backend/uv.lock`.

**D-006 Core SQLModel models live in `app/models/core.py`.** (2026-10-27)
*Why:* `app/models.py` was shadowed by the `app/models/` package and loaded via importlib under a fake module
name. Import from `app.models` as before. *Where:* `backend/app/models/__init__.py`, `backend/app/models/core.py`.

**D-007 Visual direction: "night observatory" with the orrery as the one signature.** (2026-10-27)
Ink-blue OKLCH palette, one accent (sun gold) plus orbit blue, Funnel Display + Hanken Grotesk. The 3D
orrery (React Three Fiber + three, no drei) is the only 3D element: full on the landing page, calm beside the
auth forms, a small data-driven version on the dashboard. Glass only on the floating layer; content on solid
surfaces. Replaces the "Deep Space" cyan/purple neon theme (specs 008/009).
*Why:* the old look used generic AI tells (gradient text, neon glows, identical icon cards) and gave the
product no identity; an orrery maps directly onto the product (tasks orbiting "now" by due date). App screens
stay fast (Operate mode): no heavy effects beyond the lazy mini orrery. *Where:* `frontend/app/globals.css`,
`frontend/components/three/`, `frontend/components/landing/`, `frontend/lib/orbits.ts`, `docs/design/README.md`.

<!-- Template for the next entry:

**D-00N <Decision in one line>.** (YYYY-MM-DD)
<What exactly was decided.>
*Why:* <the problem, the alternatives considered, why this one.> *Where:* <files / functions / settings>.
-->
