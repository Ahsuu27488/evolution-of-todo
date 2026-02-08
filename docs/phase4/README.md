# Phase IV: Local Kubernetes Deployment

This guide covers deploying the Chronos Todo application on a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

1. **Minikube** - Local Kubernetes cluster
   ```bash
   # Install Minikube
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube

   # Start Minikube
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

2. **Helm** - Kubernetes package manager
   ```bash
   # Install Helm
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

3. **Dapr** - Distributed Application Runtime (for Phase V)
   ```bash
   # Install Dapr CLI
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash -s 1.0.0

   # Initialize Dapr on Kubernetes
   dapr init -k
   ```

4. **kubectl** - Kubernetes CLI
   ```bash
   # Install kubectl
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

## Quick Start

### 1. Build Docker Images

```bash
# Backend
docker build -t chronos-backend:latest ./backend

# Frontend
docker build -t chronos-frontend:latest ./frontend
```

### 2. Set Environment Variables

Create a `secrets.env` file (don't commit this):

```bash
# Neon PostgreSQL (existing cloud database)
NEON_DB_PASSWORD=npg_cXY2EI8DAqhx

# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Qdrant
QDRANT_API_KEY=eyJhbGci...

# Resend Email
RESEND_API_KEY=re_MycPDamK...
RESEND_WEBHOOK_SECRET=whsec_TrpKkWU...

# Better Auth
BETTER_AUTH_SECRET=mlHt/eQkNbw8oSExN56WdGS0dxwBdNGtMtG0XJ7jveE=

# VAPID Keys
VAPID_PUBLIC_KEY=BLnlI3_WvJ6cDbDuyen07L4GOcqxPZFAoJJ4z48mvaK3VC2XMSylx6xlTTUTFWTuMyvIoVMZRe43PHubaZXEysY
VAPID_PRIVATE_KEY=J4fh6gilYWT5RXJdm211piusPnlRsVVF2-vqwS3yGpA
```

### 3. Install the Helm Chart

```bash
# Deploy to Minikube
helm install chronos-todo ./helm/chronos-todo \
  --set global.neon.password=$NEON_DB_PASSWORD \
  --set global.openai.apiKey=$OPENAI_API_KEY \
  --set global.qdrant.apiKey=$QDRANT_API_KEY \
  --set global.resend.apiKey=$RESEND_API_KEY \
  --set global.resend.webhookSecret=$RESEND_WEBHOOK_SECRET \
  --namespace chronos \
  --create-namespace
```

### 4. Access the Application

```bash
# Tunnel services to access them
minikube tunnel

# Get service URLs
minikube service chronos-todo-frontend --namespace chronos --url
minikube service chronos-todo-backend --namespace chronos --url
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Minikube Kubernetes Cluster                  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Frontend    │  │  Backend     │  │     Redpanda           │ │
│  │  (Next.js)   │  │  (FastAPI)   │  │     (Kafka)            │ │
│  │              │◄─┤              │◄─┤                        │ │
│  │   Pod 1      │  │   Pod 1      │  │     Pod 1              │ │
│  └──────────────┘  └──────┬───────┘  └────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│                    ┌─────────────┐                            │
│                    │ Dapr Sidecar│                           │
│                    │  (Pod 1)    │                            │
│                    └─────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Neon    │  │  Qdrant  │  │  OpenAI  │  │   Resend     │   │
│  │  Postgres│  │  Cloud   │  │   API    │  │   Email      │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Dapr Integration (Phase V)

The backend includes Dapr sidecar integration for:

- **Pub/Sub**: Publish events to Kafka (Redpanda)
- **State**: Store conversation state in PostgreSQL
- **Secrets**: Access Kubernetes secrets
- **Service Invocation**: Call other services

### Dapr Topics

The following Kafka topics are created:

| Topic | Purpose |
|-------|---------|
| `task-events` | All task CRUD operations |
| `reminders` | Task due date reminders |
| `task-updates` | Real-time client sync |

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n chronos
kubectl describe pod <pod-name> -n chronos
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/chronos-todo-backend -n chronos

# Frontend logs
kubectl logs -f deployment/chronos-todo-frontend -n chronos

# Dapr sidecar logs
kubectl logs -f deployment/chronos-todo-backend -c daprd -n chronos
```

### Check Services

```bash
kubectl get svc -n chronos
```

### Port Forward to Localhost

```bash
# Forward frontend
kubectl port-forward -n chronos svc/chronos-todo-frontend 3000:3000

# Forward backend
kubectl port-forward -n chronos svc/chronos-todo-backend 8000:8000
```

### Common Issues

1. **Dapr sidecar not starting**
   ```bash
   # Check Dapr installation
   dapr status -k

   # Reinstall Dapr
   dapr uninstall -k
   dapr init -k
   ```

2. **Redpanda not connecting**
   ```bash
   # Check Redpanda pod
   kubectl logs -f deployment/chronos-todo-redpanda -n chronos
   ```

3. **Database connection errors**
   - Verify Neon database is accessible
   - Check connection string in secrets

## Cleanup

```bash
# Uninstall Helm release
helm uninstall chronos-todo -n chronos

# Delete namespace
kubectl delete namespace chronos

# Stop Minikube
minikube stop
```

## Next Steps

Proceed to [Phase V: Oracle Cloud Deployment](../phase5/README.md) for production deployment on Oracle Kubernetes Engine (OKE).
