---
name: "cloud-native-blueprint"
description: "Generate cloud-native deployment blueprints (Dockerfiles, K8s manifests, Helm charts) from application code. Use for spec-driven infrastructure automation (Phase IV+, Bonus +200 points)."
version: "1.0.0"
---

# Cloud-Native Blueprint Generation Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions deployment blueprints or infrastructure generation
- Implementation requires Dockerfiles, K8s manifests, or Helm charts
- User asks about containerizing applications or cloud deployment
- Phase IV/V infrastructure automation begins
- Bonus feature: Cloud-Native Blueprints (+200 points) implementation

## How This Skill Works

Step-by-step workflow:
1. **Analyze Application**: Detect app type (FastAPI, Next.js, etc.)
2. **Generate Dockerfile**: Multi-stage build with best practices
3. **Generate K8s Manifests**: Deployment, Service, ConfigMap
4. **Generate Helm Chart**: Parameterized deployment package
5. **Validate Output**: Run `helm lint` and `kubectl --dry-run`

## Output Format

Provide structured output:
- **Application Type**: Detected framework/runtime
- **Dockerfile**: Multi-stage build configuration
- **K8s Resources**: Deployment, Service, Ingress
- **Helm Chart**: Complete chart structure
- **Validation**: Lint and dry-run results

## Constraints and Rules

- ALWAYS use multi-stage builds for smaller images
- ALWAYS run as non-root user in containers
- Include health checks and resource limits
- Use ConfigMaps for configuration, Secrets for credentials
- Generated charts MUST pass `helm lint`
- This skill applies to Phase IV+ only

## Blueprint Architecture

```
Application Code
       │
       ▼
┌──────────────────┐
│  Blueprint Skill │
│  ┌────────────┐  │
│  │ Analyze    │  │
│  │ Generate   │  │
│  │ Validate   │  │
│  └────────────┘  │
└──────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│              Generated Artifacts          │
│  ┌────────────┐  ┌────────────────────┐  │
│  │ Dockerfile │  │ k8s/               │  │
│  │            │  │  ├─ deployment.yaml│  │
│  │            │  │  ├─ service.yaml   │  │
│  │            │  │  └─ ingress.yaml   │  │
│  └────────────┘  └────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ helm/                              │  │
│  │  ├─ Chart.yaml                     │  │
│  │  ├─ values.yaml                    │  │
│  │  └─ templates/                     │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Example: FastAPI Backend Blueprint

**Input**: "Generate cloud-native blueprints for the FastAPI backend"

**Output**:

### 1. Dockerfile (Multi-Stage)

```dockerfile
# backend/Dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install UV for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

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

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes Deployment

```yaml
# k8s/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
        - name: backend
          image: todo-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: todo-secrets
                  key: database-url
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: todo-secrets
                  key: auth-secret
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### 3. Kubernetes Service

```yaml
# k8s/backend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

### 4. Helm Chart Structure

```
k8s/helm/todo-app/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── ingress.yaml
│   ├── secrets.yaml
│   └── configmap.yaml
```

### 5. Helm Chart.yaml

```yaml
# k8s/helm/todo-app/Chart.yaml
apiVersion: v2
name: todo-app
description: Evolution of Todo - Full Stack Application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - fastapi
  - nextjs
  - kubernetes
maintainers:
  - name: Evolution of Todo Team
```

### 6. Helm values.yaml

```yaml
# k8s/helm/todo-app/values.yaml
# Backend Configuration
backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
    targetPort: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# Frontend Configuration
frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
    targetPort: 3000
  resources:
    requests:
      memory: "128Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "200m"

# Ingress Configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

# Secrets (reference only - actual values in sealed secrets)
secrets:
  databaseUrl: ""
  authSecret: ""
  openaiApiKey: ""
```

### 7. Helm Template Example

```yaml
# k8s/helm/todo-app/templates/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      component: backend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        component: backend
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.backend.service.targetPort }}
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
```

## Next.js Frontend Blueprint

Similar structure with:
- Multi-stage Dockerfile (build + runtime)
- Standalone output mode for smaller images
- Environment variable injection at runtime

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

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

## Validation Commands

```bash
# Validate Helm chart
helm lint k8s/helm/todo-app/

# Dry-run Kubernetes deployment
helm template todo-app k8s/helm/todo-app/ | kubectl apply --dry-run=client -f -

# Build Docker images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

## Reference: Best Practices Applied

| Practice | Implementation |
|----------|----------------|
| Multi-stage builds | Separate build and runtime stages |
| Non-root user | `USER appuser` in Dockerfile |
| Health checks | Liveness and readiness probes |
| Resource limits | CPU and memory constraints |
| ConfigMaps | External configuration |
| Secrets | Sensitive data management |
| Helm templating | Parameterized deployments |
