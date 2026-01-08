---
name: "better-auth-guide"
description: "Fetch Better Auth documentation and apply JWT authentication best practices. Use when implementing user authentication, JWT tokens, or securing API endpoints (Phase II+)."
version: "1.0.0"
---

# Better Auth + FastAPI JWT Integration Guide

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Better Auth, JWT tokens, or authentication
- Implementation requires user login, signup, or session management
- User asks about securing API endpoints or protecting routes
- Phase II authentication implementation begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Auth Need**: Detect authentication requirement from context
2. **Fetch Docs**: Call Context7 for Better Auth and PyJWT documentation
3. **Apply Cross-Stack Pattern**: Configure both Next.js (Better Auth) and FastAPI (JWT verify)
4. **Validate Security**: Ensure no common authentication vulnerabilities

## Output Format

Provide structured output:
- **Context7 Source**: Library ID used for documentation
- **Auth Flow**: Description of the authentication flow
- **Frontend Config**: Better Auth setup in Next.js
- **Backend Config**: JWT verification in FastAPI
- **Security Checklist**: Applied security measures

## Constraints and Rules

- ALWAYS use environment variables for secrets (BETTER_AUTH_SECRET)
- NEVER log or expose JWT tokens
- ALWAYS validate token expiration
- Use httpOnly cookies for token storage when possible
- Implement proper CORS configuration
- Both frontend and backend MUST share the same secret
- This skill applies to Phase II and later only

## Example

**Input**: "Set up user authentication for the Todo app"

**Output**:
```
Context7 Source: /better-auth/better-auth (topic: jwt plugin)
Auth Flow: Better Auth issues JWT → Frontend attaches to requests → FastAPI validates

Frontend Config (Next.js):
- Install better-auth with jwt plugin
- Configure database adapter for Neon
- Set BETTER_AUTH_SECRET environment variable

Backend Config (FastAPI):
- Install PyJWT library
- Create verify_jwt dependency function
- Apply to protected routes with Depends()

Security Checklist:
- [x] Shared secret in environment variables
- [x] Token expiration configured (7 days)
- [x] CORS restricted to frontend origin
- [x] User ID validation on resource access
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `jwt plugin` | JWT token configuration |
| `configuration` | Initial Better Auth setup |
| `database` | Database adapter setup |
| `session` | Session management patterns |
