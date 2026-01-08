# Research: Phase II - "Chronos" Web App Technology Decisions

**Feature**: 007-phase2-chronos-webapp
**Date**: 2026-01-06
**Status**: Complete

## Overview

This document captures technology research and decision-making for the Phase II "Chronos" Professional Web App. All decisions align with the hackathon Phase II requirements and constitution constraints.

---

## Frontend Technology Decisions

### State Management: Zustand

**Decision**: Use Zustand for client-side UI state management

**Rationale**:
- Minimal boilerplate compared to Redux Toolkit
- Works seamlessly with React Server Components (RSC)
- TypeScript-first with excellent type inference
- Small bundle size (~1KB gzipped)
- Simple API that doesn't require providers/actions/reducers pattern

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| Redux Toolkit | Industry standard, great devtools | Heavy boilerplate, not RSC-friendly | Overkill for this use case |
| TanStack Query | Excellent for server state | Designed for server state, not UI state | Use for server state instead |
| Jotai | Atomic, similar to Zustand | Smaller community, less familiar | Zustand has better docs |
| React Context | Built-in, no dependencies | Performance issues with frequent updates | Causes unnecessary re-renders |

**Implementation Notes**:
- Use Zustand for: Modal open/close states, Filter states, Command Center input
- Use TanStack Query for: Server state (tasks, user session), caching, optimistic updates

---

### Animation Library: framer-motion

**Decision**: Use framer-motion for complex UI animations

**Rationale**:
- Comprehensive animation toolkit with declarative API
- Built-in layout animations (AnimatePresence for enter/exit)
- Gesture support (drag, hover, tap) for future interactivity
- Excellent TypeScript support
- Performance optimizations (GPU acceleration, will-change)

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| AutoAnimate | Simpler API, auto-layout | Less expressive, limited control | Need complex sequences |
| React Spring | Physics-based, performant | Different mental model, steeper learning curve | Framer Motion more intuitive |
| pure CSS | No dependency, native | Complex sequences difficult, no gesture support | Insufficient for confetti, modals |
| GSAP | Most powerful | Heavy, expensive license for commercial | Overkill for this project |

**Implementation Notes**:
- Use AnimatePresence for modal slide-in/out
- Use motion.div for task card hover/glow effects
- Use layout prop for automatic layout animations when list order changes

---

### Confetti Effect: canvas-confetti

**Decision**: Use canvas-confetti for task completion celebration

**Rationale**:
- Lightweight (~5KB gzipped)
- Performant (uses HTML5 Canvas)
- Highly configurable (colors, velocity, spread)
- Easy integration with React

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| react-confetti | React wrapper, drop-in | Heavier bundle, less configurable | Lighter option available |
| react-dom-confetti | Declarative, React-friendly | Less performant (DOM-based) | Canvas more performant |
| Custom implementation | Full control, no dependency | Time-consuming, reinventing wheel | Unnecessary complexity |

