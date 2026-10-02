"""VisionTrack ANPR — System Health API."""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import get_current_user
from app.database.redis import get_redis
from app.database.session import get_db
from app.models import User
from app.schemas import APIResponse, SystemHealth
from app.services.camera_service import CameraService

router = APIRouter(prefix="/system", tags=["System"])

_start_time = time.time()


@router.get("/health", response_model=APIResponse[SystemHealth],
            summary="System health check")
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    """Public health check endpoint."""
    health = SystemHealth(
        status="healthy",
        api="healthy",
        version=settings.app_version,
        uptime_seconds=round(time.time() - _start_time, 1),
    )

    # Database
    try:
        await db.execute(text("SELECT 1"))
        health.database = "healthy"
    except Exception:
        health.database = "unhealthy"
        health.status = "degraded"

    # Redis
    try:
        redis = await get_redis()
        await redis.ping()
        health.redis = "healthy"
    except Exception:
        health.redis = "unhealthy"

    # GPU
    try:
        import torch
        if torch.cuda.is_available():
            health.gpu = f"available ({torch.cuda.get_device_name(0)})"
        else:
            health.gpu = "cpu_only"
    except ImportError:
        health.gpu = "torch_not_installed"

    return APIResponse(data=health)


@router.get("/health/detailed", response_model=APIResponse[SystemHealth],
            summary="Detailed system health (authenticated)")
async def detailed_health(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Detailed health check — requires authentication."""
    resp = await health_check(db)
    health = resp.data

    # Camera counts
    service = CameraService(db)
    health.cameras_online = await service.get_online_count()
    health.cameras_total = await service.get_total_count()

    return APIResponse(data=health)
