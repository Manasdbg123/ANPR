"""VisionTrack ANPR — Detection Service."""

from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy import and_, desc, asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models import Camera, DetectionEvent
from app.schemas import DetectionFilter, DetectionResponse, PaginatedResponse

logger = get_logger("detection_service")


class DetectionService:
    """Handles detection event CRUD and search."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(self, filters: DetectionFilter) -> PaginatedResponse[DetectionResponse]:
        """Search detection events with filters."""
        query = select(DetectionEvent)
        count_query = select(func.count(DetectionEvent.id))

        conditions = []

        if filters.plate_number:
            conditions.append(
                DetectionEvent.plate_number.ilike(f"%{filters.plate_number}%")
            )
        if filters.camera_id:
            conditions.append(DetectionEvent.camera_id == filters.camera_id)
        if filters.vehicle_type:
            conditions.append(DetectionEvent.vehicle_type == filters.vehicle_type)
        if filters.vehicle_color:
            conditions.append(
                DetectionEvent.vehicle_color.ilike(f"%{filters.vehicle_color}%")
            )
        if filters.min_confidence is not None:
            conditions.append(DetectionEvent.plate_confidence >= filters.min_confidence)
        if filters.max_confidence is not None:
            conditions.append(DetectionEvent.plate_confidence <= filters.max_confidence)
        if filters.start_date:
            conditions.append(DetectionEvent.timestamp >= filters.start_date)
        if filters.end_date:
            conditions.append(DetectionEvent.timestamp <= filters.end_date)
        if filters.plate_valid is not None:
            conditions.append(DetectionEvent.plate_valid == filters.plate_valid)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Sort
        sort_col = getattr(DetectionEvent, filters.sort_by, DetectionEvent.timestamp)
        order = desc(sort_col) if filters.sort_order == "desc" else asc(sort_col)
        query = query.order_by(order)

        # Paginate
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        result = await self.db.execute(query)
        detections = result.scalars().all()

        # Fetch camera names
        camera_ids = {d.camera_id for d in detections}
        camera_names = {}
        if camera_ids:
            cam_result = await self.db.execute(
                select(Camera.id, Camera.name).where(Camera.id.in_(camera_ids))
            )
            camera_names = {row.id: row.name for row in cam_result}

        items = []
        for d in detections:
            resp = DetectionResponse.model_validate(d)
            resp.camera_name = camera_names.get(d.camera_id)
            items.append(resp)

        return PaginatedResponse(
            data=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=math.ceil(total / filters.page_size) if total > 0 else 0,
        )

    async def get_by_id(self, detection_id: str) -> DetectionResponse:
        """Get a single detection by ID."""
        result = await self.db.execute(
            select(DetectionEvent).where(DetectionEvent.id == detection_id)
        )
        detection = result.scalar_one_or_none()
        if not detection:
            raise NotFoundError("Detection", detection_id)

        # Get camera name
        cam_result = await self.db.execute(
            select(Camera.name).where(Camera.id == detection.camera_id)
        )
        cam_name = cam_result.scalar_one_or_none()

        resp = DetectionResponse.model_validate(detection)
        resp.camera_name = cam_name
        return resp

    async def get_recent(self, limit: int = 10) -> list[DetectionResponse]:
        """Get most recent detections."""
        result = await self.db.execute(
            select(DetectionEvent)
            .order_by(desc(DetectionEvent.timestamp))
            .limit(limit)
        )
        detections = result.scalars().all()
        return [DetectionResponse.model_validate(d) for d in detections]

    async def delete(self, detection_id: str) -> None:
        """Delete a detection event."""
        result = await self.db.execute(
            select(DetectionEvent).where(DetectionEvent.id == detection_id)
        )
        detection = result.scalar_one_or_none()
        if not detection:
            raise NotFoundError("Detection", detection_id)
        await self.db.delete(detection)
