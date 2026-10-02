"""VisionTrack ANPR — Authentication Service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.models import User, UserRole
from app.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = get_logger("auth_service")


class AuthService:
    """Handles user authentication and registration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> UserResponse:
        """Register a new user."""
        # Check existing email
        result = await self.db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise ConflictError(message="Email already registered")

        # Check existing username
        result = await self.db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise ConflictError(message="Username already taken")

        # Count users — first user becomes admin
        result = await self.db.execute(select(User))
        existing = result.scalars().all()
        role = UserRole.ADMIN if len(existing) == 0 else UserRole.VIEWER

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        logger.info("user_registered", user_id=user.id, role=role.value)
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate and return tokens."""
        result = await self.db.execute(
            select(User).where(User.username == data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError(message="Invalid username or password")

        if not user.is_active:
            raise AuthenticationError(message="Account is disabled")

        access_token = create_access_token({"sub": user.id, "role": user.role.value})
        refresh_token = create_refresh_token({"sub": user.id})

        logger.info("user_login", user_id=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Refresh access token."""
        payload = decode_token(refresh_token_str, expected_type="refresh")
        user_id = payload.get("sub")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise AuthenticationError(message="Invalid refresh token")

        access_token = create_access_token({"sub": user.id, "role": user.role.value})
        new_refresh = create_refresh_token({"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", user_id)
        return UserResponse.model_validate(user)
