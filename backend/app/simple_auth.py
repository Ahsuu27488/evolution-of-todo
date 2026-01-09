"""Simplified JWT authentication using shared secret.

This module provides JWT verification using a shared BETTER_AUTH_SECRET.
Better Auth can be configured to use symmetric HS256 signing with a shared secret,
which is simpler than JWKS for this hackathon project.

For production with Ed25519 asymmetric signing, use jwt_middleware.py instead.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be set and at least 32 characters long. "
        "This secret must match between frontend and backend."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 days per spec

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


# =============================================================================
# JWT Token Operations
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Payload data to encode (typically {"sub": user_id, "email": email})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token using shared secret.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Debug logging in development
        if os.getenv("DEBUG"):
            parts = token.split(".") if token else []
            logger.debug(f"JWT verify attempt: token_parts={len(parts)}, secret_length={len(SECRET_KEY)}")
            if len(parts) >= 2:
                import base64
                import json
                try:
                    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
                    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
                    logger.debug(f"JWT header={header}, payload sub={payload.get('sub')}")
                except Exception as decode_err:
                    logger.debug(f"JWT decode error: {decode_err}")

        # Decode JWT - skip audience verification since we use shared secret auth
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},  # Skip audience validation
        )
        logger.debug(f"JWT decoded successfully, sub={payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# =============================================================================
# Password Hashing
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


# =============================================================================
# FastAPI Dependencies
# =============================================================================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Dependency to extract and verify user_id from JWT token.

    Use this dependency in protected endpoints:

        @app.get("/api/tasks")
        async def list_tasks(user_id: str = Depends(get_current_user_id)):
            ...

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User ID (subject claim from JWT)

    Raises:
        HTTPException: If token is missing or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.debug(f"Token received, length: {len(token)}")

    payload = verify_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        logger.warning(f"Token payload missing 'sub' claim: {payload.keys()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    logger.debug(f"Authenticated user_id: {user_id}")
    return user_id


async def optional_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """Optional authentication - returns user_id if token provided, None otherwise.

    Use for endpoints that work for both authenticated and anonymous users.

    Args:
        credentials: HTTP Bearer credentials (optional)

    Returns:
        User ID if valid token provided, None otherwise
    """
    if credentials is None:
        return None

    try:
        payload = verify_token(credentials.credentials)
        return payload.get("sub")
    except HTTPException:
        return None


# =============================================================================
# Token Payload Model
# =============================================================================

class JWTTokenPayload:
    """Decoded JWT token payload.

    Better Auth JWT structure with HS256:
    - sub: User's unique ID (string)
    - email: User's email (optional)
    - name: User's name (optional)
    - iat: Issued at timestamp
    - exp: Expiration timestamp
    """

    def __init__(self, payload: dict):
        self.sub: str = payload.get("sub", "")
        self.email: str = payload.get("email", "")
        self.name: str = payload.get("name", "")
        self.exp: Optional[int] = payload.get("exp")
        self.iat: Optional[int] = payload.get("iat")
        self.raw_payload = payload

    def __repr__(self) -> str:
        return f"JWTTokenPayload(sub={self.sub})"

    @property
    def userId(self) -> str:
        return self.sub

    @property
    def user_id(self) -> str:
        return self.sub


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTTokenPayload:
    """Get full token payload, not just user_id.

    Returns:
        JWTTokenPayload object with all claims
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)
    return JWTTokenPayload(payload)
