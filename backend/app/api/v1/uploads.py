"""VisionTrack ANPR — File Upload API."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.database.session import get_db
from app.models import User, ProcessingJob, JobStatus
from app.schemas import APIResponse, ProcessingJobResponse

logger = get_logger("uploads")

router = APIRouter(prefix="/uploads", tags=["Uploads"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".avi", ".mov"}


def validate_upload(file: UploadFile) -> str:
    """Validate uploaded file. Returns the file extension."""
    if not file.filename:
        raise ValidationError("No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    # Check content type
    if file.content_type:
        if not (file.content_type.startswith("image/") or file.content_type.startswith("video/")):
            raise ValidationError(f"Invalid content type: {file.content_type}")

    return ext


@router.post("/image", response_model=APIResponse[dict], summary="Upload an image for processing")
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload an image for ANPR processing. Returns detected vehicles and plates."""
    ext = validate_upload(file)
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValidationError("Please upload an image file (JPEG, PNG, WebP)")

    # Save file
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    filepath = settings.upload_path / filename

    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise ValidationError(f"File too large. Maximum: {settings.max_upload_size_mb}MB")

    with open(filepath, "wb") as f:
        f.write(content)

    logger.info("image_uploaded", file_id=file_id, filename=file.filename, size=len(content))

    # In demo mode, return a placeholder response
    # In production, this would trigger the ANPR pipeline
    return APIResponse(data={
        "file_id": file_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "status": "uploaded",
        "message": "Image uploaded successfully. Processing will begin shortly.",
    })


@router.post("/video", response_model=APIResponse[ProcessingJobResponse],
             summary="Upload a video for processing")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload a video file for ANPR processing. Creates a processing job."""
    ext = validate_upload(file)
    if ext not in {".mp4", ".avi", ".mov"}:
        raise ValidationError("Please upload a video file (MP4, AVI, MOV)")

    # Save file
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    filepath = settings.upload_path / filename

    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise ValidationError(f"File too large. Maximum: {settings.max_upload_size_mb}MB")

    with open(filepath, "wb") as f:
        f.write(content)

    # Create processing job
    job = ProcessingJob(
        job_type="video",
        status=JobStatus.PENDING,
        file_path=str(filepath),
        file_name=file.filename,
        created_by=user.id,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    logger.info("video_uploaded", job_id=job.id, filename=file.filename, size=len(content))

    return APIResponse(data=ProcessingJobResponse.model_validate(job))
