"""Authentication routes for user signup, login, and logout.

These endpoints work with Better Auth on the frontend.
The backend stores user credentials and issues JWT tokens for API access.

Per contracts/backend-api.yaml specification.
"""

import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import (
    Action,
    LoginResponse,
    TaskLog,
    TaskLogPublic,
    UserCreate,
    UserLogin,
    UserPublic,
)
from app.simple_auth import (
    create_access_token,
    get_current_user_id,
    get_password_hash,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# User Table (Simple in-memory for Phase II)
# =============================================================================

# For Phase II, we'll use a simple dict-based user store.
# In production with Better Auth, users table is managed by Better Auth.
# This is a minimal implementation for standalone backend auth.
# Users are stored by UUID, with a separate email index for lookups.

_users_store: dict[str, dict] = {}  # user_id (UUID) -> user data
_email_index: dict[str, str] = {}  # email -> user_id mapping


def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID from in-memory store."""
    return _users_store.get(user_id)


def get_user_by_email(email: str) -> dict | None:
    """Get user by email from in-memory store."""
    user_id = _email_index.get(email)
    if user_id:
        return _users_store.get(user_id)
    return None


def create_user(user_data: dict) -> dict:
    """Create a new user in the in-memory store."""
    email = user_data["email"]
    user_id = user_data["id"]
    if email in _email_index:
        raise ValueError("Email already registered")
    _users_store[user_id] = user_data
    _email_index[email] = user_id
    return user_data


# =============================================================================
# Routes
# =============================================================================


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    """Register a new user account.

    Args:
        user_data: User registration data (email, password, name)
        session: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If email is already registered
    """
    # Check if email already exists
    existing = get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user with proper UUID as user_id
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }

    create_user(user)

    logger.info(f"New user registered: {user_data.email}")

    return UserPublic(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        created_at=user["created_at"],
    )


@router.post("/signin", response_model=LoginResponse)
async def signin(
    credentials: UserLogin,
) -> LoginResponse:
    """Authenticate user and return JWT token.

    Args:
        credentials: User login credentials (email, password)

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user
    user = get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "email": user["email"],
            "name": user["name"],
        }
    )

    logger.info(f"User signed in: {credentials.email}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user.get("created_at"),
        ),
    )


@router.post("/signout")
async def signout(user_id: str = Depends(get_current_user_id)) -> dict:
    """Logout user (client-side token invalidation).

    Args:
        user_id: Authenticated user ID

    Returns:
        Success message

    Note:
        JWT tokens are stateless. Logout is handled client-side by
        deleting the token. For server-side invalidation, implement
        a token blacklist with Redis.
    """
    logger.info(f"User signed out: {user_id}")
    return {"message": "Successfully signed out"}


@router.get("/me", response_model=UserPublic)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
) -> UserPublic:
    """Get current authenticated user information.

    Args:
        user_id: Authenticated user ID from JWT (UUID string)

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found
    """
    user = get_user_by_id(user_id)  # Look up by UUID
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserPublic(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user.get("created_at"),
    )
