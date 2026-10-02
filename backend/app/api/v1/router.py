"""VisionTrack ANPR — API v1 Router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.cameras import router as cameras_router
from app.api.v1.detections import router as detections_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.system import router as system_router
from app.api.v1.ai import router as ai_router
from app.api.v1.uploads import router as uploads_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(cameras_router)
api_router.include_router(detections_router)
api_router.include_router(analytics_router)
api_router.include_router(alerts_router)
api_router.include_router(system_router)
api_router.include_router(ai_router)
api_router.include_router(uploads_router)
