"""
Dapr Client Wrapper for Chronos Todo Backend

This module provides a simplified interface for interacting with Dapr building blocks:
- Pub/Sub: Event publishing to Kafka
- State: Conversation state storage
- Service Invocation: Inter-service communication
- Secrets: Secure credential access

Usage:
    from app.dapr.client import DaprClient, dapr_enabled

    if dapr_enabled():
        client = DaprClient()

        # Publish event
        await client.publish_event("task-events", {"event_type": "created", "task_id": 1})

        # Save state
        await client.save_state("conversation-123", {"messages": [...]})

        # Get secret
        api_key = await client.get_secret("openai-api-key")
"""

import os
import json
import httpx
from typing import Any, Dict, Optional
from structlog import get_logger

logger = get_logger(__name__)

# Dapr configuration from environment
DAPR_ENABLED = os.getenv("DAPR_ENABLED", "false").lower() == "true"
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_GRPC_PORT = int(os.getenv("DAPR_GRPC_PORT", "50001"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0"


def dapr_enabled() -> bool:
    """Check if Dapr sidecar is enabled and available."""
    return DAPR_ENABLED


class DaprClient:
    """
    Simple HTTP-based Dapr client for Phase V integration.

    Uses Dapr's HTTP API to interact with building blocks without requiring
    the Dapr Python SDK, keeping dependencies minimal.
    """

    def __init__(self, base_url: str = DAPR_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    # ========================================================================
    # Pub/Sub (Event Publishing)
    # ========================================================================

    async def publish_event(
        self,
        topic: str,
        data: Dict[str, Any],
        pubsub_name: str = "kafka-pubsub",
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (e.g., "task-events")
            data: Event payload (will be JSON serialized)
            pubsub_name: Dapr pubsub component name

        Returns:
            True if published successfully, False otherwise
        """
        if not dapr_enabled():
            logger.debug("Dapr not enabled, skipping event publish", topic=topic)
            return False

        url = f"{self.base_url}/publish/{pubsub_name}/{topic}"

        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            logger.info("Event published successfully", topic=topic, data=data)
            return True
        except httpx.HTTPError as e:
            logger.error("Failed to publish event", topic=topic, error=str(e))
            return False

    async def publish_task_event(
        self,
        event_type: str,  # "created", "updated", "completed", "deleted"
        task_id: int,
        user_id: str,
        task_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Publish a task-related event to the task-events topic.

        Args:
            event_type: Type of task event
            task_id: ID of the task
            user_id: ID of the user who owns the task
            task_data: Optional full task data

        Returns:
            True if published successfully
        """
        event = {
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": None,  # Will be set by consumer
        }
        if task_data:
            event["task_data"] = task_data

        return await self.publish_event("task-events", event)

    async def publish_reminder(
        self,
        task_id: int,
        user_id: str,
        title: str,
        due_at: str,
        remind_at: str,
    ) -> bool:
        """
        Publish a reminder event to the reminders topic.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            title: Task title
            due_at: When the task is due
            remind_at: When to send the reminder

        Returns:
            True if published successfully
        """
        event = {
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "due_at": due_at,
            "remind_at": remind_at,
            "timestamp": None,
        }

        return await self.publish_event("reminders", event)

    async def publish_task_update(
        self,
        task_id: int,
        user_id: str,
        update_type: str,
        data: Dict[str, Any],
    ) -> bool:
        """
        Publish a task update event for real-time client sync.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            update_type: Type of update
            data: Update data

        Returns:
            True if published successfully
        """
        event = {
            "task_id": task_id,
            "user_id": user_id,
            "update_type": update_type,
            "data": data,
            "timestamp": None,
        }

        return await self.publish_event("task-updates", event)

    # ========================================================================
    # State Management
    # ========================================================================

    async def save_state(
        self,
        key: str,
        value: Dict[str, Any],
        state_store_name: str = "statestore",
    ) -> bool:
        """
        Save state to the Dapr state store.

        Args:
            key: State key (e.g., "conversation-123")
            value: State value (will be JSON serialized)
            state_store_name: Dapr state store component name

        Returns:
            True if saved successfully
        """
        if not dapr_enabled():
            return False

        url = f"{self.base_url}/state/{state_store_name}"
        state = [{"key": key, "value": value}]

        try:
            response = await self.client.post(url, json=state)
            response.raise_for_status()
            logger.debug("State saved successfully", key=key)
            return True
        except httpx.HTTPError as e:
            logger.error("Failed to save state", key=key, error=str(e))
            return False

    async def get_state(
        self,
        key: str,
        state_store_name: str = "statestore",
    ) -> Optional[Dict[str, Any]]:
        """
        Get state from the Dapr state store.

        Args:
            key: State key
            state_store_name: Dapr state store component name

        Returns:
            State value or None if not found
        """
        if not dapr_enabled():
            return None

        url = f"{self.base_url}/state/{state_store_name}/{key}"

        try:
            response = await self.client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get state", key=key, error=str(e))
            return None

    async def delete_state(
        self,
        key: str,
        state_store_name: str = "statestore",
    ) -> bool:
        """
        Delete state from the Dapr state store.

        Args:
            key: State key
            state_store_name: Dapr state store component name

        Returns:
            True if deleted successfully
        """
        if not dapr_enabled():
            return False

        url = f"{self.base_url}/state/{state_store_name}/{key}"

        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.debug("State deleted successfully", key=key)
            return True
        except httpx.HTTPError as e:
            logger.error("Failed to delete state", key=key, error=str(e))
            return False

    # ========================================================================
    # Service Invocation
    # ========================================================================

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: Optional[Dict[str, Any]] = None,
        http_verb: str = "POST",
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a method on another service via Dapr service invocation.

        Args:
            app_id: Target Dapr app ID
            method_name: Method name to invoke
            data: Request body data
            http_verb: HTTP verb (GET, POST, PUT, DELETE)

        Returns:
            Response data or None if failed
        """
        if not dapr_enabled():
            return None

        url = f"{self.base_url}/invoke/{app_id}/method/{method_name}"

        try:
            if http_verb == "GET":
                response = await self.client.get(url, params=data)
            elif http_verb == "DELETE":
                response = await self.client.delete(url)
            else:
                response = await self.client.post(url, json=data)

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Service invocation failed", app_id=app_id, method=method_name, error=str(e))
            return None

    # ========================================================================
    # Secrets Management
    # ========================================================================

    async def get_secret(
        self,
        secret_name: str,
        secret_store_name: str = "kubernetes-secrets",
    ) -> Optional[str]:
        """
        Get a secret from the Dapr secret store.

        Args:
            secret_name: Name of the secret
            secret_store_name: Dapr secret store component name

        Returns:
            Secret value or None if not found
        """
        if not dapr_enabled():
            return None

        url = f"{self.base_url}/secrets/{secret_store_name}/{secret_name}"

        try:
            response = await self.client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get(secret_name)
        except httpx.HTTPError as e:
            logger.error("Failed to get secret", secret_name=secret_name, error=str(e))
            return None


# Singleton instance
_dapr_client: Optional[DaprClient] = None


async def get_dapr_client() -> DaprClient:
    """Get or create the Dapr client singleton."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
