<!-- shipshape:start (managed by shipshape; edit outside the markers) -->
## How to work in this repository (shipshape)

**Before writing any code, in every session:**
1. Run `sh .shipshape/context.sh` (Windows without sh: `pwsh -File .shipshape/context.ps1`) and act on its warnings.
2. Read `docs/STATUS.md` (where we are, what's next), `docs/DECISIONS.md` (what was decided and why; never undo a
   decision without a new entry) and `docs/ARCHITECTURE.md` (how the code connects).
3. Read the code you will change and its callers. Never build on a guess; if the docs and the code disagree, the
   code is the truth and the docs get fixed.
4. If a request contradicts a decision in DECISIONS.md, stop before editing: quote the decision and its reason, and
   ask the user to confirm. A confirmed change gets a new decision that supersedes the old one.

**Every change:** say the tier (T0 trivial / T1 normal / T2 risky: data, auth, money, deletes, live systems),
work on a branch (never commit to the default branch), name the check that proves it works, test the real code
path, read the whole diff, then update `docs/STATUS.md` + `docs/CHANGELOG.md` (and DECISIONS / ARCHITECTURE when
relevant) in the same commit. The `commit-msg` hook rejects code commits without them; `[no-docs]` is only for
changes with no behaviour change. Land through a pull request with What / Why / How verified / Risk.

**T2 and anything live:** written plan in `docs/plans/`, the human's go-ahead, dry run first, written rollback.
**Unattended:** never merge, never touch anything live or any secret; stop and report when stuck.

If the shipshape skills are installed, use them (`shipshape`, `shipshape-memory`, `shipshape-unattended`).
Project-specific rules below and in the docs take precedence over these defaults.
<!-- shipshape:end -->

## Project-specific rules (evolution-of-todo)

- Spec-driven development stays (D-002): non-trivial features get `specs/NNN-name/` (spec, plan, tasks) via the
  `.claude/commands/sp.*` commands. shipshape docs record the current state on top of that.
- Pushing to `main` deploys `backend/` to the Hugging Face Space (`.github/workflows/deploy-hf.yml`): treat any
  change that reaches main as a live change.
- Auth is the backend JWT in the `auth_token` httpOnly cookie (D-003). Do not reintroduce Better Auth or
  localStorage tokens.
- Backend deps: edit `requirements.txt` and `pyproject.toml` together, then `uv lock` (D-005).
- Never commit `.env`, `.env.local` or keys; the examples (`*.env.example`) hold variable names only.
