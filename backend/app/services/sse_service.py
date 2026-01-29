"""SSEService for Server-Sent Events streaming.

[Task]: T013
[From]: spec.md SC-001, SC-005, contracts/api.yaml §1.5
[From]: Context7 /sysid/sse-starlette for EventSourceResponse pattern
"""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Set

from sse_starlette.sse import EventSourceResponse


class SSEConnectionManager:
    """Manages active SSE connections for real-time notifications.

    [Task]: T013
    [From]: research.md SSE section, Context7 /sysid/sse-starlette

    Tracks active connections per user to enable broadcasting notifications
    to all connected clients for a specific user.
    """

    def __init__(self) -> None:
        # Maps user_id to set of queues for that user's connections
        self._connections: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: str) -> asyncio.Queue:
        """Subscribe a user to SSE notifications.

        Args:
            user_id: User ID to subscribe

        Returns:
            Queue for receiving events
        """
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()

            queue: asyncio.Queue = asyncio.Queue()
            self._connections[user_id].add(queue)

        return queue

    async def unsubscribe(self, user_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe a user from SSE notifications.

        Args:
            user_id: User ID to unsubscribe
            queue: Queue to remove
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(queue)

                # Clean up empty user entries
                if not self._connections[user_id]:
                    del self._connections[user_id]

    async def broadcast_to_user(
        self,
        user_id: str,
        event: dict[str, Any],
    ) -> None:
        """Broadcast an event to all connections for a user.

        [Task]: T013
        [From]: spec.md SC-005 - Real-time badge updates

        Args:
            user_id: User ID to broadcast to
            event: Event data to broadcast
        """
        async with self._lock:
            if user_id not in self._connections:
                return

            # Create a copy of the set to avoid modifying during iteration
            queues = list(self._connections[user_id])

        # Put event in all queues (outside lock to prevent blocking)
        for queue in queues:
            try:
                await queue.put(event)
            except Exception:
                # Queue might be closed, remove it
                await self.unsubscribe(user_id, queue)

    def get_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user.

        Args:
            user_id: User ID to check

        Returns:
            Number of active connections
        """
        return len(self._connections.get(user_id, set()))


# Global connection manager instance
_connection_manager = SSEConnectionManager()


class SSEService:
    """Service for Server-Sent Events streaming.

    [Task]: T013
    [From]: spec.md SC-001, SC-005, contracts/api.yaml §1.5
    [From]: Context7 /sysid/sse-starlette

    Provides real-time notification streaming to frontend clients.
    """

    # Ping interval to keep connections alive (seconds)
    PING_INTERVAL = 15

    @staticmethod
    def get_manager() -> SSEConnectionManager:
        """Get the global connection manager.

        Returns:
            SSEConnectionManager instance
        """
        return _connection_manager

    @staticmethod
    async def broadcast_to_user(
        user_id: str,
        event: dict[str, Any],
    ) -> None:
        """Broadcast an event to all connections for a user.

        [Task]: T013
        [From]: spec.md SC-005 - Real-time badge updates

        This is a convenience method that accesses the global manager.

        Args:
            user_id: User ID to broadcast to
            event: Event data to broadcast
        """
        await _connection_manager.broadcast_to_user(user_id, event)

    @staticmethod
    async def event_stream(
        user_id: str,
        request: Any,
    ) -> EventSourceResponse:
        """Create SSE event stream for a user.

        [Task]: T013
        [From]: Context7 /sysid/sse-starlette for EventSourceResponse pattern

        Args:
            user_id: User ID to stream notifications for
            request: FastAPI Request object for disconnect detection

        Returns:
            EventSourceResponse for SSE streaming
        """
        # Subscribe this user to notifications
        queue = await _connection_manager.subscribe(user_id)

        async def event_generator() -> AsyncGenerator[dict[str, str], None]:
            """Generate SSE events for the client.

            [From]: Context7 /sysid/sse-starlette documentation

            Yields:
                SSE event dictionaries with 'event' and 'data' keys
            """
            try:
                # Send initial connection确认
                yield {
                    "event": "connected",
                    "data": json.dumps({"user_id": user_id, "message": "SSE connected"}),
                }

                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break

                    try:
                        # Wait for new events with timeout
                        event_data = await asyncio.wait_for(
                            queue.get(),
                            timeout=SSEService.PING_INTERVAL,
                        )

                        # Send the event
                        event_type = event_data.get("event", "notification")
                        yield {
                            "event": event_type,
                            "data": json.dumps(event_data.get("data", event_data)),
                        }

                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        yield {
                            "event": "ping",
                            "data": json.dumps({"timestamp": asyncio.get_event_loop().time()}),
                        }

            finally:
                # Clean up on disconnect
                await _connection_manager.unsubscribe(user_id, queue)

        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    @staticmethod
    async def notify_unread_count(
        session: Any,
        user_id: str,
    ) -> None:
        """Send current unread count to user's SSE connections.

        [Task]: T013
        [From]: spec.md SC-005 - Unread badge update <200ms

        Args:
            session: Database session
            user_id: User ID to send count for
        """
        from app.services.notification_service import NotificationService

        unread_count = await NotificationService.get_unread_count(
            session,
            user_id,
        )

        await SSEService.broadcast_to_user(
            user_id,
            {
                "event": "notification_read_count",
                "data": {
                    "unread_count": unread_count,
                },
            },
        )
