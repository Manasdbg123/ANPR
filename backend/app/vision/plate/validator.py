"""VisionTrack ANPR — Indian Number Plate Validator."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger("vision.plate.validator")

# Indian state and union territory codes
INDIAN_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "GA",
    "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH",
    "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ", "SK",
    "TN", "TS", "TR", "UK", "UP", "WB",
}


@dataclass
class ValidationResult:
    """Result of plate validation."""
    text: str
    valid: bool
    confidence: float
    normalized_text: str
    state_code: str | None = None
    district_code: str | None = None
    series: str | None = None
    number: str | None = None
    format_type: str | None = None  # "standard", "commercial", etc.


class PlateValidator:
    """Validates and normalizes Indian vehicle registration plates.

    Supports multiple plate formats:
    - Standard: XX00XX0000 (e.g., DL01AB1234)
    - Commercial: XX00X0000 (e.g., MH04J5678)
    - Short series: XX00XX000 (3-digit number)
    - BH series: BH00XX0000 (Bharat series)
    """

    # Patterns ordered by specificity
    PATTERNS = [
        # Standard format: DL01AB1234
        (r'^([A-Z]{2})(\d{2})([A-Z]{1,3})(\d{1,4})$', "standard"),
        # BH series: 22BH1234AB
        (r'^(\d{2})(BH)(\d{4})([A-Z]{1,2})$', "bh_series"),
    ]

    def __init__(self, strict: bool = False):
        self.strict = strict
        self._compiled = [(re.compile(p), t) for p, t in self.PATTERNS]

    def validate(self, text: str, ocr_confidence: float = 0.0) -> ValidationResult:
        """Validate a plate number against known Indian formats."""
        if not text:
            return ValidationResult(
                text="", valid=False, confidence=0.0, normalized_text=""
            )

        # Normalize input
        normalized = text.upper().strip()
        normalized = re.sub(r'[^A-Z0-9]', '', normalized)

        # Try each pattern
        for pattern, fmt_type in self._compiled:
            match = pattern.match(normalized)
            if match:
                groups = match.groups()

                if fmt_type == "standard":
                    state = groups[0]
                    district = groups[1]
                    series = groups[2]
                    number = groups[3]

                    # Validate state code
                    state_valid = state in INDIAN_STATE_CODES
                    if self.strict and not state_valid:
                        continue

                    # Build confidence
                    validity_confidence = ocr_confidence
                    if state_valid:
                        validity_confidence = min(1.0, validity_confidence + 0.1)
                    if len(number) == 4:
                        validity_confidence = min(1.0, validity_confidence + 0.05)

                    return ValidationResult(
                        text=text,
                        valid=True,
                        confidence=round(validity_confidence, 3),
                        normalized_text=f"{state}{district}{series}{number}",
                        state_code=state,
                        district_code=district,
                        series=series,
                        number=number,
                        format_type=fmt_type,
                    )

                elif fmt_type == "bh_series":
                    year = groups[0]
                    bh = groups[1]
                    number = groups[2]
                    series = groups[3]

                    return ValidationResult(
                        text=text,
                        valid=True,
                        confidence=round(ocr_confidence + 0.05, 3),
                        normalized_text=f"{year}{bh}{number}{series}",
                        state_code="BH",
                        district_code=year,
                        series=series,
                        number=number,
                        format_type=fmt_type,
                    )

        # No pattern matched
        # Still could be a valid plate with OCR errors
        partial_valid = self._partial_validate(normalized)

        return ValidationResult(
            text=text,
            valid=partial_valid,
            confidence=round(ocr_confidence * 0.7 if partial_valid else 0.0, 3),
            normalized_text=normalized,
        )

    def _partial_validate(self, text: str) -> bool:
        """Partial validation for plates that don't match exact patterns.

        Returns True if the text looks plate-like enough.
        """
        if len(text) < 6 or len(text) > 12:
            return False

        # Should start with 2 letters (state code)
        if len(text) >= 2 and text[:2].isalpha():
            # Should have digits after state code
            if len(text) >= 4 and text[2:4].isdigit():
                return True

        return False
