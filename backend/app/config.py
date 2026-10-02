"""VisionTrack ANPR — Application Configuration."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeviceType(str, Enum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"


class OCREngineType(str, Enum):
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "VisionTrack ANPR"
    app_version: str = "1.0.0"
    app_env: Environment = Environment.DEVELOPMENT
    demo_mode: bool = True
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://visiontrack:visiontrack@localhost:5432/visiontrack"
    database_url_sync: str = "postgresql://visiontrack:visiontrack@localhost:5432/visiontrack"
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-this-to-a-secure-random-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = '["http://localhost:3000","http://127.0.0.1:3000"]'

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> str:
        if isinstance(v, list):
            return json.dumps(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    # Vision
    yolo_model: str = "yolov8n.pt"
    yolo_plate_model: str = "yolov8n.pt"
    ocr_engine: OCREngineType = OCREngineType.EASYOCR
    device: DeviceType = DeviceType.AUTO

    # Processing
    frame_skip: int = 2
    confidence_threshold: float = 0.5
    plate_confidence_threshold: float = 0.3
    duplicate_suppression_seconds: int = 300
    max_inference_resolution: int = 640

    # AI
    llm_api_key: str = ""
    llm_model: str = "gemini-pro"

    # Logging
    log_level: str = "INFO"

    # Upload
    max_upload_size_mb: int = 500
    upload_dir: str = "uploads"
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]
    allowed_video_types: list[str] = ["video/mp4", "video/avi", "video/quicktime"]

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def upload_path(self) -> Path:
        p = self.base_dir / self.upload_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def models_dir(self) -> Path:
        p = self.base_dir.parent / "models"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
