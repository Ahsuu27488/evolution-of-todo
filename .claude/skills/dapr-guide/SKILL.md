---
name: dapr-guide
description: Fetch Dapr documentation and apply distributed systems best practices. Use when implementing pub/sub, state, or service invocation (Phase V).
version: 2.0.0
---

# Dapr Integration Mastery Skill

## Context7 Research Results

**Library ID**: `/websites/dapr_io`
**Source**: https://docs.dapr.io
**Reputation**: High

## When to Use This Skill

Activation triggers:
- Implementing Dapr sidecars
- Setting up pub/sub with Kafka
- Using Dapr state management
- Service-to-service invocation
- Phase V distributed systems

## Core Dapr Building Blocks

### Pub/Sub Component

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "todo-service"
  - name: authRequired
    value: "false"
```

### Publishing Events

```python
import dapr.clients

dapr = dapr.clients.DaprClient()

async def publish_task_event(task_id: int, event_type: str):
    """Publish task event via Dapr."""
    dapr.publish_event(
        pubsub_name='kafka-pubsub',
        topic_name='task-events',
        data=json.dumps({
            'event_type': event_type,
            'task_id': task_id,
            'timestamp': datetime.utcnow().isoformat()
        }),
    )
```

### Subscribing to Events

```yaml
# dapr/subscriptions.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    - path: /events/task
      rules:
        - match: 'event_type == "TASK_CREATED"'
          path: /events/task/created
```

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Pub/Sub | "Dapr pubsub Kafka component configuration" |
| State | "Dapr state store etcd redis" |
| Service invocation | "Dapr service invocation HTTP gRPC" |
| Secrets | "Dapr secret management component" |
