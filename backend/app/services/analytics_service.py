"""VisionTrack ANPR — Analytics Service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, distinct, func, select, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import Camera, CameraStatus, DetectionEvent, VehicleType
from app.schemas import (
    AnalyticsOverview,
    CameraStats,
    HourlyTraffic,
    VehicleTypeDistribution,
)

logger = get_logger("analytics_service")


class AnalyticsService:
    """Provides analytics aggregations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self) -> AnalyticsOverview:
        """Get dashboard overview statistics."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hour_start = now - timedelta(hours=1)

        # Total vehicles
        total_result = await self.db.execute(select(func.count(DetectionEvent.id)))
        total_vehicles = total_result.scalar() or 0

        # Unique plates
        unique_result = await self.db.execute(
            select(func.count(distinct(DetectionEvent.plate_number))).where(
                DetectionEvent.plate_number.isnot(None)
            )
        )
        unique_plates = unique_result.scalar() or 0

        # Plates recognized (non-null plates)
        recognized_result = await self.db.execute(
            select(func.count(DetectionEvent.id)).where(
                DetectionEvent.plate_number.isnot(None)
            )
        )
        plates_recognized = recognized_result.scalar() or 0

        # Active cameras
        active_result = await self.db.execute(
            select(func.count(Camera.id)).where(Camera.status == CameraStatus.ONLINE)
        )
        active_cameras = active_result.scalar() or 0

        # Average confidence
        avg_result = await self.db.execute(
            select(func.avg(DetectionEvent.plate_confidence)).where(
                DetectionEvent.plate_confidence.isnot(None)
            )
        )
        avg_confidence = round(avg_result.scalar() or 0, 2)

        # Vehicles today
        today_result = await self.db.execute(
            select(func.count(DetectionEvent.id)).where(
                DetectionEvent.timestamp >= today_start
            )
        )
        vehicles_today = today_result.scalar() or 0

        # Vehicles this hour
        hour_result = await self.db.execute(
            select(func.count(DetectionEvent.id)).where(
                DetectionEvent.timestamp >= hour_start
            )
        )
        vehicles_this_hour = hour_result.scalar() or 0

        return AnalyticsOverview(
            total_vehicles=total_vehicles,
            unique_plates=unique_plates,
            plates_recognized=plates_recognized,
            active_cameras=active_cameras,
            avg_confidence=avg_confidence,
            vehicles_today=vehicles_today,
            vehicles_this_hour=vehicles_this_hour,
        )

    async def get_vehicle_type_distribution(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> list[VehicleTypeDistribution]:
        """Get vehicle type distribution."""
        query = select(
            DetectionEvent.vehicle_type,
            func.count(DetectionEvent.id).label("count"),
        ).group_by(DetectionEvent.vehicle_type)

        if start:
            query = query.where(DetectionEvent.timestamp >= start)
        if end:
            query = query.where(DetectionEvent.timestamp <= end)

        result = await self.db.execute(query)
        rows = result.all()
        total = sum(r.count for r in rows) or 1

        return [
            VehicleTypeDistribution(
                vehicle_type=r.vehicle_type.value if r.vehicle_type else "unknown",
                count=r.count,
                percentage=round((r.count / total) * 100, 1),
            )
            for r in rows
        ]

    async def get_hourly_traffic(
        self, date: datetime | None = None
    ) -> list[HourlyTraffic]:
        """Get hourly traffic distribution."""
        if date is None:
            date = datetime.now(timezone.utc)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        query = (
            select(
                extract("hour", DetectionEvent.timestamp).label("hour"),
                func.count(DetectionEvent.id).label("count"),
            )
            .where(
                and_(
                    DetectionEvent.timestamp >= day_start,
                    DetectionEvent.timestamp < day_end,
                )
            )
            .group_by(extract("hour", DetectionEvent.timestamp))
            .order_by(extract("hour", DetectionEvent.timestamp))
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Fill in all 24 hours
        hour_map = {int(r.hour): r.count for r in rows}
        return [
            HourlyTraffic(hour=h, count=hour_map.get(h, 0)) for h in range(24)
        ]

    async def get_camera_stats(self) -> list[CameraStats]:
        """Get detection statistics per camera."""
        query = (
            select(
                Camera.id,
                Camera.name,
                func.count(DetectionEvent.id).label("count"),
                func.max(DetectionEvent.timestamp).label("last_detection"),
            )
            .outerjoin(DetectionEvent, DetectionEvent.camera_id == Camera.id)
            .group_by(Camera.id, Camera.name)
            .order_by(func.count(DetectionEvent.id).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            CameraStats(
                camera_id=r.id,
                camera_name=r.name,
                detection_count=r.count,
                last_detection=r.last_detection,
            )
            for r in rows
        ]

    async def get_top_plates(
        self, limit: int = 10, start: datetime | None = None, end: datetime | None = None
    ) -> list[dict]:
        """Get most frequently detected plates."""
        query = (
            select(
                DetectionEvent.plate_number,
                func.count(DetectionEvent.id).label("count"),
                func.avg(DetectionEvent.plate_confidence).label("avg_confidence"),
            )
            .where(DetectionEvent.plate_number.isnot(None))
            .group_by(DetectionEvent.plate_number)
            .order_by(func.count(DetectionEvent.id).desc())
            .limit(limit)
        )

        if start:
            query = query.where(DetectionEvent.timestamp >= start)
        if end:
            query = query.where(DetectionEvent.timestamp <= end)

        result = await self.db.execute(query)
        rows = result.all()
        return [
            {
                "plate_number": r.plate_number,
                "count": r.count,
                "avg_confidence": round(float(r.avg_confidence or 0), 2),
            }
            for r in rows
        ]
