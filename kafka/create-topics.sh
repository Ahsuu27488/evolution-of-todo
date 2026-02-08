#!/bin/bash
# Chronos Todo - Kafka Topics Creation Script
# Creates required Kafka topics for event-driven architecture

set -e

KAFKA_BROKER=${KAFKA_BROKER:-"localhost:9092"}
PARTITIONS=${PARTITIONS:-3}
REPLICATION_FACTOR=${REPLICATION_FACTOR:-1}

echo "Creating Kafka topics for Chronos Todo..."
echo "Broker: $KAFKA_BROKER"
echo "Partitions: $PARTITIONS"
echo "Replication Factor: $REPLICATION_FACTOR"
echo ""

# Topics to create
TOPICS=(
    "task-events"
    "reminders"
    "task-updates"
)

# Check if rpk is available (Redpanda CLI)
if command -v rpk &> /dev/null; then
    echo "Using rpk (Redpanda CLI)..."
    for topic in "${TOPICS[@]}"; do
        echo "Creating topic: $topic"
        rpk topic create "$topic" \
            --partitions "$PARTITIONS" \
            --replication-factor "$REPLICATION_FACTOR" \
            --brokers "$KAFKA_BROKER" || echo "Topic $topic may already exist"
    done
# Check if kafka-topics is available (Kafka CLI)
elif command -v kafka-topics &> /dev/null; then
    echo "Using kafka-topics (Kafka CLI)..."
    for topic in "${TOPICS[@]}"; do
        echo "Creating topic: $topic"
        kafka-topics --create \
            --bootstrap-server "$KAFKA_BROKER" \
            --topic "$topic" \
            --partitions "$PARTITIONS" \
            --replication-factor "$REPLICATION_FACTOR" || echo "Topic $topic may already exist"
    done
# Use Docker exec if available
elif command -v docker &> /dev/null; then
    echo "Using Docker to access Kafka..."
    for topic in "${TOPICS[@]}"; do
        echo "Creating topic: $topic"
        docker exec -it chronos-redpanda rpk topic create "$topic" \
            --partitions "$PARTITIONS" \
            --replication-factor "$REPLICATION_FACTOR" || echo "Topic $topic may already exist"
    done
else
    echo "Error: No Kafka CLI tool found (rpk, kafka-topics, or docker)"
    exit 1
fi

echo ""
echo "Topics created successfully!"
echo ""
echo "Listing topics:"
if command -v rpk &> /dev/null; then
    rpk topic list --brokers "$KAFKA_BROKER"
elif command -v kafka-topics &> /dev/null; then
    kafka-topics --list --bootstrap-server "$KAFKA_BROKER"
elif command -v docker &> /dev/null; then
    docker exec -it chronos-redpanda rpk topic list
fi
