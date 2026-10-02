"""VisionTrack ANPR — Authentication API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models import User
from app.schemas import (
    APIResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[UserResponse], status_code=201,
             summary="Register a new user")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account. The first user automatically becomes admin."""
    service = AuthService(db)
    user = await service.register(data)
    return APIResponse(data=user)


@router.post("/login", response_model=APIResponse[TokenResponse],
             summary="Login and get tokens")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with username and password. Returns JWT tokens."""
    service = AuthService(db)
    tokens = await service.login(data)
    return APIResponse(data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse],
             summary="Refresh access token")
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Use a refresh token to get new access and refresh tokens."""
    service = AuthService(db)
    tokens = await service.refresh(data.refresh_token)
    return APIResponse(data=tokens)


@router.get("/me", response_model=APIResponse[UserResponse],
            summary="Get current user")
async def get_me(user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return APIResponse(data=UserResponse.model_validate(user))
