"""VisionTrack ANPR — Camera Service."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import get_logger
from app.models import Camera, CameraStatus
from app.schemas import CameraCreate, CameraUpdate, CameraResponse

logger = get_logger("camera_service")


class CameraService:
    """Handles camera CRUD and management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CameraCreate, user_id: str | None = None) -> CameraResponse:
        """Create a new camera."""
        camera = Camera(
            name=data.name,
            location=data.location,
            rtsp_url=data.rtsp_url,
            stream_type=data.stream_type,
            fps=data.fps,
            resolution_width=data.resolution_width,
            resolution_height=data.resolution_height,
            enabled=data.enabled,
            created_by=user_id,
        )
        self.db.add(camera)
        await self.db.flush()
        await self.db.refresh(camera)
        logger.info("camera_created", camera_id=camera.id, name=camera.name)
        return CameraResponse.model_validate(camera)

    async def get_all(self) -> list[CameraResponse]:
        """Get all cameras."""
        result = await self.db.execute(select(Camera).order_by(Camera.name))
        cameras = result.scalars().all()
        return [CameraResponse.model_validate(c) for c in cameras]

    async def get_by_id(self, camera_id: str) -> CameraResponse:
        """Get camera by ID."""
        result = await self.db.execute(select(Camera).where(Camera.id == camera_id))
        camera = result.scalar_one_or_none()
        if not camera:
            raise NotFoundError("Camera", camera_id)
        return CameraResponse.model_validate(camera)

    async def update(self, camera_id: str, data: CameraUpdate) -> CameraResponse:
        """Update camera."""
        result = await self.db.execute(select(Camera).where(Camera.id == camera_id))
        camera = result.scalar_one_or_none()
        if not camera:
            raise NotFoundError("Camera", camera_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)

        await self.db.flush()
        await self.db.refresh(camera)
        return CameraResponse.model_validate(camera)

    async def delete(self, camera_id: str) -> None:
        """Delete camera."""
        result = await self.db.execute(select(Camera).where(Camera.id == camera_id))
        camera = result.scalar_one_or_none()
        if not camera:
            raise NotFoundError("Camera", camera_id)
        await self.db.delete(camera)

    async def get_online_count(self) -> int:
        """Get count of online cameras."""
        result = await self.db.execute(
            select(func.count(Camera.id)).where(Camera.status == CameraStatus.ONLINE)
        )
        return result.scalar() or 0

    async def get_total_count(self) -> int:
        """Get total camera count."""
        result = await self.db.execute(select(func.count(Camera.id)))
        return result.scalar() or 0
