---
description: "Deploy applications to Kubernetes with Helm charts. Use when implementing Phase IV/V deployments."
handoffs:
  - label: Monitor Deployment
    agent: general-purpose
    prompt: Monitor the Kubernetes deployment status and logs
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Deploy the todo chatbot application to Kubernetes clusters (Minikube for Phase IV, cloud for Phase V). This agent handles containerization, Helm chart creation, and deployment automation.

This agent is invoked when:
- User needs to deploy to Minikube (Phase IV)
- User needs to deploy to AKS/GKE/OKE (Phase V)
- Creating Docker images or Helm charts for the application

## Prerequisites

Before this agent runs:
- [ ] Phase III chatbot is complete and working locally
- [ ] Docker Desktop installed and running
- [ ] Minikube installed (Phase IV) or cloud cluster configured (Phase V)
- [ ] kubectl configured to target cluster

## Workflow Phases

### Phase 1: Containerization

**Goal**: Create Docker images for frontend and backend

**Steps**:
1. Fetch Docker best practices via Context7
2. Create Dockerfile for backend (FastAPI + MCP server)
3. Create Dockerfile for frontend (Next.js)
4. Build and test images locally with `docker build`

**Output**: Working Docker images for both services

### Phase 2: Helm Charts

**Prerequisites**: Phase 1 complete

**Goal**: Create Helm charts for Kubernetes deployment

**Steps**:
1. Fetch Helm chart structure via Context7
2. Create chart for backend with ConfigMaps and Secrets
3. Create chart for frontend with ingress configuration
4. Define values.yaml for environment-specific settings

**Output**: Helm charts at `k8s/helm/`

### Phase 3: Deployment

**Prerequisites**: Phase 2 complete

**Goal**: Deploy to target Kubernetes cluster

**Steps**:
1. Push images to container registry (if cloud deployment)
2. Install Helm charts to cluster
3. Verify pods are running with `kubectl get pods`
4. Test application endpoints

**Output**: Running application on Kubernetes

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| Backend Dockerfile | `backend/Dockerfile` | FastAPI container image |
| Frontend Dockerfile | `frontend/Dockerfile` | Next.js container image |
| Helm Charts | `k8s/helm/` | Kubernetes deployment charts |
| Deploy Script | `k8s/deploy.sh` | Automated deployment script |

## Quality Gates

Before completing, verify:
- [ ] Docker images build without errors
- [ ] Helm charts pass `helm lint`
- [ ] Pods reach Running state
- [ ] Application accessible via cluster IP/ingress

## Error Handling

| Error Type | Response |
|------------|----------|
| Docker build fails | FIX - Check Dockerfile and dependencies |
| Pod CrashLoopBackOff | DEBUG - Check logs with `kubectl logs` |
| Helm install fails | FIX - Validate chart with `helm template` |

## Key Rules

- Use multi-stage Docker builds for smaller images
- Never hardcode secrets in Dockerfiles or charts
- Use ConfigMaps for non-sensitive configuration
- Use Secrets for sensitive data (API keys, DB credentials)
