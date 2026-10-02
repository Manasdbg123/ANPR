"""VisionTrack ANPR — Vehicle Detection Module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np

from app.core.logging import get_logger

logger = get_logger("vision.detection")


@dataclass
class BoundingBox:
    """Bounding box with coordinates and metadata."""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float = 0.0
    class_id: int = 0
    class_name: str = ""

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def to_dict(self) -> dict:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}

    def to_xyxy(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    def to_int(self) -> tuple[int, int, int, int]:
        return (int(self.x1), int(self.y1), int(self.x2), int(self.y2))


@dataclass
class DetectionResult:
    """Result from vehicle detection."""
    boxes: list[BoundingBox] = field(default_factory=list)
    frame_shape: tuple[int, int, int] | None = None
    inference_time_ms: float = 0.0

    @property
    def count(self) -> int:
        return len(self.boxes)


VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

VEHICLE_CLASS_NAMES = set(VEHICLE_CLASSES.values())


@runtime_checkable
class VehicleDetectorProtocol(Protocol):
    """Protocol for vehicle detection implementations."""

    def detect(self, frame: np.ndarray) -> DetectionResult: ...
    def is_loaded(self) -> bool: ...


class YOLOVehicleDetector:
    """YOLO-based vehicle detector using Ultralytics."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        input_size: int = 640,
        device: str = "auto",
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.input_size = input_size
        self.device = device
        self._model = None
        self._loaded = False

    def _load_model(self):
        """Lazy load the YOLO model."""
        if self._loaded:
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
            logger.info("yolo_model_loaded", model=self.model_path, device=device)
        except Exception as e:
            logger.error("yolo_model_load_failed", error=str(e))
            raise

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """Detect vehicles in a frame."""
        import time
        self._load_model()

        start = time.perf_counter()
        results = self._model(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            imgsz=self.input_size,
            verbose=False,
        )
        inference_ms = (time.perf_counter() - start) * 1000

        boxes = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in VEHICLE_CLASSES:
                        xyxy = box.xyxy[0].cpu().numpy()
                        boxes.append(BoundingBox(
                            x1=float(xyxy[0]),
                            y1=float(xyxy[1]),
                            x2=float(xyxy[2]),
                            y2=float(xyxy[3]),
                            confidence=float(box.conf[0]),
                            class_id=cls_id,
                            class_name=VEHICLE_CLASSES[cls_id],
                        ))

        logger.debug("vehicle_detection", boxes=len(boxes), time_ms=round(inference_ms, 1))
        return DetectionResult(
            boxes=boxes,
            frame_shape=frame.shape,
            inference_time_ms=inference_ms,
        )

    def is_loaded(self) -> bool:
        return self._loaded
