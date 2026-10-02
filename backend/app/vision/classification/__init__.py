"""VisionTrack ANPR — Vehicle Classification Module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from app.core.logging import get_logger

logger = get_logger("vision.classification")


@dataclass
class ClassificationResult:
    """Result of vehicle classification."""
    vehicle_type: str = "unknown"
    vehicle_color: str = "unknown"
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    type_confidence: float = 0.0
    color_confidence: float = 0.0


@runtime_checkable
class VehicleClassifierProtocol(Protocol):
    def classify(self, image: np.ndarray) -> ClassificationResult: ...


class VehicleClassifier:
    """Classifies vehicle type and color from crop images.

    Uses color histogram analysis for color detection.
    Vehicle type is inferred from the YOLO detection class.
    Make/model classification requires a specialized model —
    the interface is provided for future integration.
    """

    # HSV color ranges for common vehicle colors
    COLOR_RANGES = {
        "White": [(0, 0, 180), (180, 30, 255)],
        "Black": [(0, 0, 0), (180, 255, 50)],
        "Silver": [(0, 0, 120), (180, 30, 180)],
        "Red": [(0, 100, 100), (10, 255, 255)],
        "Blue": [(100, 100, 100), (130, 255, 255)],
        "Green": [(35, 100, 100), (85, 255, 255)],
        "Yellow": [(20, 100, 100), (35, 255, 255)],
        "Grey": [(0, 0, 50), (180, 50, 120)],
    }

    def classify(self, image: np.ndarray, yolo_class: str = "unknown") -> ClassificationResult:
        """Classify vehicle type and color."""
        color, color_conf = self._detect_color(image)

        return ClassificationResult(
            vehicle_type=yolo_class,
            vehicle_color=color,
            type_confidence=0.0,  # From YOLO, set by caller
            color_confidence=color_conf,
        )

    def _detect_color(self, image: np.ndarray) -> tuple[str, float]:
        """Detect dominant vehicle color using HSV analysis."""
        import cv2

        if image is None or image.size == 0:
            return "unknown", 0.0

        try:
            # Crop center region (avoid background)
            h, w = image.shape[:2]
            margin_y = int(h * 0.2)
            margin_x = int(w * 0.15)
            center = image[margin_y:h - margin_y, margin_x:w - margin_x]

            if center.size == 0:
                center = image

            hsv = cv2.cvtColor(center, cv2.COLOR_BGR2HSV)
            total_pixels = hsv.shape[0] * hsv.shape[1]

            if total_pixels == 0:
                return "unknown", 0.0

            best_color = "unknown"
            best_ratio = 0.0

            for color_name, (lower, upper) in self.COLOR_RANGES.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                ratio = cv2.countNonZero(mask) / total_pixels

                # Red wraps around in HSV
                if color_name == "Red":
                    mask2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
                    ratio += cv2.countNonZero(mask2) / total_pixels

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_color = color_name

            confidence = min(1.0, best_ratio * 2)  # Scale up since we're looking at center
            return best_color, round(confidence, 2)

        except Exception as e:
            logger.debug("color_detection_failed", error=str(e))
            return "unknown", 0.0
