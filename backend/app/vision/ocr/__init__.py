"""VisionTrack ANPR — OCR Engine Module."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np

from app.core.logging import get_logger

logger = get_logger("vision.ocr")


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str = ""
    confidence: float = 0.0
    raw_text: str = ""
    bounding_boxes: list[dict] = field(default_factory=list)
    engine: str = ""


@runtime_checkable
class OCREngineProtocol(Protocol):
    """Protocol for OCR engine implementations."""

    def recognize(self, image: np.ndarray) -> OCRResult: ...
    def is_loaded(self) -> bool: ...


class EasyOCREngine:
    """EasyOCR-based text recognition engine."""

    def __init__(self, languages: list[str] | None = None, gpu: bool = False):
        self.languages = languages or ["en"]
        self.gpu = gpu
        self._reader = None
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        try:
            import easyocr
            self._reader = easyocr.Reader(self.languages, gpu=self.gpu)
            self._loaded = True
            logger.info("easyocr_loaded", languages=self.languages, gpu=self.gpu)
        except Exception as e:
            logger.error("easyocr_load_failed", error=str(e))
            raise

    def recognize(self, image: np.ndarray) -> OCRResult:
        """Recognize text in an image."""
        import time
        self._load()

        start = time.perf_counter()
        results = self._reader.readtext(image)
        elapsed = (time.perf_counter() - start) * 1000

        if not results:
            return OCRResult(engine="easyocr")

        # Combine all detected text
        texts = []
        confidences = []
        boxes = []

        for bbox, text, conf in results:
            texts.append(text)
            confidences.append(conf)
            boxes.append({
                "text": text,
                "confidence": conf,
                "bbox": [list(map(float, p)) for p in bbox],
            })

        raw_text = " ".join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Normalize the text
        normalized = self._normalize_plate_text(raw_text)

        logger.debug("ocr_result", text=normalized, confidence=round(avg_confidence, 3), time_ms=round(elapsed, 1))
        return OCRResult(
            text=normalized,
            confidence=avg_confidence,
            raw_text=raw_text,
            bounding_boxes=boxes,
            engine="easyocr",
        )

    def is_loaded(self) -> bool:
        return self._loaded

    @staticmethod
    def _normalize_plate_text(text: str) -> str:
        """Normalize OCR output for plate text."""
        # Remove whitespace and special characters
        text = text.upper().strip()
        text = re.sub(r'[^A-Z0-9]', '', text)
        return text


class CharacterCorrector:
    """Context-aware OCR character correction for license plates.

    Uses expected plate format to resolve common OCR confusions:
    O ↔ 0, I ↔ 1, B ↔ 8, S ↔ 5, Z ↔ 2, G ↔ 6
    """

    # OCR confusion pairs
    ALPHA_TO_DIGIT = {"O": "0", "I": "1", "B": "8", "S": "5", "Z": "2", "G": "6", "D": "0"}
    DIGIT_TO_ALPHA = {"0": "O", "1": "I", "8": "B", "5": "S", "2": "Z", "6": "G"}

    def correct(self, text: str, expected_pattern: str | None = None) -> str:
        """Apply context-aware character correction.

        Args:
            text: Raw OCR text (normalized, uppercase)
            expected_pattern: Pattern like "AADDAADDDD" where
                             A = alpha expected, D = digit expected

        Returns:
            Corrected text
        """
        if not text or not expected_pattern:
            return text

        if len(text) != len(expected_pattern):
            return text  # Length mismatch — don't guess

        corrected = list(text)
        for i, (char, expect) in enumerate(zip(text, expected_pattern)):
            if expect == "A" and char.isdigit():
                corrected[i] = self.DIGIT_TO_ALPHA.get(char, char)
            elif expect == "D" and char.isalpha():
                corrected[i] = self.ALPHA_TO_DIGIT.get(char, char)

        result = "".join(corrected)
        if result != text:
            logger.debug("character_correction", original=text, corrected=result)
        return result
