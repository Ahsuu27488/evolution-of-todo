"""
Correlation ID middleware for distributed tracing.

Per FR-LOG-002 through FR-LOG-005, LOG-013, LOG-015:
- Generate or propagate X-Correlation-ID header
- Bind correlation ID to async context
- Include correlation ID in all response headers
- Bind user_id from JWT to context

This enables tracing requests across:
- API calls
- MCP tool invocations
- Agent handoffs
- External API calls (OpenAI, Qdrant, Whisper)
"""

import contextvars
import uuid
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.ai.utils.logging import get_logger, set_correlation_id, set_user_id


# =============================================================================
# Configuration
# =============================================================================

CORRELATION_ID_HEADER = "X-Correlation-ID"


# =============================================================================
# Middleware
# =============================================================================

class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage correlation IDs for distributed tracing.

    Per spec.md FR-LOG-002 through FR-LOG-005:

    1. Checks incoming X-Correlation-ID header
    2. Generates new UUID v4 if not provided
    3. Binds to async context for propagation
    4. Adds to all response headers

    Example:
        # Incoming request
        GET /api/chat HTTP/1.1
        X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000

        # Outgoing response
        HTTP/1.1 200 OK
        X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
    """

    def __init__(
        self,
        app: ASGIApp,
        header_name: str = CORRELATION_ID_HEADER,
        generate_if_missing: bool = True,
    ) -> None:
        """
        Initialize correlation middleware.

        Args:
            app: ASGI application
            header_name: Header name for correlation ID
            generate_if_missing: Generate UUID if header not present
        """
        super().__init__(app)
        self.header_name = header_name
        self.generate_if_missing = generate_if_missing
        self.logger = get_logger("middleware", "CorrelationMiddleware")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Process request with correlation ID handling.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with correlation ID header
        """
        # Extract or generate correlation ID
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id and self.generate_if_missing:
            correlation_id = str(uuid.uuid4())

        # Bind to async context
        if correlation_id:
            set_correlation_id(correlation_id)

        # Log request start
        self.logger.info(
            "Request started",
            event_type="request_start",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            client_host=request.client.host if request.client else None,
        )

        # Process request
        try:
            response = await call_next(request)

            # Add correlation ID to response headers
            if correlation_id:
                response.headers[self.header_name] = correlation_id

            # Log request end
            self.logger.info(
                "Request completed",
                event_type="request_end",
                status_code=response.status_code,
            )

            return response

        except Exception as e:
            # Log error
            self.logger.error(
                "Request failed",
                event_type="request_error",
                error_type=type(e).__name__,
                error_message=str(e),
            )

            # Re-raise for error handlers
            raise


class UserIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and bind user_id from JWT.

    This middleware runs AFTER authentication middleware to
    bind the user_id to context for logging.

    Per FR-LOG-015: Use contextvars to propagate user_id across async boundaries.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize user ID middleware."""
        super().__init__(app)
        self.logger = get_logger("middleware", "UserIdMiddleware")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Extract user_id from request state (set by auth middleware).

        The simple_auth.py middleware sets request.state.user_id after
        validating the JWT token.
        """
        # Get user_id from request state (set by auth)
        user_id = getattr(request.state, "user_id", None)

        if user_id:
            set_user_id(user_id)

        # Process request
        return await call_next(request)


# =============================================================================
# Utility Functions
# =============================================================================

def get_request_correlation_id(request: Request) -> str | None:
    """
    Extract correlation ID from request headers or state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID or None
    """
    # Check headers first
    correlation_id = request.headers.get(CORRELATION_ID_HEADER)
    if correlation_id:
        return correlation_id

    # Check state (set by middleware)
    return getattr(request.state, "correlation_id", None)


def add_correlation_id_to_request(request: Request, correlation_id: str) -> None:
    """
    Add correlation ID to request state for downstream access.

    Args:
        request: FastAPI request object
        correlation_id: Correlation ID to bind
    """
    request.state.correlation_id = correlation_id
