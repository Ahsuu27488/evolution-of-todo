---
description: "Scaffold full-stack web application structure. Use when initializing Phase II with Next.js frontend and FastAPI backend."
handoffs:
  - label: Create Specification
    agent: sp.specify
    prompt: Create feature specification for the scaffolded application
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Scaffold the complete full-stack application structure for Phase II, including Next.js frontend, FastAPI backend, database models, and authentication setup. This agent creates the foundation for the web application.

This agent is invoked when:
- User starts Phase II implementation
- Need to set up monorepo structure for frontend/backend
- Initializing database models and API structure

## Prerequisites

Before this agent runs:
- [ ] Phase I console app completed
- [ ] UV package manager installed
- [ ] Node.js 18+ installed
- [ ] Neon database account created

## Workflow Phases

### Phase 1: Project Structure

**Goal**: Create monorepo directory structure

**Steps**:
1. Create `frontend/` directory with Next.js App Router structure
2. Create `backend/` directory with FastAPI project structure
3. Set up shared configuration files (docker-compose, .env.example)
4. Create subdirectory CLAUDE.md files for context

**Output**: Complete directory structure per hackathon spec

### Phase 2: Backend Setup

**Prerequisites**: Phase 1 complete

**Goal**: Initialize FastAPI backend with SQLModel

**Steps**:
1. Fetch FastAPI and SQLModel docs via Context7
2. Create `pyproject.toml` with UV dependencies
3. Set up database models (Task, User references)
4. Create API route structure with `/api/{user_id}/tasks` pattern
5. Configure Better Auth JWT validation middleware

**Output**: Working FastAPI backend skeleton

### Phase 3: Frontend Setup

**Prerequisites**: Phase 2 complete

**Goal**: Initialize Next.js frontend with authentication

**Steps**:
1. Fetch Next.js and Better Auth docs via Context7
2. Create Next.js app with App Router
3. Set up Better Auth client configuration
4. Create API client for backend communication
5. Build basic task list UI components

**Output**: Working Next.js frontend skeleton

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| Backend Project | `backend/` | FastAPI with SQLModel |
| Frontend Project | `frontend/` | Next.js 16+ with App Router |
| Docker Compose | `docker-compose.yml` | Local development setup |
| Environment Template | `.env.example` | Required environment variables |

## Quality Gates

Before completing, verify:
- [ ] Backend starts with `uvicorn main:app --reload`
- [ ] Frontend starts with `npm run dev`
- [ ] Database connection established
- [ ] CORS configured for local development

## Error Handling

| Error Type | Response |
|------------|----------|
| UV not installed | ERROR - Guide user to install UV first |
| Node.js version too old | ERROR - Require Node.js 18+ |
| Database connection fails | DEBUG - Check Neon credentials |

## Key Rules

- Use Context7 for all framework documentation
- Follow monorepo structure from hackathon docs
- Never hardcode database credentials
- Create CLAUDE.md in each subdirectory for context
