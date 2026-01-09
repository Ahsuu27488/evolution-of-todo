---
name: docker-guide
description: Fetch Docker documentation and apply containerization best practices. Use when building Dockerfiles, docker-compose, or containerizing applications (Phase IV+).
version: 2.0.0
---

# Docker Containerization Mastery Skill

## Context7 Research Results

**Library ID**: `/docker/docs`
**Source**: https://docs.docker.com
**Reputation**: High

## When to Use This Skill

Activation triggers:
- Creating Dockerfiles for applications
- Writing docker-compose configurations
- Optimizing container images
- Setting up multi-stage builds
- Phase IV+ containerization work

## Core Dockerfile Patterns

### Multi-Stage Build (Python/FastAPI)

```dockerfile
# Builder stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to a temporary location
RUN uv sync --frozen --no-dev --target /install

# Runtime stage
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy dependencies from builder
COPY --from=builder /install /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Build (Next.js)

```dockerfile
# Dependencies stage
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Builder stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Environment for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN npm run build

# Runner stage
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## Docker Compose Patterns

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL database
  postgres:
    image: postgres:16-alpine
    container_name: todo-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: todo
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todo"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-backend
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://todo:${POSTGRES_PASSWORD:-changeme}@postgres:5432/todo
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
      API_URL: http://localhost:8000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  # Next.js frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: todo-frontend
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      BETTER_AUTH_URL: http://localhost:3000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Multi-stage builds | Separate builder and runtime stages |
| Non-root user | `USER appuser` after creating |
| Health checks | `HEALTHCHECK` instruction |
| Layer caching | Copy dependency files before code |
| Minimal images | Use `slim` or `alpine` variants |
| No secrets | Use environment variables, not ARG |
| .dockerignore | Exclude unnecessary files |

## .dockerignore

```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.env.venv
.git
.gitignore
.vscode
*.md
.next
node_modules
```

## Common Commands

```bash
# Build image
docker build -t todo-backend:latest .

# Run container
docker run -p 8000:8000 todo-backend:latest

# Compose up
docker-compose up -d

# Compose down
docker-compose down -v

# View logs
docker-compose logs -f backend

# Exec into container
docker-compose exec backend bash

# Clean up
docker system prune -a
```

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Python Dockerfile | "Python multi-stage Dockerfile slim" |
| Node Dockerfile | "Next.js Docker build standalone" |
| Docker Compose | "docker compose depends_on healthcheck" |
| Optimization | "Dockerfile best practices layer caching" |
