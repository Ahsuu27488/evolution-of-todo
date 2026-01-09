---
name: cloud-native-blueprint
description: Generate cloud-native deployment blueprints (Dockerfiles, K8s manifests, Helm charts) from application code. Use for spec-driven infrastructure automation (Phase IV+, Bonus +200 points).
version: 2.0.0
---

# Cloud-Native Blueprint Generation Skill

## Purpose

Auto-generates complete cloud-native deployment artifacts from application code:
- **Dockerfiles**: Multi-stage builds optimized for production
- **Kubernetes Manifests**: Deployment, Service, ConfigMap, Ingress
- **Helm Charts**: Parameterized deployment packages

## When to Use This Skill

Activation triggers:
- Generating deployment blueprints from code
- Creating Dockerfiles for applications
- Packaging K8s manifests as Helm charts
- Phase IV+ bonus feature (+200 points)

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
│  └────────────┘  │  ├─ service.yaml   │  │
│  ┌────────────────────────────────────┐  │
│  │ helm/                              │  │
│  │  ├─ Chart.yaml                     │  │
│  │  ├─ values.yaml                    │  │
│  │  └─ templates/                     │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Output Artifacts

### 1. Multi-Stage Dockerfile

### 2. Kubernetes Resources

- Deployment with replicas, resource limits
- Service (ClusterIP)
- ConfigMap for environment
- Secret reference for credentials
- Ingress for external access

### 3. Helm Chart

- Chart.yaml with metadata
- values.yaml with documented defaults
- templates/ with Go templating
- NOTES.txt with post-install instructions

## Validation

- `helm lint` passes
- `kubectl apply --dry-run=client` succeeds
- No secrets hardcoded
- Health checks configured
- Resource limits defined

## Best Practices Applied

| Practice | Implementation |
|----------|----------------|
| Multi-stage builds | Smaller final images |
| Non-root user | Security |
| Health checks | Readiness/liveness probes |
| Resource limits | CPU/memory constraints |
| ConfigMaps/Secrets | External configuration |
| Helm templating | Parameterized deployments |
