---
name: "kubernetes-guide"
description: "Fetch Kubernetes documentation and apply deployment best practices. Use when creating K8s manifests, deployments, or services (Phase IV+)."
version: "1.0.0"
---

# Kubernetes Deployment Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Kubernetes, K8s, minikube, or kubectl
- Implementation requires creating deployment manifests
- User asks about pods, services, ingress, or K8s resources
- Phase IV deployment to Kubernetes begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Kubernetes-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/websites/kubernetes_io` and relevant topic
3. **Apply Patterns**: Use official K8s patterns for the specific resource type
4. **Validate**: Ensure manifests follow best practices (resource limits, probes, labels)

## Output Format

Provide structured output:
- **Context7 Source**: `/websites/kubernetes_io`
- **Resource Types**: K8s resources being created
- **Key Concepts**: Applied Kubernetes concepts
- **Best Practices**: Applied configurations

## Constraints and Rules

- ALWAYS include resource limits and requests
- ALWAYS add liveness and readiness probes
- Use namespaces for isolation
- Apply consistent labeling strategy
- Never use `latest` tag in production
- This skill applies to Phase IV and later only

## Example

**Input**: "Deploy the todo backend to Kubernetes"

**Output**:
```
Context7 Source: /websites/kubernetes_io (topic: deployment)
Resource Types: Deployment, Service, ConfigMap
Key Concepts:
- ReplicaSet with 3 replicas
- ClusterIP service for internal access
- ConfigMap for environment configuration
Best Practices:
- Resource limits: 256Mi memory, 200m CPU
- Readiness probe on /health endpoint
- Rolling update strategy
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `deployment` | Application deployment patterns |
| `service` | Service discovery and load balancing |
| `configmap secrets` | Configuration management |
| `ingress` | External traffic routing |
| `persistent volumes` | Storage for stateful apps |
| `horizontal pod autoscaler` | Auto-scaling |
