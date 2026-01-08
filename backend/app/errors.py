"""Centralized error handling for the FastAPI backend.

Provides:
- Custom exception classes with error codes
- Exception handlers for consistent API responses
- Error logging with request context
- Request ID middleware for tracking
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# =============================================================================
# Error Codes
# =============================================================================

class ErrorCode(str, Enum):
    """Error codes for programmatic error handling."""

    # Authentication errors
    UNAUTHORIZED = "UNAUTHORIZED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    MISSING_TOKEN = "MISSING_TOKEN"

    # Authorization errors
    FORBIDDEN = "FORBIDDEN"
    NOT_OWNER = "NOT_OWNER"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"

    # Server errors
    SERVER_ERROR = "SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"

    # Unknown
    UNKNOWN = "UNKNOWN"


# =============================================================================
# Error Response Model
# =============================================================================

class ErrorResponse(BaseModel):
    """Standardized error response format."""

    detail: str
    code: ErrorCode
    request_id: Optional[str] = None
    timestamp: str
    path: Optional[str] = None

    class Config:
        use_enum_values = True


# =============================================================================
# Custom Exceptions
# =============================================================================

class AppException(HTTPException):
    """Base application exception with error code support."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class AuthenticationError(AppException):
    """Authentication-related errors (401)."""

    def __init__(
        self,
        detail: str = "Authentication required",
        code: ErrorCode = ErrorCode.UNAUTHORIZED,
    ):
        super().__init__(status_code=401, detail=detail, code=code)


class AuthorizationError(AppException):
    """Authorization-related errors (403)."""

    def __init__(
        self,
        detail: str = "Not authorized to access this resource",
        code: ErrorCode = ErrorCode.FORBIDDEN,
    ):
        super().__init__(status_code=403, detail=detail, code=code)


class NotFoundError(AppException):
    """Resource not found errors (404)."""

    def __init__(
        self,
        detail: str = "Resource not found",
        code: ErrorCode = ErrorCode.NOT_FOUND,
    ):
        super().__init__(status_code=404, detail=detail, code=code)


class ValidationError(AppException):
    """Validation errors (422)."""

    def __init__(
        self,
        detail: str = "Invalid input",
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
    ):
        super().__init__(status_code=422, detail=detail, code=code)


class DatabaseError(AppException):
    """Database-related errors (500)."""

    def __init__(
        self,
        detail: str = "A database error occurred",
        code: ErrorCode = ErrorCode.DATABASE_ERROR,
    ):
        super().__init__(status_code=500, detail=detail, code=code)


# =============================================================================
# Request ID Middleware
# =============================================================================

REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id(request: Request) -> str:
    """Get or generate a request ID for tracking."""
    # Check if request ID was provided by client
    request_id = request.headers.get(REQUEST_ID_HEADER)

    # Generate if not provided
    if not request_id:
        request_id = f"req_{uuid.uuid4().hex[:12]}"

    return request_id


async def request_id_middleware(request: Request, call_next):
    """Middleware to add request ID to all requests and responses."""
    request_id = get_request_id(request)

    # Store in request state for access in handlers
    request.state.request_id = request_id

    # Add to response headers
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id

    return response


# =============================================================================
# Exception Handlers
# =============================================================================

def create_error_response(
    request: Request,
    status_code: int,
    detail: str,
    code: ErrorCode,
) -> JSONResponse:
    """Create a standardized error response."""
    request_id = getattr(request.state, "request_id", None)

    error = ErrorResponse(
        detail=detail,
        code=code,
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
        headers={REQUEST_ID_HEADER: request_id} if request_id else None,
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom AppException instances."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the error
    logger.warning(
        f"AppException: {exc.code} - {exc.detail} "
        f"[request_id={request_id}, path={request.url.path}]"
    )

    return create_error_response(
        request,
        exc.status_code,
        exc.detail,
        exc.code,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTPException instances."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Map status codes to error codes
    code_map = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        422: ErrorCode.INVALID_INPUT,
        500: ErrorCode.SERVER_ERROR,
    }
    code = code_map.get(exc.status_code, ErrorCode.UNKNOWN)

    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail} "
        f"[request_id={request_id}, path={request.url.path}]"
    )

    return create_error_response(
        request,
        exc.status_code,
        str(exc.detail),
        code,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the full error in development
    logger.exception(
        f"Unhandled exception [request_id={request_id}, path={request.url.path}]: {exc}"
    )

    # Return generic error to client (don't leak internal details)
    return create_error_response(
        request,
        500,
        "An internal server error occurred",
        ErrorCode.SERVER_ERROR,
    )


# =============================================================================
# Setup Function
# =============================================================================

def setup_error_handling(app):
    """Configure error handling for the FastAPI app.

    Call this in main.py after creating the app:
        setup_error_handling(app)
    """
    from starlette.middleware.base import BaseHTTPMiddleware

    # Add request ID middleware
    app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_middleware)

    # Register exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
