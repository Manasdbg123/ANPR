"""VisionTrack ANPR — License Plate Detection Module."""

from __future__ import annotations

import numpy as np

from app.core.logging import get_logger
from app.vision.detection import BoundingBox, DetectionResult

logger = get_logger("vision.plate")


class PlateDetector:
    """Detects license plates within vehicle crops.

    Uses a YOLO model fine-tuned for plate detection, or falls back
    to a contour-based approach.
    """

    def __init__(
        self,
        model_path: str | None = None,
        confidence_threshold: float = 0.3,
        device: str = "auto",
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._model = None
        self._loaded = False
        self._use_contour_fallback = model_path is None

    def _load_model(self):
        """Load plate detection model."""
        if self._loaded:
            return
        if self._use_contour_fallback:
            self._loaded = True
            return

        try:
            from ultralytics import YOLO
            device = self.device
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            self._model = YOLO(self.model_path)
            self._model.to(device)
            self._loaded = True
            logger.info("plate_model_loaded", model=self.model_path)
        except Exception as e:
            logger.warning("plate_model_load_failed_using_contour", error=str(e))
            self._use_contour_fallback = True
            self._loaded = True

    def detect(self, vehicle_crop: np.ndarray) -> list[BoundingBox]:
        """Detect license plates in a vehicle crop image."""
        import time
        self._load_model()

        start = time.perf_counter()

        if self._use_contour_fallback:
            plates = self._detect_contour(vehicle_crop)
        else:
            plates = self._detect_yolo(vehicle_crop)

        elapsed = (time.perf_counter() - start) * 1000
        logger.debug("plate_detection", plates=len(plates), time_ms=round(elapsed, 1))
        return plates

    def _detect_yolo(self, crop: np.ndarray) -> list[BoundingBox]:
        """YOLO-based plate detection."""
        results = self._model(crop, conf=self.confidence_threshold, verbose=False)
        plates = []
        if results and len(results) > 0:
            for box in results[0].boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                plates.append(BoundingBox(
                    x1=float(xyxy[0]),
                    y1=float(xyxy[1]),
                    x2=float(xyxy[2]),
                    y2=float(xyxy[3]),
                    confidence=float(box.conf[0]),
                    class_name="plate",
                ))
        return plates

    def _detect_contour(self, crop: np.ndarray) -> list[BoundingBox]:
        """Contour-based plate detection fallback.

        Uses morphological operations and contour analysis to find
        rectangular plate-like regions.
        """
        import cv2

        h, w = crop.shape[:2]
        if h < 20 or w < 20:
            return []

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop.copy()

        # Bilateral filter for noise reduction while preserving edges
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)

        # Canny edge detection
        edges = cv2.Canny(blurred, 30, 200)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        plates = []
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:10]:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * peri, True)

            if len(approx) >= 4:
                x, y, cw, ch = cv2.boundingRect(approx)
                aspect_ratio = cw / max(ch, 1)

                # Indian plates typically have aspect ratio between 2.0 and 6.0
                if 1.5 < aspect_ratio < 7.0 and cw > 60 and ch > 15:
                    # Area should be significant portion of the crop
                    area_ratio = (cw * ch) / (w * h)
                    if 0.02 < area_ratio < 0.8:
                        confidence = min(0.7, area_ratio * 3)
                        plates.append(BoundingBox(
                            x1=float(x),
                            y1=float(y),
                            x2=float(x + cw),
                            y2=float(y + ch),
                            confidence=confidence,
                            class_name="plate",
                        ))

        # Return top candidate
        if plates:
            plates.sort(key=lambda p: p.confidence, reverse=True)
            return plates[:1]
        return []

    def crop_plate(self, vehicle_crop: np.ndarray, plate_box: BoundingBox) -> np.ndarray:
        """Crop the plate region from vehicle image."""
        x1, y1, x2, y2 = plate_box.to_int()
        h, w = vehicle_crop.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        return vehicle_crop[y1:y2, x1:x2]
