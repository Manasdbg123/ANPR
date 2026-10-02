"""VisionTrack ANPR — Image Preprocessing Pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import cv2
import numpy as np

from app.core.logging import get_logger

logger = get_logger("vision.preprocessing")


@dataclass
class PreprocessedImage:
    """Result of preprocessing with metadata."""
    image: np.ndarray
    method: str
    description: str


class PreprocessingPipeline:
    """Intelligent image preprocessing pipeline for plate OCR.

    Applies multiple preprocessing strategies and returns candidates
    for OCR when confidence is low.
    """

    def preprocess_for_ocr(self, plate_image: np.ndarray) -> list[PreprocessedImage]:
        """Generate multiple preprocessed variants of a plate image.

        Returns a list of candidates ordered by likely OCR quality.
        """
        if plate_image is None or plate_image.size == 0:
            return []

        candidates = []

        # 1. Original (resized)
        resized = self._resize(plate_image)
        candidates.append(PreprocessedImage(resized, "original", "Resized original"))

        # 2. Grayscale + contrast
        gray = self._to_grayscale(resized)
        candidates.append(PreprocessedImage(gray, "grayscale", "Grayscale"))

        # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = self._apply_clahe(gray)
        candidates.append(PreprocessedImage(clahe, "clahe", "CLAHE enhanced"))

        # 4. Adaptive threshold
        thresh = self._adaptive_threshold(gray)
        candidates.append(PreprocessedImage(thresh, "threshold", "Adaptive threshold"))

        # 5. Sharpened
        sharp = self._sharpen(gray)
        candidates.append(PreprocessedImage(sharp, "sharpened", "Sharpened"))

        # 6. Denoised + CLAHE
        denoised = self._denoise(gray)
        denoised_clahe = self._apply_clahe(denoised)
        candidates.append(PreprocessedImage(denoised_clahe, "denoised_clahe", "Denoised + CLAHE"))

        return candidates

    def standard_preprocess(self, plate_image: np.ndarray) -> np.ndarray:
        """Standard single-pass preprocessing for high-confidence scenarios."""
        if plate_image is None or plate_image.size == 0:
            return plate_image

        img = self._resize(plate_image)
        img = self._to_grayscale(img)
        img = self._denoise(img)
        img = self._apply_clahe(img)
        return img

    def _resize(self, img: np.ndarray, target_height: int = 64) -> np.ndarray:
        """Resize maintaining aspect ratio."""
        h, w = img.shape[:2]
        if h == 0:
            return img
        scale = target_height / h
        new_w = int(w * scale)
        return cv2.resize(img, (new_w, target_height), interpolation=cv2.INTER_CUBIC)

    def _to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert to grayscale if needed."""
        if len(img.shape) == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def _apply_clahe(self, img: np.ndarray) -> np.ndarray:
        """Apply CLAHE for contrast enhancement."""
        gray = self._to_grayscale(img)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def _adaptive_threshold(self, img: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding."""
        gray = self._to_grayscale(img)
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    def _sharpen(self, img: np.ndarray) -> np.ndarray:
        """Sharpen the image."""
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(img, -1, kernel)

    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Denoise with bilateral filter."""
        gray = self._to_grayscale(img)
        return cv2.bilateralFilter(gray, 9, 75, 75)

    def _morphological_clean(self, img: np.ndarray) -> np.ndarray:
        """Apply morphological operations to clean up."""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        return img
