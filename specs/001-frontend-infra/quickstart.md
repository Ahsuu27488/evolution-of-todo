# Quickstart: Frontend Infrastructure Stabilization

**Feature**: 001-frontend-infra
**Branch**: `001-frontend-infra`

## Prerequisites

1. **Backend running** on `http://localhost:8000`
2. **Frontend dependencies** installed
3. **Environment variables** configured (`.env` file)

## Development Setup

### 1. Start Backend

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

Verify:
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"ok","timestamp":"...","version":"2.0.0"}
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

## Environment Variables

Create `frontend/.env`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=<shared-secret-with-backend>
DATABASE_URL=<neon-postgres-connection-string>
```

**Important**: `BETTER_AUTH_SECRET` must match the backend's `BETTER_AUTH_SECRET` for JWT verification to work.

## Verification Commands

### Type Check

```bash
cd frontend
npx tsc --noEmit --strict
```

Expected: 0 errors

### E2E Test

```bash
./scripts/verify-e2e.sh
```

Expected: All 13 tests pass

### Backend Tests

```bash
./backend/scripts/test_all.py
```

Expected: All 8 test suites pass

## Implementation Checklist

Use `/sp.tasks` to generate detailed tasks for:

- [ ] Create `/api/auth/token/route.ts` endpoint
- [ ] Refactor `lib/api-client.ts` (unified client)
- [ ] Remove `userId` parameters from API methods
- [ ] Update `healthCheck()` to use `/api/health`
- [ ] Update `middleware.ts` (cookie names, remove console.log)
- [ ] Update `app/actions/tasks.ts` to use unified client
- [ ] Delete `lib/api.ts`
- [ ] Run type checking and fix any errors
- [ ] Run E2E tests and verify

## Troubleshooting

### "No active session" error

- Ensure Better Auth session cookie is set
- Check that `BETTER_AUTH_SECRET` matches frontend and backend
- Verify `/api/auth/signin` works correctly

### Type errors after refactoring

- Run `npx tsc --noEmit` to see specific errors
- Ensure `lib/errors.ts` Result type is imported
- Check that all API client methods are typed correctly

### Health check failing

- Verify backend is running on port 8000
- Check that `/api/health` returns 200 (not `/health`)
- Ensure no CORS issues blocking the request

## Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `lib/api-client.ts` | Unified API client | REFACTOR |
| `lib/api.ts` | Duplicate client | DELETE |
| `lib/errors.ts` | Result/ApiError types | KEEP |
| `lib/auth.ts` | Better Auth config | KEEP |
| `app/api/auth/token/route.ts` | JWT endpoint | CREATE |
| `middleware.ts` | Route protection | UPDATE |

## Rollback Plan

If issues arise, revert to previous state:

```bash
# Check out the commit before changes
git log --oneline
git checkout <commit-hash>

# Or reset the branch
git reset --hard HEAD~1
```
