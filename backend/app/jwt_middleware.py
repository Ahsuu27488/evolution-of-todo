"""JWT verification middleware for Better Auth JWT tokens.

This module verifies JWT tokens issued by Better Auth on the frontend.
Better Auth's JWT plugin uses EdDSA (Ed25519) asymmetric signing by default.

Token Flow:
1. User signs in on frontend via Better Auth
2. Frontend calls /api/auth/token which returns a JWT
3. Frontend sends JWT in Authorization header to FastAPI
4. Backend fetches JWKS from Better Auth to get the public key
5. Backend verifies EdDSA signature using the public key
6. Extracts user info from the token payload (sub claim = userId)
"""

import logging
import os
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .errors import AuthenticationError, ErrorCode

# =============================================================================
# Configuration
# =============================================================================

logger = logging.getLogger(__name__)

# Better Auth frontend URL for JWKS fetching
# Use 127.0.0.1 instead of localhost to avoid IPv6 connection issues with httpx
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://127.0.0.1:3000")
JWKS_URL = urljoin(BETTER_AUTH_URL, "/api/auth/jwks")

# Cache for JWKS (public keys don't change frequently)
_jwks_cache: dict = {}
_jwks_cache_expiry: Optional[float] = None
JWKS_CACHE_DURATION = 3600  # 1 hour

# =============================================================================
# JWKS Management
# =============================================================================


async def fetch_jwks() -> dict:
    """Fetch the JSON Web Key Set from Better Auth.

    Returns the JWKS dict containing public keys for JWT verification.
    """
    global _jwks_cache, _jwks_cache_expiry

    # Return cached JWKS if still valid
    if _jwks_cache and _jwks_cache_expiry:
        if datetime.utcnow().timestamp() < _jwks_cache_expiry:
            logger.debug("Using cached JWKS")
            return _jwks_cache

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(JWKS_URL)
            response.raise_for_status()
            jwks = response.json()

            # Cache the JWKS
            _jwks_cache = jwks
            _jwks_cache_expiry = datetime.utcnow().timestamp() + JWKS_CACHE_DURATION
            logger.info(f"Successfully fetched JWKS from {JWKS_URL} with {len(jwks.get('keys', []))} keys")
            return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS from {JWKS_URL}: {e}")
        # If we have cached data, return it even if expired
        if _jwks_cache:
            logger.warning("Using expired cached JWKS due to fetch failure")
            return _jwks_cache
        raise AuthenticationError(
            detail="Unable to verify JWT token at this time",
            code=ErrorCode.UNAUTHORIZED,
        )


