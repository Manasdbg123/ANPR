"""VisionTrack ANPR — Analytics API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models import User
from app.schemas import (
    APIResponse,
    AnalyticsOverview,
    CameraStats,
    HourlyTraffic,
    VehicleTypeDistribution,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=APIResponse[AnalyticsOverview],
            summary="Dashboard overview statistics")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get aggregated dashboard statistics."""
    service = AnalyticsService(db)
    overview = await service.get_overview()
    return APIResponse(data=overview)


@router.get("/vehicle-types", response_model=APIResponse[list[VehicleTypeDistribution]],
            summary="Vehicle type distribution")
async def get_vehicle_types(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    data = await service.get_vehicle_type_distribution(start, end)
    return APIResponse(data=data)


@router.get("/hourly-traffic", response_model=APIResponse[list[HourlyTraffic]],
            summary="Hourly traffic distribution")
async def get_hourly_traffic(
    date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    data = await service.get_hourly_traffic(date)
    return APIResponse(data=data)


@router.get("/camera-stats", response_model=APIResponse[list[CameraStats]],
            summary="Per-camera detection statistics")
async def get_camera_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    data = await service.get_camera_stats()
    return APIResponse(data=data)


@router.get("/top-plates", summary="Most frequently detected plates")
async def get_top_plates(
    limit: int = Query(10, ge=1, le=50),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    data = await service.get_top_plates(limit, start, end)
    return APIResponse(data=data)
