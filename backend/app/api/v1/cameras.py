"""VisionTrack ANPR — Camera API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models import User, UserRole
from app.schemas import APIResponse, CameraCreate, CameraResponse, CameraUpdate
from app.services.camera_service import CameraService

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/", response_model=APIResponse[list[CameraResponse]],
            summary="List all cameras")
async def list_cameras(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all configured cameras."""
    service = CameraService(db)
    cameras = await service.get_all()
    return APIResponse(data=cameras)


@router.post("/", response_model=APIResponse[CameraResponse], status_code=201,
             summary="Add a camera")
async def create_camera(
    data: CameraCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
):
    """Add a new camera to the system."""
    service = CameraService(db)
    camera = await service.create(data, user_id=user.id)
    return APIResponse(data=camera)


@router.get("/{camera_id}", response_model=APIResponse[CameraResponse],
            summary="Get camera details")
async def get_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = CameraService(db)
    camera = await service.get_by_id(camera_id)
    return APIResponse(data=camera)


@router.patch("/{camera_id}", response_model=APIResponse[CameraResponse],
              summary="Update camera")
async def update_camera(
    camera_id: str,
    data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
):
    service = CameraService(db)
    camera = await service.update(camera_id, data)
    return APIResponse(data=camera)


@router.delete("/{camera_id}", status_code=204,
               summary="Delete camera")
async def delete_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    service = CameraService(db)
    await service.delete(camera_id)
