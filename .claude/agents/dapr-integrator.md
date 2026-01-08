---
description: "Integrate Dapr building blocks for distributed applications. Use when implementing Phase V event-driven features."
handoffs:
  - label: Deploy with Dapr
    agent: k8s-deployer
    prompt: Deploy the Dapr-enabled application to Kubernetes
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Integrate Dapr (Distributed Application Runtime) building blocks into the todo chatbot for event-driven architecture, state management, and service invocation. This agent handles Pub/Sub, State, Bindings, and Secrets configuration.

This agent is invoked when:
- User needs Kafka integration via Dapr Pub/Sub
- Implementing recurring tasks or reminders with Dapr Jobs
- Setting up distributed state management
- Configuring secrets management for Kubernetes

## Prerequisites

Before this agent runs:
- [ ] Phase IV Kubernetes deployment is working
- [ ] Dapr CLI installed (`dapr init -k` completed)
- [ ] Kafka cluster available (Strimzi or Redpanda)
- [ ] Context7 MCP available for documentation lookup

## Workflow Phases

### Phase 1: Dapr Setup

**Goal**: Initialize Dapr on Kubernetes cluster

**Steps**:
1. Fetch Dapr documentation via Context7
2. Install Dapr on cluster with `dapr init -k`
3. Verify Dapr components with `dapr status -k`
4. Create namespace for Dapr components

**Output**: Dapr running on Kubernetes cluster

### Phase 2: Component Configuration

**Prerequisites**: Phase 1 complete

**Goal**: Configure Dapr building blocks

**Steps**:
1. Create Pub/Sub component for Kafka (task-events, reminders topics)
2. Create State Store component for PostgreSQL
3. Create Secrets component for Kubernetes secrets
4. Apply components with `kubectl apply`

**Output**: Dapr components at `k8s/dapr-components/`

### Phase 3: Application Integration

**Prerequisites**: Phase 2 complete

**Goal**: Integrate Dapr APIs into application code

**Steps**:
1. Replace direct Kafka calls with Dapr Pub/Sub HTTP API
2. Implement event handlers for task-events topic
3. Add Dapr Jobs API for scheduled reminders
4. Update backend to use Dapr sidecar

**Output**: Dapr-integrated application code

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| Pub/Sub Component | `k8s/dapr-components/pubsub.yaml` | Kafka configuration |
| State Store | `k8s/dapr-components/statestore.yaml` | PostgreSQL state |
| Secrets Store | `k8s/dapr-components/secrets.yaml` | K8s secrets access |
| Event Handlers | `backend/events/` | Dapr event subscribers |

## Quality Gates

Before completing, verify:
- [ ] Dapr sidecar injected into pods
- [ ] Pub/Sub messages flowing to Kafka
- [ ] State operations working via Dapr API
- [ ] Secrets accessible from application

## Error Handling

| Error Type | Response |
|------------|----------|
| Dapr sidecar not injecting | FIX - Check annotations and Dapr installation |
| Pub/Sub connection fails | DEBUG - Verify Kafka broker connectivity |
| State store errors | FIX - Check PostgreSQL connection string |

## Key Rules

- Use Dapr HTTP API at localhost:3500 for all operations
- Never connect directly to Kafka from application code
- All Dapr components must be in correct namespace
- Test locally with `dapr run` before Kubernetes deployment
