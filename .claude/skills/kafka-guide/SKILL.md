---
name: "kafka-guide"
description: "Fetch Apache Kafka documentation and apply messaging best practices. Use when implementing producers, consumers, or event streaming (Phase V)."
version: "1.0.0"
---

# Apache Kafka Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Kafka, topics, producers, or consumers
- Implementation requires event streaming or message queues
- User asks about partitions, consumer groups, or Kafka configuration
- Phase V event-driven architecture begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Kafka-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/dpkp/kafka-python` and relevant topic
3. **Apply Patterns**: Use official Kafka patterns for producers/consumers
4. **Validate**: Ensure configuration follows Kafka best practices (partitioning, replication)

## Output Format

Provide structured output:
- **Context7 Source**: `/dpkp/kafka-python`
- **Pattern Applied**: Kafka pattern used (producer, consumer, etc.)
- **Configuration**: Key Kafka settings
- **Best Practices**: Applied optimizations

## Constraints and Rules

- ALWAYS configure appropriate replication factor for production
- ALWAYS use consumer groups for scalable consumption
- Implement idempotent producers for exactly-once semantics
- Use appropriate serialization (JSON, Avro, Protobuf)
- Configure proper retention and cleanup policies
- This skill applies to Phase V only

## Example

**Input**: "Create a Kafka consumer for todo events"

**Output**:
```
Context7 Source: /dpkp/kafka-python (topic: consumer)
Pattern Applied: Consumer Group with auto-commit
Configuration:
  from kafka import KafkaConsumer

  consumer = KafkaConsumer(
      'todo-events',
      bootstrap_servers=['kafka:9092'],
      group_id='todo-processor',
      auto_offset_reset='earliest',
      enable_auto_commit=True,
      value_deserializer=lambda x: json.loads(x.decode('utf-8'))
  )

  for message in consumer:
      process_todo_event(message.value)
Best Practices:
- Consumer group for parallel processing
- Earliest offset reset for new groups
- JSON deserialization
- Graceful shutdown handling
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `producer` | Publishing messages |
| `consumer` | Consuming messages |
| `consumer groups` | Scalable consumption |
| `partitions` | Parallel processing |
| `serialization` | Message encoding |
| `configuration` | Broker/client settings |
