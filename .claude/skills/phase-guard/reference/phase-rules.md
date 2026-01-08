# Phase Isolation Rules

Reference from Constitution §IV.4.2 - Phase Progression

## Phase I: In-Memory Console
**Allowed**: Add, Delete, Update, View, Mark Complete (in-memory only)
**Forbidden**: Databases, Files, Auth, Web, APIs

## Phase II: Full-Stack Web
**Allowed**: Phase I + Persistence, Auth, REST API
**Forbidden**: Chatbot, AI, Kubernetes

## Phase III: AI Chatbot
**Allowed**: Phase II + MCP Server, Agents SDK, ChatKit
**Forbidden**: Kubernetes, Kafka, Dapr

## Phase IV: Local K8s
**Allowed**: Phase III + Docker, Minikube, Helm
**Forbidden**: Cloud deployment, Kafka

## Phase V: Cloud Deployment
**Allowed**: All features + Kafka, Dapr, AKS/GKE/OKE
**Forbidden**: N/A (final phase)

## Decision Tree

```
Is the feature in current phase allowed list?
├── YES → Proceed with implementation
└── NO → Is it in forbidden list?
    ├── YES → BLOCK - Report phase violation
    └── NO → Check future phases
        ├── Found in future phase → BLOCK - Belongs to Phase N
        └── Not found anywhere → ASK - Feature not in spec
```
