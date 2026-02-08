"""
Dapr Integration for Chronos Todo Backend (Phase V)

This package provides Dapr sidecar integration for:
- Event-driven architecture with Kafka (via Redpanda)
- State management for conversation caching
- Service invocation for microservices
- Secret management for secure credential access

Usage:
    from app.dapr.client import get_dapr_client, dapr_enabled

    # Publish task events
    if dapr_enabled():
        client = await get_dapr_client()
        await client.publish_task_event("created", task_id, user_id, task_data)
"""

from app.dapr.client import (
    DaprClient,
    dapr_enabled,
    get_dapr_client,
)

__all__ = [
    "DaprClient",
    "dapr_enabled",
    "get_dapr_client",
]
