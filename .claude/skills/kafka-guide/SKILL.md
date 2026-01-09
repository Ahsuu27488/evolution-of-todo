---
name: kafka-guide
description: Fetch Apache Kafka documentation and apply messaging best practices. Use when implementing producers, consumers, or event streaming (Phase V).
version: 2.0.0
---

# Apache Kafka Mastery Skill

## Context7 Research Results

**Library ID**: `/dpkp/kafka-python`
**Source**: https://kafka-python.readthedocs.io
**Reputation**: High

## When to Use This Skill

Activation triggers:
- Implementing Kafka producers/consumers
- Setting up event streaming
- Configuring message topics
- Phase V event-driven architecture

## Core Patterns

### Producer

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=str.encode,
    acks='all',  # Wait for all replicas
    retries=3,
)

def send_task_event(task_id: int, event_type: str, data: dict):
    """Send task event to Kafka."""
    message = {
        'event_type': event_type,
        'task_id': task_id,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    producer.send(
        'task-events',
        key=str(task_id),
        value=message
    )
    producer.flush()

# Usage
send_task_event(123, 'TASK_CREATED', {'title': 'Buy milk'})
```

### Consumer with Group

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'task-events',
    bootstrap_servers=['kafka:9092'],
    group_id='task-processor',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    key_deserializer=lambda m: m.decode('utf-8'),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
)

for message in consumer:
    event_type = message.value.get('event_type')
    task_id = message.key

    if event_type == 'TASK_CREATED':
        handle_task_created(message.value)
    elif event_type == 'TASK_COMPLETED':
        handle_task_completed(message.value)
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Consumer groups | One group per service type |
| Partitioning | Key by user_id for even distribution |
| Retention | Configure based on data criticality |
| Dead letter topics | Failed messages go to DLT |
| Idempotent consumers | Handle duplicate messages |

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Producer | "KafkaProducer send acks retries" |
| Consumer | "KafkaConsumer group_id offset_reset" |
| Topics | "create topic partitions replication" |
| Serialization | "json deserializer value_serializer" |
