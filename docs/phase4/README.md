# Phase IV: Local Kubernetes Deployment

This guide covers deploying the Chronos Todo application on a local Kubernetes cluster using Minikube and Helm.

## Overview

Phase IV transforms the application from a development setup to a containerized, cloud-native architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Minikube Kubernetes Cluster                    │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐                      │
│  │   Frontend     │  │   Backend       │                      │
│  │   (Next.js)    │  │   (FastAPI)      │                      │
│  │   Pod 1        │  │   Pod 1          │                      │
│  │   Port: 3000   │  │   Port: 8000      │                      │
│  └────────┬────────┘  └────────┬────────┘                      │
│           │                      │                                 │
│           └──────────┬───────────┘                             │
│                          │                                        │
│                          ▼                                        │
│               ┌────────────────────────────────┐                   │
│               │   Neon PostgreSQL (External)   │                   │
│               │   - Database                      │                   │
│               │   - User sessions                │                   │
│               └────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. Minikube Installation

```bash
# Install Minikube on Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with recommended settings
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable kubectl to use Minikube's context
minikube profile kubectl
```

### 2. Helm Installation

```bash
# Install Helm v3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

### 3. Docker Installation

```bash
# Install Docker Desktop
# https://docs.docker.com/desktop/install/linux/
```

## Quick Start

### 1. Build and Deploy

The deployment script automates the entire process:

```bash
# From project root
./scripts/deploy-minikube.sh
```

This script:
1. Checks Minikube status
2. Loads environment variables from `backend/.env`
3. Builds Docker images
4. Loads images into Minikube
5. Creates Kubernetes namespace
6. Deploys Helm chart with your configuration

### 2. Access the Application

#### Option A: Port Forwarding (Recommended for Development)

```bash
# Forward backend to localhost:8000
kubectl port-forward -n chronos svc/chronos-todo-backend 8000:8000

# Forward frontend to localhost:3000 (in a new terminal)
kubectl port-forward -n chronos svc/chronos-todo-frontend 3000:3000
```

Then visit: http://localhost:3000

#### Option B: Minikube Tunnel

```bash
# Start tunnel (exposes services via LoadBalancer)
minikube tunnel
```

Get service URLs:
```bash
minikube service chronos-todo-frontend --url -n chronos
minikube service chronos-todo-backend --url -n chronos
```

## Architecture Details

### Docker Images

| Component | Image Name | Port | Health Check |
|-----------|------------|------|---------------|
| Backend | `chronos-backend` | 8000 | `/api/health` |
| Frontend | `chronos-frontend` | 3000 | `/api/health` |

### Kubernetes Resources

| Resource | Name | Namespace |
|----------|------|-----------|
| Deployment | `chronos-todo-backend` | `chronos` |
| Deployment | `chronos-todo-frontend` | `chronos` |
| Service | `chronos-todo-backend` | `chronos` |
| Service | `chronos-todo-frontend` | `chronos` |

### Environment Configuration

All sensitive configuration is passed via Helm values at deployment time:

| Variable | Description | Source |
|----------|-------------|---------|
| `global.neon.password` | Neon database password | `.env` |
| `global.openai.apiKey` | OpenAI API key | `.env` |
| `global.qdrant.apiKey` | Qdrant vector DB key | `.env` |
| `global.resend.apiKey` | Resend email key | `.env` |
| `global.betterAuth.secret` | JWT shared secret | `.env` |
| `global.vapid.publicKey` | Web Push public key | `.env` |
| `global.vapid.privateKey` | Web Push private key | `.env` |

## Troubleshooting

### Check Pod Status

```bash
# List all pods
kubectl get pods -n chronos

# Describe specific pod
kubectl describe pod <pod-name> -n chronos

# Pod logs
kubectl logs -f deployment/chronos-todo-backend -n chronos
kubectl logs -f deployment/chronos-todo-frontend -n chronos
```

### Common Issues

#### 1. Image Pull Errors

If pods show `ErrImageNeverPull`:

```bash
# Check if images exist in Minikube
minikube image list

# Load images manually
minikube image load chronos-backend:latest
minikube image load chronos-frontend:latest
```

#### 2. CrashLoopBackOff

```bash
# Check logs for error messages
kubectl logs -f deployment/chronos-todo-backend -n chronos

# Common causes:
# - Missing environment variables
# - Database connection failure
# - Port conflicts
```

#### 3. Health Check Failures

```bash
# Check if service is running inside pod
kubectl exec -n chronos deployment/chronos-todo-backend -- curl localhost:8000/api/health

# Adjust probe thresholds in helm/chronos-todo/values.yaml if needed
```

#### 4. Minikube Out of Memory

```bash
# Stop Minikube and increase memory
minikube stop
minikube start --memory=10240 --cpus=4
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall chronos-todo -n chronos

# Delete namespace
kubectl delete namespace chronos

# Remove Docker images (optional)
docker rmi chronos-backend chronos-frontend
```

## Next Steps

After successfully deploying to Minikube:

1. **Verify all features work** - Tasks, chat, notifications
2. **Test resource limits** - Monitor memory/CPU usage
3. **Prepare for Phase V** - Cloud deployment to Oracle OKE

Proceed to [Phase V: Cloud Deployment](../phase5/README.md)
