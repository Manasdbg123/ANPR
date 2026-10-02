"""VisionTrack ANPR — Exception Hierarchy."""

from __future__ import annotations

from typing import Any


class VisionTrackError(Exception):
    """Base exception for VisionTrack."""

    def __init__(self, message: str = "An error occurred", code: str = "INTERNAL_ERROR", status_code: int = 500, details: Any = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(VisionTrackError):
    """Authentication failure."""

    def __init__(self, message: str = "Authentication failed", code: str = "AUTH_FAILED"):
        super().__init__(message=message, code=code, status_code=401)


class AuthorizationError(VisionTrackError):
    """Authorization failure."""

    def __init__(self, message: str = "Insufficient permissions", code: str = "FORBIDDEN"):
        super().__init__(message=message, code=code, status_code=403)


class NotFoundError(VisionTrackError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(message=msg, code="NOT_FOUND", status_code=404)


class ConflictError(VisionTrackError):
    """Resource conflict."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, code="CONFLICT", status_code=409)


class ValidationError(VisionTrackError):
    """Validation failure."""

    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


class CameraConnectionError(VisionTrackError):
    """Camera connection failure."""

    def __init__(self, camera_id: str = "", message: str = "Unable to connect to camera"):
        super().__init__(message=message, code="CAMERA_CONNECTION_FAILED", status_code=503)


class ProcessingError(VisionTrackError):
    """Vision processing failure."""

    def __init__(self, message: str = "Processing error"):
        super().__init__(message=message, code="PROCESSING_ERROR", status_code=500)


class RateLimitError(VisionTrackError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, code="RATE_LIMITED", status_code=429)
