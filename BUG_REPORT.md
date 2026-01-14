# Bug Report - Evolution of Todo (Phase II)

**Date**: 2026-01-14
**Environment**: Production (evolution-of-todo-tau.vercel.app)

---

## Summary

Frontend is deployed and UI works, but **task list doesn't load** due to Better Auth session validation failing.

---

## What Works ✅

| Component | Status |
|-----------|--------|
| Backend (FastAPI on HF Spaces) | ✅ All endpoints passing |
| Frontend Build | ✅ `npm run build` succeeds |
| Sign Up / Sign In | ✅ Creates Better Auth session |
| Task Creation | ✅ Saves to backend successfully |
| Landing Page | ✅ Beautiful glassmorphism UI |

---

## What's Broken ❌

### Primary Issue: `/api/auth/token` → 401

**Symptom**: Dashboard shows "No tasks yet" even after creating tasks.

**Root Cause**:
```bash
curl https://evolution-of-todo-tau.vercel.app/api/auth/token
# Returns: { "error": "No active session" }
```

The `/api/auth/token` endpoint (used by `lib/api-client.ts` to fetch JWT) fails because:
- `auth.api.getSession()` in `app/api/auth/token/route.ts` can't read the Better Auth session cookie
- Likely a **Vercel serverless + Neon DB cold start** timing issue

**Impact**: TanStack Query can't fetch tasks because `api.getTasks()` has no JWT token.

---

## Files to Debug

### 1. `frontend/lib/auth.ts`
```typescript
// Better Auth config with Neon pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 40000,  // ← May need increase for cold starts
})
```

### 2. `frontend/app/api/auth/token/route.ts`
```typescript
// This fails to read session:
const session = await auth.api.getSession({
  headers: await headers(),
})
// Returns: null (401 error)
```

### 3. `frontend/lib/api-client.ts`
```typescript
// Auto-fetches JWT before each request:
private async getAuthToken(): Promise<string | null> {
  const response = await fetch(`${this.appUrl}/api/auth/token`, {
    credentials: "include",
  })
  // Returns 401 → no token → API calls fail
}
```

---

## Fix Attempts (In Priority Order)

### 1. Increase DB Connection Timeout
```typescript
// lib/auth.ts
connectionTimeoutMillis: 60000,  // Increase from 40s to 60s
```

### 2. Check Vercel Environment Variables
```bash
# Verify these are set on Vercel:
DATABASE_URL=<valid Neon connection string>
BETTER_AUTH_SECRET=<matches backend>
BETTER_AUTH_URL=https://evolution-of-todo-tau.vercel.app
```

### 3. Use Better Auth's Server-Side Session First
Try fetching tasks directly via Better Auth's server-side session instead of JWT:
```typescript
// In dashboard/page.tsx (Server Component)
const session = await auth.api.getSession({ headers: await headers() })
// Then call backend with session.user.id directly
```

### 4. Fallback: Direct Backend Sign-In
If Better Auth continues failing, bypass it for API calls:
- Store JWT from backend `/api/auth/signin` directly in httpOnly cookie
- Skip `/api/auth/token` endpoint entirely

---

## Testing Commands

```bash
# Backend tests (should pass)
cd backend && BETTER_AUTH_SECRET=xxx .venv/bin/python scripts/test_all.py

# Frontend build
cd frontend && npm run build

# Check auth endpoint (after logging in via browser)
curl -v https://evolution-of-todo-tau.vercel.app/api/auth/token \
  -H "Cookie: better-auth.session_token=<from-browser>"
```

---

## Workaround While Fixing

1. **Test on localhost** where Better Auth works fine
2. **Use backend API directly** via curl/Postman to confirm tasks exist
3. **Monitor Vercel logs** for Neon DB connection errors
