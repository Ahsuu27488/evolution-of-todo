---
name: kubernetes-guide
description: Fetch Kubernetes documentation and apply deployment best practices. Use when creating K8s manifests, deployments, or services (Phase IV+).
version: 2.0.0
---

# Kubernetes Deployment Mastery Skill

## Context7 Research Results

**Library ID**: `/websites/kubernetes_io`
**Source**: https://kubernetes.io/docs
**Reputation**: High

## When to Use This Skill

Activation triggers:
- Creating Kubernetes manifests (Deployment, Service, Ingress)
- Setting up pod configurations
- Configuring health checks and probes
- Phase IV+ deployment work

## Core Manifest Patterns

### Deployment with Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
    version: v1
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
          name: http
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
            port: http
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: http
  type: ClusterIP
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
data:
  API_URL: "http://todo-backend:80"
  LOG_LEVEL: "info"
  ENVIRONMENT: "production"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@postgres:5432/todo"
  auth-secret: "your-secret-key-here"
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Resource limits | Always set requests and limits |
| Health probes | Liveness and readiness on all services |
| Labels | Consistent labeling strategy |
| Non-root | Run as non-root user in container |
| Image tag | Avoid `:latest`, use specific tags |
| Replicas | Minimum 2 for production |

## Common K8s Resources

| Resource | Purpose |
|----------|---------|
| **Deployment** | Stateless applications |
| **StatefulSet** | Stateful applications (databases) |
| **Service** | Network endpoint discovery |
| **Ingress** | External traffic routing |
| **ConfigMap** | Configuration data |
| **Secret** | Sensitive data |
| **PersistentVolume** | Storage |
| **Namespace** | Resource isolation |

## kubectl Commands

```bash
# Apply manifests
kubectl apply -f k8s/

# Get all resources
kubectl get all

# Get pods with watch
kubectl get pods -w

# Describe pod
kubectl describe pod/todo-backend-xxx

# View logs
kubectl logs -f deployment/todo-backend

# Exec into pod
kubectl exec -it todo-backend-xxx -- bash

# Port forward
kubectl port-forward deployment/todo-backend 8000:8000

# Delete resources
kubectl delete -f k8s/

# Get events
kubectl get events --sort-by='.lastTimestamp'
```

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Deployment | "Deployment replicas selector template" |
| Service | "Service ClusterIP NodePort LoadBalancer" |
| Probes | "livenessProbe readinessProbe httpGet" |
| ConfigMap Secret | "ConfigMap Secret environment variables" |
| Ingress | "Ingress nginx routing rules" |