**Implementation Notes**:
- Trigger on task completion (User Story 5)
- Custom colors: cyan (#00f5ff) and purple (#a855f7) to match brand
- Limit particle count for performance
- Auto-stop after 2 seconds

---

### Form Handling: react-hook-form + zod

**Decision**: Use react-hook-form with zod validation

**Rationale**:
- react-hook-form: Minimal re-renders, performant by default
- zod: TypeScript-first schema validation, excellent error messages
- Seamless integration between the two libraries
- Validation runs on both client and server (type safety)

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| Formik | Battle-tested, feature-rich | Heavier, older API, more rerenders | Newer alternatives better |
| TanKit Form | Modern, TanStack ecosystem | Still evolving, less mature | react-hook-form more stable |
| Controller-only (no validation library) | Simplest | Manual validation, error-prone | Type safety important |

**Implementation Notes**:
- Task creation modal: Use react-hook-form with zod schema
- Real-time validation: Trigger on blur, show errors immediately
- Server-side validation: Re-use zod schemas on FastAPI backend (via Pydantic)

---

### Data Fetching: TanStack Query (React Query)

**Decision**: Use TanStack Query for server state management

**Rationale**:
- Automatic caching and background refetching
- Optimistic updates built-in
- Loading/error states managed automatically
- Excellent TypeScript support
- Works with React Server Components (use client)

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| SWR | Simpler API, lighter | Fewer features, less popular | TanStack Query more comprehensive |
| fetch + useState | No dependency, full control | Manual caching, error handling, loading states | Too much boilerplate |
| RTK Query | Bundled with Redux Toolkit | Heavy, requires full Redux setup | Overkill for this app |

**Implementation Notes**:
- Query keys: `['tasks']`, `['task', id]`
- Mutations: Create, update, delete, toggle complete
- Optimistic updates: Show immediate feedback, rollback on error
- Stale time: 30 seconds for task list

---

### Date Picker: shadcn/ui calendar (react-day-picker)

**Decision**: Use shadcn/ui calendar component (built on react-day-picker)

**Rationale**:
- Consistent with design system (shadcn/ui)
- Accessible by default (keyboard navigation, ARIA labels)
- Customizable styling via Tailwind
- Supports date ranges, disabled dates, localization

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| react-datepicker | Feature-rich | Older UI, harder to style consistently | shadcn/ui more modern |
| HTML input[type="date"] | Native, no dependency | Inconsistent across browsers, hard to style | Poor UX on some browsers |
| MUI DatePicker | Comprehensive | Heavy dependency, different design system | shadcn/ui already chosen |

**Implementation Notes**:
- Due dates: Date only (no time for Phase II)
- Human-readable display: "Today", "Tomorrow", "Jan 15", "Overdue"
- Styling: Glassmorphism variant with cyan/purple accents

---

### API Client: fetch with Zustand wrapper

**Decision**: Use native fetch with Zustand store for API state

**Rationale**:
- Native browser API, no additional dependency
- Full control over request/response handling
- JWT token management in one place (Zustand store)
- TanStack Query handles caching, so fetch only needs transport layer

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| axios | Automatic JSON, interceptors | Additional dependency (~15KB) | Fetch is sufficient |
| ky | Lightweight, type-safe | Less familiar, smaller community | Fetch is standard |
| ofetch | Tiny, promise-based | Abandoned project | Use standard API |

**Implementation Notes**:
- Create `lib/api.ts` with typed fetch wrappers
- Automatically include JWT from Zustand store
- Handle 401 responses (redirect to login)
- Type definitions from contracts/frontend-api.ts

---

### JWT Storage: httpOnly cookies (Better Auth)

**Decision**: Use httpOnly cookies managed by Better Auth

**Rationale**:
- Secure against XSS attacks (JavaScript cannot access cookies)
- Automatic CSRF protection
- Better Auth handles cookie management transparently
- No manual token refresh logic needed

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| localStorage | Easy to access, persists | Vulnerable to XSS | Security risk |
| sessionStorage | Cleared on close | Vulnerable to XSS | Security risk |
| memory | Securest | Lost on refresh | Poor UX |

**Implementation Notes**:
- Better Auth session cookie: httpOnly, secure, sameSite=lax
- JWT for API communication: Stored in session cookie
- Frontend: Access via Better Auth client (`auth.ts`)

---

## Backend Technology Decisions

### Async Database Access: asyncpg with SQLModel

**Decision**: Use SQLModel with asyncpg driver for async database operations

**Rationale**:
- SQLModel: Pydantic + SQLAlchemy, excellent type hints
- asyncpg: Fastest PostgreSQL driver, fully async
- Connection pooling built-in
- Type safety from database to API

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| SQLAlchemy 2.0 async | Mature, feature-rich | More verbose than SQLModel | SQLModel simpler |
| Tortoise ORM | Fully async, fast | Less mature, smaller community | SQLModel more standard |
| Databases (core) | Simple API | Synchronous only | Need async for FastAPI |

**Implementation Notes**:
- Use `SQLModel` for table definitions
- Use `AsyncSession` with asyncpg engine
- Connection pooling via `create_async_engine`

---

### JWT Implementation: python-jose + passlib

**Decision**: Use python-jose for JWT, passlib with bcrypt for passwords

**Rationale**:
- python-jose: JWS/JWE implementation, supports Pydantic
- passlib: Password hashing, supports multiple algorithms
- bcrypt: Proven, secure, widely used
- Better Auth handles frontend JWT generation

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| PyJWT | Simple API | Less actively maintained | python-jose more modern |
| authlib | Comprehensive | Heavier, more complex | Simpler options sufficient |
| argon2 | Memory-hard, secure | Slower than bcrypt | bcrypt sufficient for hackathon |

**Implementation Notes**:
- JWT secret: Shared `BETTER_AUTH_SECRET` env var
- Algorithm: HS256
- Expiry: 7 days
- Password hashing: bcrypt with cost factor 12

---

## Testing Decisions

### Backend Testing: pytest + httpx

**Decision**: Use pytest with httpx for FastAPI testing

**Rationale**:
- pytest: De facto standard, fixtures, plugins
- httpx: Async HTTP client for testing FastAPI
- FastAPI TestClient: Built-in, but httpx more realistic

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| unittest | Built-in | More verbose, less powerful | pytest preferred |
| FastAPI TestClient | Official | Sync-only, not realistic for async | httpx async |

### Frontend Testing: Vitest + Playwright

**Decision**: Use Vitest for unit tests, Playwright for E2E

**Rationale**:
- Vitest: Fast, Jest-compatible, works with Vite
- Playwright: Cross-browser, reliable, excellent debugging
- Both have excellent TypeScript support

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|-------|------------------|
| Jest | Standard, mature | Slower than Vitest | Vitest faster |
| Cypress | Popular, good UI | Heavier, slower | Playwright faster |

---

## Research Summary

All technology decisions made with:
1. **Constitution alignment**: Every choice complies with Section 5.2 (Phase II stack)
2. **Phase isolation**: No Phase III features selected
3. **AI readiness**: Database schema预留 (reserved) fields for Phase III
4. **Performance**: Lightweight libraries, async operations, optimization strategies
5. **Developer experience**: TypeScript-first, great documentation, active communities

## Next Steps

1. Create data-model.md with complete database schema
2. Create API contracts in contracts/ directory
3. Create quickstart.md with setup instructions
4. Run update-agent-context.sh to update Claude Code context
