---
name: "dapr-guide"
description: "Fetch Dapr documentation and apply distributed systems best practices. Use when implementing pub/sub, state, or service invocation (Phase V)."
version: "1.0.0"
---

# Dapr Integration Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Dapr, pub/sub, or event-driven architecture
- Implementation requires service-to-service communication
- User asks about state management, secrets, or Dapr sidecars
- Phase V distributed systems development begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Dapr-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/websites/dapr_io` and relevant topic
3. **Apply Patterns**: Use official Dapr patterns for the specific building block
4. **Validate**: Ensure configuration follows Dapr best practices (components, sidecars)

## Output Format

Provide structured output:
- **Context7 Source**: `/websites/dapr_io`
- **Building Block**: Dapr capability used (pub/sub, state, etc.)
- **Component Config**: YAML configuration for Dapr component
- **Best Practices**: Applied patterns

## Constraints and Rules

- ALWAYS use Dapr building blocks via HTTP/gRPC sidecar
- ALWAYS define component YAML for each building block
- Use scopes to restrict component access
- Implement proper error handling and retries
- Configure appropriate message TTL for pub/sub
- This skill applies to Phase V only

## Example

**Input**: "Set up Kafka pub/sub with Dapr"

**Output**:
```
Context7 Source: /websites/dapr_io (topic: pubsub kafka)
Building Block: Pub/Sub
Component Config:
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
Best Practices:
- Consumer group for load balancing
- Dead letter topic for failed messages
- Retry policy with exponential backoff
- CloudEvents format for messages
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `pubsub` | Event-driven messaging |
| `state management` | Distributed state store |
| `service invocation` | Service-to-service calls |
| `secrets` | Secret management |
| `configuration` | Centralized config |
| `bindings` | External system triggers |
