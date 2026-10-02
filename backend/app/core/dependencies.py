"""VisionTrack ANPR — FastAPI Dependencies."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.database.session import get_db
from app.models import User, UserRole

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from JWT token."""
    if credentials is None:
        raise AuthenticationError(message="Missing authentication token")

    payload = decode_token(credentials.credentials, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(message="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError(message="User not found")
    if not user.is_active:
        raise AuthenticationError(message="User account is disabled")

    return user


def require_role(*roles: UserRole):
    """Dependency factory that enforces role-based access control."""
    async def _check_role(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AuthorizationError(
                message=f"This action requires one of: {', '.join(r.value for r in roles)}"
            )
        return user
    return _check_role


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None
