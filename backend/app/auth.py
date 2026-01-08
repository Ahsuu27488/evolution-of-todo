"""Authentication module for Better Auth JWT/Bearer tokens.

This module provides JWT-based authentication for the FastAPI backend.
Better Auth's JWT plugin issues EdDSA-signed tokens that this backend verifies.

All authentication logic is delegated to jwt_middleware.py.
This module re-exports the public API for convenience.
"""

from .jwt_middleware import (
    JWTTokenPayload,
    decode_jwt_token,
    extract_token_from_header,
    fetch_jwks,
    get_current_user_id,
    get_public_key,
    require_user_match,
    verify_jwt_token,
)

__all__ = [
    # Main dependency for protected routes
    "verify_jwt_token",

    # Get just the user ID
    "get_current_user_id",

    # Verify user owns the resource
    "require_user_match",

    # Token payload model
    "JWTTokenPayload",

    # Utility functions
    "extract_token_from_header",
    "decode_jwt_token",
    "fetch_jwks",
    "get_public_key",
]
