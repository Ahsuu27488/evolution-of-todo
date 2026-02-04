"""
Rate limiting middleware for API endpoints.

Per FR-089: System MUST implement per-user rate limiting at 30 requests/minute,
return 429 with retry-after header when exceeded.

Uses sliding window algorithm for accurate rate limiting.
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.ai.utils.logging import get_logger


# =============================================================================
# Configuration
# =============================================================================

# Per spec.md FR-089
DEFAULT_RATE_LIMIT = 30  # requests per minute per user
DEFAULT_WINDOW_SECONDS = 60

# Endpoint-specific limits (can override default)
ENDPOINT_LIMITS = {
    "/api/chat": 30,  # Chat endpoint: 30 req/min
    "/api/chat/transcribe": 10,  # Voice transcription: 10 req/min (expensive)
}


# =============================================================================
# In-Memory Store (for production, use Redis)
# =============================================================================

@dataclass
class RateLimitEntry:
    """Rate limit entry for a user."""

    requests: deque = field(default_factory=deque)  # Timestamps of requests
    blocked_until: float | None = None  # Unix timestamp when block expires


class RateLimiterStore:
    """
    In-memory store for rate limit tracking.

    For production deployment with multiple instances, use Redis or similar.
    This implementation uses memory with automatic cleanup.

    Structure: {user_id: {endpoint: RateLimitEntry}}
    """

    _store: dict[str, dict[str, RateLimitEntry]] = defaultdict(lambda: defaultdict(RateLimitEntry))
    _last_cleanup: float = time.time()

    @classmethod
    def get_entry(cls, user_id: str, endpoint: str) -> RateLimitEntry:
        """Get rate limit entry for user+endpoint."""
        return cls._store[user_id][endpoint]

    @classmethod
    def cleanup_old_entries(cls, window_seconds: int = 120) -> None:
        """Remove entries older than window to prevent memory leaks."""
        now = time.time()

        # Only cleanup every 60 seconds
        if now - cls._last_cleanup < 60:
            return

        cls._last_cleanup = now

        # Clean old entries
        for user_id in list(cls._store.keys()):
            for endpoint in list(cls._store[user_id].keys()):
                entry = cls._store[user_id][endpoint]

                # Remove entry if no requests and not blocked
                if not entry.requests and entry.blocked_until is None:
                    del cls._store[user_id][endpoint]

                # Remove user if empty
                if not cls._store[user_id]:
                    del cls._store[user_id]

    @classmethod
    def record_request(cls, user_id: str, endpoint: str, timestamp: float) -> None:
        """Record a request timestamp."""
        entry = cls.get_entry(user_id, endpoint)
        entry.requests.append(timestamp)

    @classmethod
    def is_rate_limited(
        cls,
        user_id: str,
        endpoint: str,
        limit: int,
        window_seconds: int,
        now: float,
    ) -> tuple[bool, int | None]:
        """
        Check if request should be rate limited.

        Returns:
            (is_limited, retry_after_seconds)
        """
        entry = cls.get_entry(user_id, endpoint)

        # Check if currently blocked
        if entry.blocked_until and now < entry.blocked_until:
            retry_after = int(entry.blocked_until - now) + 1
            return True, retry_after

        # Remove old requests outside the window
        cutoff = now - window_seconds
        while entry.requests and entry.requests[0] < cutoff:
            entry.requests.popleft()

        # Check if limit exceeded
        if len(entry.requests) >= limit:
            # Block until the oldest request expires
            if entry.requests:
                retry_after = int(entry.requests[0] + window_seconds - now) + 1
                entry.blocked_until = now + retry_after
                return True, retry_after

        # Reset block if passed
        entry.blocked_until = None

        return False, None


# =============================================================================
# Middleware
# =============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-user rate limiting middleware.

    Per FR-089:
    - Rate limit: 30 requests/minute per user (configurable per endpoint)
    - Returns 429 with Retry-After header when exceeded
    - Sliding window algorithm for accurate limiting

    Example:
        # Apply globally or to specific routes
        app.add_middleware(RateLimitMiddleware)

        # Request within limit
        GET /api/chat HTTP/1.1
        HTTP/1.1 200 OK

        # Request over limit
        GET /api/chat HTTP/1.1
        HTTP/1.1 429 Too Many Requests
        Retry-After: 30
    """

    def __init__(
        self,
        app: ASGIApp,
        default_limit: int = DEFAULT_RATE_LIMIT,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        endpoint_limits: dict[str, int] | None = None,
    ) -> None:
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            default_limit: Default requests per window per user
            window_seconds: Time window in seconds
            endpoint_limits: Endpoint-specific limits
        """
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.endpoint_limits = endpoint_limits or ENDPOINT_LIMITS
        self.logger = get_logger("middleware", "RateLimitMiddleware")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response or 429 if rate limited

        Raises:
            None - always returns Response
        """
        # Get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Skip rate limiting for unauthenticated requests (health check, etc.)
        if not user_id:
            return await call_next(request)

        # Get endpoint limit
        endpoint = request.url.path
        limit = self.endpoint_limits.get(endpoint, self.default_limit)

        # Clean old entries periodically
        RateLimiterStore.cleanup_old_entries(self.window_seconds * 2)

        # Check rate limit
        now = time.time()
        is_limited, retry_after = RateLimiterStore.is_rate_limited(
            user_id=user_id,
            endpoint=endpoint,
            limit=limit,
            window_seconds=self.window_seconds,
            now=now,
        )

        if is_limited and retry_after is not None:
            # Log rate limit hit
            self.logger.info(
                "Rate limit exceeded",
                event_type="rate_limit_exceeded",
                user_id=user_id,
                endpoint=endpoint,
                retry_after=retry_after,
            )

            # Return 429 with Retry-After header
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        # Record this request
        RateLimiterStore.record_request(user_id, endpoint, now)

        # Process request
        return await call_next(request)


# =============================================================================
# Utility Functions
# =============================================================================

def check_rate_limit(
    user_id: str,
    endpoint: str,
    limit: int = DEFAULT_RATE_LIMIT,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> tuple[bool, int | None]:
    """
    Check if a user is rate limited for an endpoint.

    Utility function for manual rate limit checks outside middleware.

    Args:
        user_id: User ID to check
        endpoint: Endpoint path
        limit: Rate limit
        window_seconds: Time window

    Returns:
        (is_limited, retry_after_seconds)
    """
    now = time.time()
    return RateLimiterStore.is_rate_limited(user_id, endpoint, limit, window_seconds, now)


def get_rate_limit_status(
    user_id: str,
    endpoint: str,
    limit: int = DEFAULT_RATE_LIMIT,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> dict[str, int]:
    """
    Get current rate limit status for a user.

    Args:
        user_id: User ID to check
        endpoint: Endpoint path
        limit: Rate limit
        window_seconds: Time window

    Returns:
        Dict with 'remaining' and 'reset' keys
    """
    entry = RateLimiterStore.get_entry(user_id, endpoint)
    now = time.time()

    # Count requests in current window
    cutoff = now - window_seconds
    recent_count = sum(1 for ts in entry.requests if ts > cutoff)

    remaining = max(0, limit - recent_count)

    # Calculate reset time (when oldest request expires)
    if entry.requests:
        oldest = min(ts for ts in entry.requests)
        reset = int(oldest + window_seconds - now)
    else:
        reset = 0

    return {
        "remaining": remaining,
        "reset": max(0, reset),
    }
