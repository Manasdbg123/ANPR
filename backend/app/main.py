"""VisionTrack ANPR — Main Application Entry Point."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import setup_middleware, setup_exception_handlers
from app.database.redis import close_redis
from app.database.session import init_db
from app.websocket import ws_manager

setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info(
        "application_starting",
        app=settings.app_name,
        version=settings.app_version,
        env=settings.app_env.value,
        demo_mode=settings.demo_mode,
    )

    # Initialize database tables (development only)
    if settings.app_env == "development" or settings.demo_mode:
        await init_db()
        logger.info("database_initialized")

    # Seed demo data if in demo mode
    if settings.demo_mode:
        await seed_demo_data()

    yield

    # Cleanup
    await close_redis()
    logger.info("application_stopped")


app = FastAPI(
    title=settings.app_name,
    description="Real-Time Vehicle Intelligence, Powered by Computer Vision",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup
setup_middleware(app)
setup_exception_handlers(app)

# API routes
app.include_router(api_router)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection events."""
    await ws_manager.connect(websocket, channel="detections")
    try:
        while True:
            data = await websocket.receive_text()
            # Client can send channel subscription messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="detections")


@app.websocket("/ws/{channel}")
async def websocket_channel(websocket: WebSocket, channel: str):
    """WebSocket endpoint for specific channels."""
    await ws_manager.connect(websocket, channel=channel)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel=channel)


async def seed_demo_data():
    """Seed demonstration data for development/demo mode."""
    import uuid
    from datetime import datetime, timedelta, timezone
    import random

    from sqlalchemy import select

    from app.database.session import async_session_factory
    from app.models import (
        Camera, CameraStatus, DetectionEvent, VehicleType,
        AlertRule, AlertSeverity, User, UserRole,
    )
    from app.core.security import hash_password

    async with async_session_factory() as db:
        # Check if data already exists
        result = await db.execute(select(User))
        if result.scalars().first():
            logger.info("demo_data_exists_skipping")
            return

        logger.info("seeding_demo_data")

        # Create demo user
        admin = User(
            email="admin@visiontrack.ai",
            username="admin",
            hashed_password=hash_password("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
        )
        operator = User(
            email="operator@visiontrack.ai",
            username="operator",
            hashed_password=hash_password("operator123"),
            full_name="Camera Operator",
            role=UserRole.OPERATOR,
        )
        db.add_all([admin, operator])
        await db.flush()

        # Create demo cameras
        cameras = []
        camera_configs = [
            ("CAM-01", "Main Gate", CameraStatus.ONLINE),
            ("CAM-02", "Parking Entrance", CameraStatus.ONLINE),
            ("CAM-03", "Exit Gate", CameraStatus.ONLINE),
            ("CAM-04", "Highway Toll", CameraStatus.OFFLINE),
            ("CAM-05", "Side Entrance", CameraStatus.ONLINE),
            ("CAM-06", "Loading Dock", CameraStatus.DISABLED),
        ]
        for name, location, status in camera_configs:
            cam = Camera(
                name=name,
                location=location,
                rtsp_url=f"rtsp://demo.visiontrack.ai/{name.lower().replace('-', '')}",
                status=status,
                last_heartbeat=datetime.now(timezone.utc) if status == CameraStatus.ONLINE else None,
                created_by=admin.id,
            )
            cameras.append(cam)
            db.add(cam)
        await db.flush()

        # Indian state codes for realistic plates
        state_codes = ["DL", "MH", "KA", "TN", "UP", "RJ", "GJ", "HR", "AP", "TS", "KL", "WB"]
        colors = ["White", "Black", "Silver", "Red", "Blue", "Grey", "Green", "Yellow"]
        makes = [
            ("Maruti Suzuki", ["Swift", "Baleno", "Dzire", "Alto", "WagonR", "Vitara Brezza"]),
            ("Hyundai", ["Creta", "i20", "Venue", "Verna", "Tucson"]),
            ("Tata", ["Nexon", "Punch", "Harrier", "Safari", "Altroz"]),
            ("Mahindra", ["XUV700", "Thar", "Scorpio", "XUV300", "Bolero"]),
            ("Toyota", ["Innova", "Fortuner", "Glanza", "Urban Cruiser"]),
            ("Kia", ["Seltos", "Sonet", "Carnival", "EV6"]),
            ("Honda", ["City", "Amaze", "Elevate", "WR-V"]),
        ]
        vehicle_types = [VehicleType.CAR, VehicleType.CAR, VehicleType.CAR, VehicleType.SUV,
                        VehicleType.MOTORCYCLE, VehicleType.BUS, VehicleType.TRUCK,
                        VehicleType.AUTO_RICKSHAW]

        now = datetime.now(timezone.utc)
        online_cameras = [c for c in cameras if c.status == CameraStatus.ONLINE]

        # Generate ~200 demo detections over the last 7 days
        detections = []
        for i in range(200):
            hours_ago = random.uniform(0, 168)  # 7 days
            ts = now - timedelta(hours=hours_ago)
            cam = random.choice(online_cameras)
            state = random.choice(state_codes)
            district = f"{random.randint(1, 99):02d}"
            series = "".join(random.choices("ABCDEFGHJKLMNPRSTUVWXYZ", k=2))
            number = f"{random.randint(1000, 9999)}"
            plate = f"{state}{district}{series}{number}"

            vtype = random.choice(vehicle_types)
            color = random.choice(colors)
            make_info = random.choice(makes)
            make_name = make_info[0]
            model_name = random.choice(make_info[1])

            confidence = round(random.uniform(0.55, 0.99), 2)
            vehicle_conf = round(random.uniform(0.7, 0.99), 2)
            processing_time = random.randint(50, 300)

            detection = DetectionEvent(
                camera_id=cam.id,
                tracking_id=f"T{random.randint(1000, 9999)}",
                timestamp=ts,
                vehicle_type=vtype,
                vehicle_color=color,
                vehicle_make=make_name,
                vehicle_model=model_name,
                vehicle_confidence=vehicle_conf,
                vehicle_bbox={"x1": 100, "y1": 200, "x2": 400, "y2": 500},
                plate_number=plate,
                plate_number_raw=plate,
                plate_confidence=confidence,
                plate_bbox={"x1": 150, "y1": 350, "x2": 300, "y2": 400},
                plate_valid=confidence > 0.7,
                processing_time_ms=processing_time,
                ocr_engine="easyocr",
                first_seen=ts,
                last_seen=ts + timedelta(seconds=random.randint(1, 30)),
                frame_count=random.randint(1, 15),
            )
            detections.append(detection)
            db.add(detection)

        await db.flush()

        # Create demo alert rules
        rules = [
            AlertRule(
                name="VIP Vehicle Alert",
                description="Alert when a VIP plate is detected",
                rule_type="plate_match",
                conditions={"plate_number": "DL01"},
                severity=AlertSeverity.CRITICAL,
                created_by=admin.id,
            ),
            AlertRule(
                name="Low Confidence Detection",
                description="Alert on low OCR confidence",
                rule_type="low_confidence",
                conditions={"threshold": 0.6},
                severity=AlertSeverity.WARNING,
                created_by=admin.id,
            ),
            AlertRule(
                name="Truck Detection",
                description="Alert when a truck is detected",
                rule_type="vehicle_type",
                conditions={"vehicle_type": "truck"},
                severity=AlertSeverity.INFO,
                created_by=admin.id,
            ),
        ]
        db.add_all(rules)

        await db.commit()
        logger.info("demo_data_seeded", detections=len(detections), cameras=len(cameras))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
