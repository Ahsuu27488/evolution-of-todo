---
description: "Generate cloud-native deployment blueprints (Dockerfiles, K8s manifests, Helm charts) for spec-driven infrastructure automation. Use when deploying applications to Kubernetes (Phase IV+, Bonus +200 points)."
handoffs:
  - label: Deploy to Kubernetes
    agent: k8s-deployer
    prompt: Deploy the generated Helm charts to Kubernetes cluster
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Generate production-ready cloud-native deployment blueprints from application code. This agent analyzes existing application structure and generates Dockerfiles, Kubernetes manifests, and Helm charts following best practices. This is a key differentiator for the hackathon bonus points (+200 for Cloud-Native Blueprints).

This agent is invoked when:
- User needs to containerize frontend or backend applications
- User requests Kubernetes deployment configuration
- User wants to generate Helm charts for the application
- Phase IV deployment preparation begins

## Prerequisites

Before this agent runs:
- [ ] Application code exists (backend/ and/or frontend/)
- [ ] Application can run locally (verified working)
- [ ] Docker Desktop or Docker Engine installed
- [ ] Phase III chatbot complete (for full-stack blueprints)

## Workflow Phases

### Phase 1: Application Analysis

**Goal**: Understand application structure and dependencies

**Steps**:
1. Scan `backend/` for Python dependencies (pyproject.toml, requirements.txt)
2. Scan `frontend/` for Node.js dependencies (package.json)
3. Identify application entry points (main.py, server.js)
4. Detect environment variables from .env.example
5. List services that need to be containerized

**Output**: Application manifest with identified components and dependencies

### Phase 2: Dockerfile Generation

**Prerequisites**: Phase 1 complete

**Goal**: Generate optimized Dockerfiles for each service

**Steps**:
1. Fetch Docker best practices via Context7 (if available)
2. Generate multi-stage Dockerfile for FastAPI backend
   - Build stage: Install dependencies with UV
   - Runtime stage: Minimal Python image with non-root user
3. Generate multi-stage Dockerfile for Next.js frontend
   - Build stage: npm install and build
   - Runtime stage: Standalone output with non-root user
4. Add health check endpoints to each Dockerfile
5. Create docker-compose.yml for local development

**Output**: Dockerfiles at `backend/Dockerfile` and `frontend/Dockerfile`, docker-compose.yml

### Phase 3: Kubernetes Manifest Generation

**Prerequisites**: Phase 2 complete

**Goal**: Generate Kubernetes deployment manifests

**Steps**:
1. Fetch Kubernetes best practices via Context7
2. Generate Deployment manifests with:
   - Resource limits (CPU, memory)
   - Liveness and readiness probes
   - Environment variable injection from ConfigMaps/Secrets
3. Generate Service manifests (ClusterIP type)
4. Generate Ingress manifest for external access
5. Generate Secret and ConfigMap templates

**Output**: K8s manifests at `k8s/manifests/`

### Phase 4: Helm Chart Generation

**Prerequisites**: Phase 3 complete

**Goal**: Package deployments as parameterized Helm charts

**Steps**:
1. Fetch Helm best practices via Context7
2. Create Helm chart structure at `k8s/helm/todo-app/`
3. Generate Chart.yaml with metadata
4. Generate values.yaml with configurable parameters:
   - Replica counts
   - Image repositories and tags
   - Resource limits
   - Ingress hosts
5. Convert K8s manifests to Helm templates with variable substitution
6. Add helper templates (_helpers.tpl)
7. Validate with `helm lint`

**Output**: Complete Helm chart at `k8s/helm/todo-app/`

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| Backend Dockerfile | `backend/Dockerfile` | Multi-stage FastAPI container |
| Frontend Dockerfile | `frontend/Dockerfile` | Multi-stage Next.js container |
| Docker Compose | `docker-compose.yml` | Local development orchestration |
| K8s Manifests | `k8s/manifests/` | Raw Kubernetes YAML files |
| Helm Chart | `k8s/helm/todo-app/` | Parameterized Helm chart |
| Deploy Script | `scripts/deploy.sh` | Convenience deployment script |

## Quality Gates

Before completing, verify:
- [ ] Docker images build successfully: `docker build -t todo-backend ./backend`
- [ ] Docker images build successfully: `docker build -t todo-frontend ./frontend`
- [ ] Helm chart passes linting: `helm lint k8s/helm/todo-app/`
- [ ] K8s dry-run succeeds: `helm template todo k8s/helm/todo-app/ | kubectl apply --dry-run=client -f -`
- [ ] All containers run as non-root user
- [ ] Health checks are configured
- [ ] Resource limits are set

## Error Handling

| Error Type | Response |
|------------|----------|
| No application code found | ERROR - Require backend/ or frontend/ directory |
| Missing pyproject.toml | WARNING - Create basic pyproject.toml from imports |
| Missing package.json | WARNING - Create basic package.json from source |
| Helm lint fails | FIX - Address linting errors before proceeding |
| Docker build fails | DEBUG - Check Dockerfile syntax and dependencies |

## Key Rules

- ALWAYS use multi-stage builds for smaller images
- ALWAYS run containers as non-root user
- NEVER hardcode secrets in Dockerfiles or manifests
- Use ConfigMaps for configuration, Secrets for credentials
- Include resource limits in all deployments
- Use Context7 for all framework documentation

---

## Blueprint Templates

### Backend Dockerfile Template

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . .
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile Template

```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app
RUN adduser -D appuser
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static
COPY --from=builder --chown=appuser:appuser /app/public ./public
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

### Helm values.yaml Template

```yaml
backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
  resources:
    requests: { memory: "256Mi", cpu: "100m" }
    limits: { memory: "512Mi", cpu: "500m" }

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
  resources:
    requests: { memory: "128Mi", cpu: "50m" }
    limits: { memory: "256Mi", cpu: "200m" }

ingress:
  enabled: true
  hosts:
    - host: todo.local
      paths: ["/api:backend", "/:frontend"]
```

---

## Post-Completion: PHR Creation

As the main request completes, create a PHR (Prompt History Record):

1) **Stage**: misc (infrastructure work)

2) **Title**: "Generated Cloud-Native Blueprints"

3) **Route**: `history/prompts/<feature-name>/` or `history/prompts/general/`

4) **Create PHR**: Run `.specify/scripts/bash/create-phr.sh --title "generated-cloud-native-blueprints" --stage misc --json`
