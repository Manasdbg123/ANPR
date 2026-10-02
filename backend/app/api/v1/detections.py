"""VisionTrack ANPR — Detection API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models import User, UserRole
from app.schemas import APIResponse, DetectionFilter, DetectionResponse, PaginatedResponse
from app.services.detection_service import DetectionService

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.get("/", response_model=PaginatedResponse[DetectionResponse],
            summary="Search detections")
async def search_detections(
    plate_number: Optional[str] = Query(None),
    camera_id: Optional[str] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    vehicle_color: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None),
    max_confidence: Optional[float] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    plate_valid: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Search and filter detection events with pagination."""
    filters = DetectionFilter(
        plate_number=plate_number,
        camera_id=camera_id,
        vehicle_type=vehicle_type,
        vehicle_color=vehicle_color,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        start_date=start_date,
        end_date=end_date,
        plate_valid=plate_valid,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = DetectionService(db)
    return await service.search(filters)


@router.get("/recent", response_model=APIResponse[list[DetectionResponse]],
            summary="Get recent detections")
async def recent_detections(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the most recent detection events."""
    service = DetectionService(db)
    detections = await service.get_recent(limit)
    return APIResponse(data=detections)


@router.get("/{detection_id}", response_model=APIResponse[DetectionResponse],
            summary="Get detection detail")
async def get_detection(
    detection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get full details of a specific detection event."""
    service = DetectionService(db)
    detection = await service.get_by_id(detection_id)
    return APIResponse(data=detection)


@router.delete("/{detection_id}", status_code=204,
               summary="Delete detection")
async def delete_detection(
    detection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Delete a detection event. Admin only."""
    service = DetectionService(db)
    await service.delete(detection_id)
