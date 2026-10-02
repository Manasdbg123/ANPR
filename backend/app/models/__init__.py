"""VisionTrack ANPR — Database Models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# Use String for IDs to support both PostgreSQL and SQLite
from sqlalchemy import TypeDecorator

class UUIDStr(TypeDecorator):
    """UUID stored as String(36) for database portability."""
    impl = String(36)
    cache_ok = True
from sqlalchemy.orm import relationship

from app.database.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


# ──────────────────── Enums ────────────────────


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    DISABLED = "disabled"


class VehicleType(str, enum.Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    TRUCK = "truck"
    SUV = "suv"
    VAN = "van"
    AUTO_RICKSHAW = "auto_rickshaw"
    UNKNOWN = "unknown"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ──────────────────── Models ────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    name = Column(String(200), nullable=False)
    location = Column(String(500), nullable=True)
    rtsp_url = Column(String(1000), nullable=True)
    stream_type = Column(String(50), default="rtsp")  # rtsp, webcam, file
    fps = Column(Integer, default=30)
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    enabled = Column(Boolean, default=True)
    status = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    processing_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    created_by = Column(UUIDStr, ForeignKey("users.id"), nullable=True)

    detections = relationship("DetectionEvent", back_populates="camera", lazy="dynamic")


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    camera_id = Column(UUIDStr, ForeignKey("cameras.id"), nullable=False, index=True)
    tracking_id = Column(String(100), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)

    # Vehicle
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.UNKNOWN, index=True)
    vehicle_color = Column(String(50), nullable=True, index=True)
    vehicle_make = Column(String(100), nullable=True)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_confidence = Column(Float, nullable=True)
    vehicle_bbox = Column(JSON, nullable=True)  # {x1, y1, x2, y2}

    # Plate
    plate_number = Column(String(20), nullable=True, index=True)
    plate_number_raw = Column(String(50), nullable=True)
    plate_confidence = Column(Float, nullable=True, index=True)
    plate_bbox = Column(JSON, nullable=True)
    plate_valid = Column(Boolean, default=False)

    # Images
    snapshot_path = Column(String(500), nullable=True)
    vehicle_crop_path = Column(String(500), nullable=True)
    plate_crop_path = Column(String(500), nullable=True)

    # Processing
    processing_time_ms = Column(Integer, nullable=True)
    ocr_engine = Column(String(50), nullable=True)
    preprocessing_method = Column(String(100), nullable=True)

    # Metadata
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    frame_count = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), default=utcnow)

    camera = relationship("Camera", back_populates="detections")
    alerts = relationship("AlertEvent", back_populates="detection", lazy="dynamic")

    __table_args__ = (
        Index("ix_detection_plate_ts", "plate_number", "timestamp"),
        Index("ix_detection_camera_ts", "camera_id", "timestamp"),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)  # plate_match, unknown_plate, vehicle_type, etc.
    conditions = Column(JSON, nullable=False)  # Flexible condition structure
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO)
    enabled = Column(Boolean, default=True)
    camera_ids = Column(JSON, nullable=True)  # null = all cameras
    created_by = Column(UUIDStr, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    events = relationship("AlertEvent", back_populates="rule", lazy="dynamic")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    rule_id = Column(UUIDStr, ForeignKey("alert_rules.id"), nullable=False, index=True)
    detection_id = Column(UUIDStr, ForeignKey("detection_events.id"), nullable=True, index=True)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    acknowledged_by = Column(UUIDStr, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    rule = relationship("AlertRule", back_populates="events")
    detection = relationship("DetectionEvent", back_populates="alerts")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUIDStr, primary_key=True, default=new_uuid)
    job_type = Column(String(50), nullable=False)  # video, image, batch
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    total_frames = Column(Integer, nullable=True)
    processed_frames = Column(Integer, default=0)
    detections_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUIDStr, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