def get_public_key(jwks: dict, kid: str) -> str:
    """Extract the public key from JWKS for a given key ID.

    Args:
        jwks: The JWKS dict
        kid: The key ID to find

    Returns:
        The public key in PEM format
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            # EdDSA uses Ed25519, the key is in 'x' field as base64url
            if key.get("kty") == "OKP" and key.get("crv") == "Ed25519":
                x = key.get("x")
                if not x:
                    raise ValueError("Public key missing 'x' field")

                # Convert base64url to raw bytes
                import base64
                x_bytes = base64.urlsafe_b64decode(x + '=' * (4 - len(x) % 4))

                # Format as Ed25519 public key PEM
                pem_key = (
                    "-----BEGIN PUBLIC KEY-----\n"
                    + base64.b64encode(
                        b'\x30\x2a\x30\x05\x06\x03\x2b\x65\x70\x03\x21\x00' + x_bytes
                    ).decode('ascii')
                    + "\n-----END PUBLIC KEY-----"
                )
                return pem_key

    raise ValueError(f"Key with kid={kid} not found in JWKS")


# =============================================================================
# Token Payload Model
# =============================================================================

class JWTTokenPayload:
    """Decoded JWT token payload from Better Auth.

    Better Auth JWT structure:
    - sub: User's unique ID (string)
    - email: User's email
    - iat: Issued at timestamp
    - exp: Expiration timestamp
    """

    def __init__(self, payload: dict):
        self.sub: str = payload.get("sub", "")
        self.email: str = payload.get("email", "")
        self.name: str = payload.get("name", "")
        self.exp: Optional[int] = payload.get("exp")
        self.iat: Optional[int] = payload.get("iat")
        self.iss: Optional[str] = payload.get("iss")
        self.raw_payload = payload

    def __repr__(self) -> str:
        return f"JWTTokenPayload(sub={self.sub})"

    @property
    def userId(self) -> str:
        return self.sub

    @property
    def user_id(self) -> str:
        return self.sub

    def is_expired(self) -> bool:
        if self.exp is None:
            return False
        return datetime.utcnow().timestamp() > self.exp


# =============================================================================
# Token Verification
# =============================================================================

async def decode_jwt_token(token: str) -> JWTTokenPayload:
    """Decode and verify a JWT token from Better Auth using JWKS.

    Fetches the public key from Better Auth's JWKS endpoint and verifies
    the EdDSA signature.
    """
    # Import jwt at function level for exception handlers
    import jwt

    try:
        # Decode header without verification to get kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if not kid:
            raise AuthenticationError(
                detail="Invalid token: missing kid header",
                code=ErrorCode.INVALID_TOKEN,
            )

        # Fetch JWKS and get the public key
        jwks = await fetch_jwks()
        public_key = get_public_key(jwks, kid)

        # Verify and decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["EdDSA"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Audience check is optional
                "verify_iss": False,  # Issuer check is optional
            },
        )

        token_payload = JWTTokenPayload(payload)

        if not token_payload.sub:
            raise AuthenticationError(
                detail="Invalid token: missing user identifier",
                code=ErrorCode.INVALID_TOKEN,
            )

        logger.debug(f"JWT verified: user={token_payload.sub}")
        return token_payload

    except jwt.ExpiredSignatureError:
        logger.info("JWT token has expired")
        raise AuthenticationError(
            detail="Token has expired. Please sign in again.",
            code=ErrorCode.SESSION_EXPIRED,
        )
    except jwt.InvalidTokenError as e:
        error_msg = str(e)
        logger.warning(f"JWT verification failed: {error_msg}")
        raise AuthenticationError(
            detail=f"Invalid token: {error_msg}",
            code=ErrorCode.INVALID_TOKEN,
        )
    except Exception as e:
        logger.exception(f"Unexpected error during JWT verification")
        raise AuthenticationError(
            detail="Token verification failed",
            code=ErrorCode.INVALID_TOKEN,
        )


# =============================================================================
# FastAPI Dependencies
# =============================================================================

security = HTTPBearer(
    scheme_name="JWT",
    description="JWT token from Better Auth (/api/auth/token endpoint)",
    auto_error=False,
)


async def verify_jwt_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> JWTTokenPayload:
    """Verify Better Auth JWT token and return decoded payload."""
    if credentials is None:
        raise AuthenticationError(
            detail="Authentication required. Please provide a JWT token.",
            code=ErrorCode.MISSING_TOKEN,
        )

    token = credentials.credentials
    if not token:
        raise AuthenticationError(
            detail="Empty token provided",
            code=ErrorCode.MISSING_TOKEN,
        )

    return await decode_jwt_token(token)


async def get_current_user_id(
    payload: JWTTokenPayload = Depends(verify_jwt_token),
) -> str:
    """Extract user ID from verified JWT token."""
    return payload.sub


async def require_user_match(
    request: Request,
    user_id_from_path: str,
    current_user_id: str = Depends(get_current_user_id),
) -> str:
    """Verify that the authenticated user matches the requested resource.

    Returns 403 Forbidden (not 404) when user doesn't own the resource.
    """
    from .errors import AuthorizationError

    if current_user_id != user_id_from_path:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"User mismatch: token_user={current_user_id}, "
            f"requested_user={user_id_from_path} [request_id={request_id}]"
        )
        raise AuthorizationError(
            detail="Not authorized to access this user's resources",
            code=ErrorCode.NOT_OWNER,
        )

    return current_user_id


def extract_token_from_header(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return auth_header
