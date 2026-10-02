"""VisionTrack ANPR — Pydantic Schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field


T = TypeVar("T")


# ──────────────────── Common ────────────────────


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: dict | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict = Field(default_factory=lambda: {"code": "UNKNOWN", "message": "An error occurred"})


# ──────────────────── Auth ────────────────────


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────── Camera ────────────────────


class CameraCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: str | None = None
    rtsp_url: str | None = None
    stream_type: str = "rtsp"
    fps: int = Field(default=30, ge=1, le=120)
    resolution_width: int = Field(default=1920, ge=320)
    resolution_height: int = Field(default=1080, ge=240)
    enabled: bool = True


class CameraUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    rtsp_url: str | None = None
    fps: int | None = None
    enabled: bool | None = None


class CameraResponse(BaseModel):
    id: str
    name: str
    location: str | None
    stream_type: str
    fps: int
    resolution_width: int
    resolution_height: int
    enabled: bool
    status: str
    last_heartbeat: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────── Detection ────────────────────


class DetectionResponse(BaseModel):
    id: str
    camera_id: str
    camera_name: str | None = None
    tracking_id: str | None
    timestamp: datetime
    vehicle_type: str | None
    vehicle_color: str | None
    vehicle_make: str | None
    vehicle_model: str | None
    vehicle_confidence: float | None
    vehicle_bbox: dict | None
    plate_number: str | None
    plate_number_raw: str | None
    plate_confidence: float | None
    plate_bbox: dict | None
    plate_valid: bool
    snapshot_url: str | None = None
    vehicle_crop_url: str | None = None
    plate_crop_url: str | None = None
    processing_time_ms: int | None
    ocr_engine: str | None
    first_seen: datetime | None
    last_seen: datetime | None
    frame_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionFilter(BaseModel):
    plate_number: str | None = None
    camera_id: str | None = None
    vehicle_type: str | None = None
    vehicle_color: str | None = None
    min_confidence: float | None = None
    max_confidence: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    plate_valid: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "timestamp"
    sort_order: str = "desc"


# ──────────────────── Analytics ────────────────────


class AnalyticsOverview(BaseModel):
    total_vehicles: int = 0
    unique_plates: int = 0
    plates_recognized: int = 0
    active_cameras: int = 0
    avg_confidence: float = 0.0
    vehicles_today: int = 0
    vehicles_this_hour: int = 0


class VehicleTypeDistribution(BaseModel):
    vehicle_type: str
    count: int
    percentage: float


class HourlyTraffic(BaseModel):
    hour: int
    count: int


class CameraStats(BaseModel):
    camera_id: str
    camera_name: str
    detection_count: int
    last_detection: datetime | None


# ──────────────────── Alerts ────────────────────


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    rule_type: str
    conditions: dict
    severity: str = "info"
    enabled: bool = True
    camera_ids: list[str] | None = None


class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    rule_type: str
    conditions: dict
    severity: str
    enabled: bool
    camera_ids: list[str] | None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertEventResponse(BaseModel):
    id: str
    rule_id: str
    detection_id: str | None
    severity: str
    status: str
    title: str
    message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────── AI ────────────────────


class AIQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None


class AIQueryResponse(BaseModel):
    response: str
    tool_calls: list[dict] = []
    conversation_id: str | None = None


# ──────────────────── System ────────────────────


class SystemHealth(BaseModel):
    status: str = "healthy"
    api: str = "healthy"
    database: str = "unknown"
    redis: str = "unknown"
    yolo: str = "unknown"
    ocr: str = "unknown"
    gpu: str = "unknown"
    cameras_online: int = 0
    cameras_total: int = 0
    uptime_seconds: float = 0.0
    version: str = ""


class ProcessingJobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    file_name: str | None
    total_frames: int | None
    processed_frames: int
    detections_count: int
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True
