"""VisionTrack ANPR — Full ANPR Pipeline."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import cv2
import numpy as np

from app.core.logging import get_logger
from app.vision.detection import BoundingBox, YOLOVehicleDetector
from app.vision.plate import PlateDetector
from app.vision.preprocessing import PreprocessingPipeline
from app.vision.ocr import EasyOCREngine, CharacterCorrector, OCRResult
from app.vision.plate.validator import PlateValidator, ValidationResult
from app.vision.tracking import SimpleTracker
from app.vision.classification import VehicleClassifier

logger = get_logger("vision.pipeline")


@dataclass
class PipelineResult:
    """Result from processing a single frame through the ANPR pipeline."""
    frame_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    vehicles: list[VehicleResult] = field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_shape: tuple[int, ...] | None = None


@dataclass
class VehicleResult:
    """Complete detection result for a single vehicle."""
    tracking_id: int | None = None
    vehicle_bbox: BoundingBox | None = None
    vehicle_type: str = "unknown"
    vehicle_color: str = "unknown"
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_confidence: float = 0.0
    plate_bbox: BoundingBox | None = None
    plate_text: str | None = None
    plate_text_raw: str | None = None
    plate_confidence: float = 0.0
    plate_valid: bool = False
    plate_crop: np.ndarray | None = None
    vehicle_crop: np.ndarray | None = None
    ocr_engine: str = ""
    preprocessing_method: str = ""

    def to_dict(self) -> dict:
        return {
            "tracking_id": self.tracking_id,
            "vehicle_type": self.vehicle_type,
            "vehicle_color": self.vehicle_color,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_confidence": self.vehicle_confidence,
            "vehicle_bbox": self.vehicle_bbox.to_dict() if self.vehicle_bbox else None,
            "plate_number": self.plate_text,
            "plate_number_raw": self.plate_text_raw,
            "plate_confidence": self.plate_confidence,
            "plate_bbox": self.plate_bbox.to_dict() if self.plate_bbox else None,
            "plate_valid": self.plate_valid,
            "ocr_engine": self.ocr_engine,
            "preprocessing_method": self.preprocessing_method,
        }


class ANPRPipeline:
    """Full ANPR processing pipeline.

    Frame → Vehicle Detection → Tracking → Plate Detection →
    Preprocessing → OCR → Validation → Vehicle Classification → Result
    """

    def __init__(
        self,
        vehicle_detector: YOLOVehicleDetector | None = None,
        plate_detector: PlateDetector | None = None,
        ocr_engine: EasyOCREngine | None = None,
        preprocessor: PreprocessingPipeline | None = None,
        validator: PlateValidator | None = None,
        corrector: CharacterCorrector | None = None,
        tracker: SimpleTracker | None = None,
        classifier: VehicleClassifier | None = None,
        min_ocr_confidence: float = 0.4,
        enable_multi_preprocess: bool = True,
    ):
        self.vehicle_detector = vehicle_detector or YOLOVehicleDetector()
        self.plate_detector = plate_detector or PlateDetector()
        self.preprocessor = preprocessor or PreprocessingPipeline()
        self.ocr_engine = ocr_engine
        self.validator = validator or PlateValidator()
        self.corrector = corrector or CharacterCorrector()
        self.tracker = tracker or SimpleTracker()
        self.classifier = classifier or VehicleClassifier()
        self.min_ocr_confidence = min_ocr_confidence
        self.enable_multi_preprocess = enable_multi_preprocess

    def process_frame(self, frame: np.ndarray, frame_id: str | None = None) -> PipelineResult:
        """Process a single frame through the complete ANPR pipeline."""
        start = time.perf_counter()
        result = PipelineResult(
            frame_id=frame_id or str(uuid.uuid4())[:8],
            frame_shape=frame.shape,
        )

        # Step 1: Vehicle detection
        detections = self.vehicle_detector.detect(frame)

        # Step 2: Update tracker
        tracks = self.tracker.update(detections.boxes)
        track_map = {}
        for track in tracks:
            # Map detection boxes to tracks by IoU
            for box in detections.boxes:
                if self.tracker._iou(track.bbox, box) > 0.5:
                    track_map[id(box)] = track.track_id
                    break

        # Step 3: Process each detected vehicle
        for box in detections.boxes:
            vehicle_result = self._process_vehicle(frame, box)
            vehicle_result.tracking_id = track_map.get(id(box))
            result.vehicles.append(vehicle_result)

        result.processing_time_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "frame_processed",
            frame_id=result.frame_id,
            vehicles=len(result.vehicles),
            time_ms=result.processing_time_ms,
        )
        return result

    def _process_vehicle(self, frame: np.ndarray, vehicle_box: BoundingBox) -> VehicleResult:
        """Process a single detected vehicle."""
        result = VehicleResult(
            vehicle_bbox=vehicle_box,
            vehicle_type=vehicle_box.class_name,
            vehicle_confidence=vehicle_box.confidence,
        )

        # Crop vehicle
        x1, y1, x2, y2 = vehicle_box.to_int()
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        vehicle_crop = frame[y1:y2, x1:x2]

        if vehicle_crop.size == 0:
            return result

        result.vehicle_crop = vehicle_crop

        # Vehicle classification (color)
        classification = self.classifier.classify(vehicle_crop, vehicle_box.class_name)
        result.vehicle_color = classification.vehicle_color
        result.vehicle_make = classification.vehicle_make
        result.vehicle_model = classification.vehicle_model

        # Plate detection
        plate_boxes = self.plate_detector.detect(vehicle_crop)
        if not plate_boxes:
            return result

        plate_box = plate_boxes[0]  # Best candidate
        result.plate_bbox = BoundingBox(
            x1=plate_box.x1 + x1,
            y1=plate_box.y1 + y1,
            x2=plate_box.x2 + x1,
            y2=plate_box.y2 + y1,
            confidence=plate_box.confidence,
            class_name="plate",
        )

        # Crop plate
        plate_crop = self.plate_detector.crop_plate(vehicle_crop, plate_box)
        if plate_crop.size == 0:
            return result
        result.plate_crop = plate_crop

        # OCR
        if self.ocr_engine is None:
            return result

        ocr_result = self._run_ocr(plate_crop)
        if not ocr_result.text:
            return result

        result.plate_text_raw = ocr_result.raw_text
        result.plate_confidence = ocr_result.confidence
        result.ocr_engine = ocr_result.engine

        # Character correction
        corrected = self.corrector.correct(
            ocr_result.text,
            expected_pattern=self._infer_pattern(ocr_result.text),
        )

        # Validation
        validation = self.validator.validate(corrected, ocr_result.confidence)
        result.plate_text = validation.normalized_text
        result.plate_valid = validation.valid
        result.plate_confidence = validation.confidence

        return result

    def _run_ocr(self, plate_crop: np.ndarray) -> OCRResult:
        """Run OCR with optional multi-preprocessing fallback."""
        # First try standard preprocessing
        preprocessed = self.preprocessor.standard_preprocess(plate_crop)
        ocr_result = self.ocr_engine.recognize(preprocessed)

        if ocr_result.confidence >= self.min_ocr_confidence or not self.enable_multi_preprocess:
            ocr_result.engine = self.ocr_engine.__class__.__name__
            return ocr_result

        # Low confidence — try multiple preprocessing strategies
        best_result = ocr_result
        candidates = self.preprocessor.preprocess_for_ocr(plate_crop)

        for candidate in candidates:
            result = self.ocr_engine.recognize(candidate.image)
            if result.confidence > best_result.confidence:
                best_result = result
                best_result.engine = f"{self.ocr_engine.__class__.__name__}+{candidate.method}"

            if best_result.confidence >= 0.85:
                break  # Good enough

        return best_result

    @staticmethod
    def _infer_pattern(text: str) -> str | None:
        """Infer expected pattern for Indian plates.

        Standard Indian plate: AA DD AA DDDD
        Returns pattern string like 'AADDAADDDD'
        """
        if len(text) >= 9 and len(text) <= 11:
            # Try standard format
            pattern = ""
            for i, char in enumerate(text):
                if i < 2:
                    pattern += "A"
                elif i < 4:
                    pattern += "D"
                elif i < 6:
                    pattern += "A"
                else:
                    pattern += "D"
            return pattern
        return None


class DuplicateSuppressor:
    """Prevents duplicate detection events for the same vehicle.

    Uses Redis or in-memory cache to track recently detected plates
    per camera and suppresses duplicate events within a configurable window.
    """

    def __init__(self, suppression_window_seconds: int = 300):
        self.suppression_window = suppression_window_seconds
        self._recent: dict[str, float] = {}  # key -> last_seen_timestamp

    def is_duplicate(self, camera_id: str, plate_number: str) -> bool:
        """Check if this detection is a duplicate."""
        if not plate_number:
            return False

        key = f"{camera_id}:{plate_number}"
        now = time.time()

        if key in self._recent:
            elapsed = now - self._recent[key]
            if elapsed < self.suppression_window:
                logger.debug("duplicate_suppressed", key=key, elapsed_s=round(elapsed, 1))
                return True

        self._recent[key] = now
        return False

    def cleanup(self):
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, v in self._recent.items() if now - v > self.suppression_window]
        for k in expired:
            del self._recent[k]
