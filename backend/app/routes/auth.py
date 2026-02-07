"""Authentication routes backed by PostgreSQL database.

Replaces in-memory storage with database persistence to fix
issues with data loss on server restart.

Per contracts/backend-api.yaml specification.

[Fix]: Create default notification preferences on signup
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
    UserUpdate,
)
# Import notification models for default preference creation
from app.models.notification import (
    NotificationPreference,
    NotificationType,
    EmailFrequency,
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
    """[T014] Register a new user account in the database.

    Updated to handle first_name and last_name fields.

    Args:
        user_data: User registration data (email, password, first_name, last_name)
        session: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If email is already registered (409 Conflict)

    [From]: openapi.yaml §/api/auth/signup
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

    # [T014] Create new User instance with first_name and last_name
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        # [T014] Legacy name field populated for backward compatibility
        name=f"{user_data.first_name} {user_data.last_name or ''}".strip(),
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # [Fix]: Create default notification preferences for new users
    # This ensures email notifications work by default for task-related events
    default_preferences = [
        # Task events - email enabled by default
        (NotificationType.TASK_DUE, True, False, True, EmailFrequency.IMMEDIATE),
        (NotificationType.TASK_OVERDUE, True, True, True, EmailFrequency.IMMEDIATE),
        (NotificationType.TASK_COMPLETED, True, False, True, EmailFrequency.IMMEDIATE),
        (NotificationType.TASK_ASSIGNED, True, False, True, EmailFrequency.IMMEDIATE),
        (NotificationType.TASK_REMINDER, True, False, True, EmailFrequency.IMMEDIATE),
        # System updates - in-app only by default
        (NotificationType.SYSTEM_UPDATE, True, False, False, EmailFrequency.NONE),
    ]

    for notif_type, in_app, push, email, frequency in default_preferences:
        pref = NotificationPreference(
            user_id=new_user.id,
            notification_type=notif_type,
            in_app_enabled=in_app,
            push_enabled=push,
            email_enabled=email,
            frequency=frequency,
        )
        session.add(pref)

    await session.commit()

    # [Fix]: Send welcome email to newly registered user
    try:
        from app.services.email_service import EmailService

        display_name = new_user.display_name if hasattr(new_user, 'display_name') else None
        await EmailService.send_welcome_email(
            session=session,
            user_id=new_user.id,
            to=new_user.email,
            user_name=display_name,
        )
    except Exception as e:
        # Log but don't fail registration if welcome email fails
        logger.warning(f"Failed to send welcome email to {new_user.email}: {e}")

    logger.info(f"New user registered: {user_data.email}")

    # [T015] Return UserPublic with new name fields and display_name
    # [Fix]: Include timezone field
    return UserPublic(
        id=new_user.id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        display_name=new_user.display_name,  # Computed property
        timezone=new_user.timezone,  # Added for notification scheduling
        created_at=new_user.created_at,
    )


@router.post("/signin", response_model=LoginResponse)
async def signin(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    """[T016] Authenticate user against database and return JWT token.

    Updated to include first_name and last_name in JWT token.

    Args:
        credentials: User login credentials (email, password)
        session: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)

    [From]: openapi.yaml §/api/auth/signin
    """
    # Get user from database by email
    user = await get_user_by_email(session, credentials.email)

    # Verify user exists and password matches
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # [T016] Create JWT token with user claims including new name fields
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "name": user.name,  # Legacy field for compatibility
        }
    )

    logger.info(f"User signed in: {credentials.email}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,  # Computed property
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
    """[T015] Get current authenticated user from database.

    Updated to return new name fields and display_name.

    Args:
        user_id: Authenticated user ID from JWT (UUID string)
        session: Database session

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found (404 Not Found)

    [From]: openapi.yaml §/api/auth/me
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
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,  # Computed property
        timezone=user.timezone,  # Include timezone for digest scheduling
        created_at=user.created_at,
    )


@router.put("/me", response_model=UserPublic)
async def update_current_user(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    """Update current user profile.

    Allows users to update their first_name and last_name.
    All fields are optional - update only what's provided.

    Args:
        user_data: Updated user data (first_name, last_name)
        user_id: Authenticated user ID from JWT
        session: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found (404 Not Found)

    [From]: openapi.yaml §/api/auth/me
    """
    user = await get_user_by_uuid(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields if provided
    if user_data.first_name is not None:
        user.first_name = user_data.first_name

    if user_data.last_name is not None:
        user.last_name = user_data.last_name

    # [Fix]: Support timezone updates for digest email scheduling
    if user_data.timezone is not None:
        user.timezone = user_data.timezone

    # Update legacy name field for backward compatibility
    if user.first_name or user.last_name:
        user.name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    await session.commit()
    await session.refresh(user)

    logger.info(f"User profile updated: {user.email}, timezone: {user.timezone}")

    return UserPublic(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        timezone=user.timezone,  # Include timezone in response
        created_at=user.created_at,
    )
