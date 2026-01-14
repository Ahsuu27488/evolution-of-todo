"""Authentication routes backed by PostgreSQL database.

Replaces in-memory storage with database persistence to fix
issues with data loss on server restart.

Per contracts/backend-api.yaml specification.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import (
    User,
    LoginResponse,
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
# Database Helpers
# =============================================================================

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch user from database by email.

    Args:
        session: Async database session
        email: User email to look up

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_uuid(session: AsyncSession, user_id: str) -> User | None:
    """Fetch user from database by ID.

    Args:
        session: Async database session
        user_id: User UUID string to look up

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


# =============================================================================
# Routes
# =============================================================================

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    """Register a new user account in the database.

    Args:
        user_data: User registration data (email, password, name)
        session: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If email is already registered (409 Conflict)
    """
    # Check if email already exists in database
    existing = await get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash password using bcrypt
    hashed_password = get_password_hash(user_data.password)

    # Create new User instance with UUID as string
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"New user registered: {user_data.email}")

    return UserPublic(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at,
    )


@router.post("/signin", response_model=LoginResponse)
async def signin(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    """Authenticate user against database and return JWT token.

    Args:
        credentials: User login credentials (email, password)
        session: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    """
    # Get user from database by email
    user = await get_user_by_email(session, credentials.email)

    # Verify user exists and password matches
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token with user claims
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "name": user.name,
        }
    )

    logger.info(f"User signed in: {credentials.email}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        ),
    )


@router.post("/signout")
async def signout(user_id: str = Depends(get_current_user_id)) -> dict:
    """Logout user (client-side token invalidation).

    Args:
        user_id: Authenticated user ID from JWT

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
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    """Get current authenticated user from database.

    Args:
        user_id: Authenticated user ID from JWT (UUID string)
        session: Database session

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found (404 Not Found)
    """
    user = await get_user_by_uuid(session, user_id)

    if not user:
        # This handles the case where a token is valid, but the user
        # was deleted from the database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserPublic(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )
