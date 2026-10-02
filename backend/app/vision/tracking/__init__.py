"""VisionTrack ANPR — Multi-Object Tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from app.core.logging import get_logger
from app.vision.detection import BoundingBox

logger = get_logger("vision.tracking")


@dataclass
class TrackedObject:
    """A tracked vehicle across frames."""
    track_id: int
    bbox: BoundingBox
    age: int = 0  # frames since creation
    hits: int = 1  # total detection hits
    misses: int = 0  # consecutive frames without detection
    last_position: Tuple[float, float] = (0.0, 0.0)
    class_name: str = ""

    @property
    def center(self) -> Tuple[float, float]:
        return self.bbox.center


class SimpleTracker:
    """IoU-based multi-object tracker.

    Assigns stable IDs to vehicles across frames using
    bounding box IoU matching. Simpler and more robust
    than full Kalman filter for ANPR where we care about
    identity more than smooth trajectory.
    """

    def __init__(
        self,
        max_age: int = 30,  # frames to keep lost track
        min_hits: int = 3,   # minimum hits to confirm track
        iou_threshold: float = 0.3,
    ):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self._tracks: Dict[int, TrackedObject] = {}
        self._next_id = 1

    def update(self, detections: List[BoundingBox]) -> List[TrackedObject]:
        """Update tracks with new detections.

        Returns list of currently active tracks.
        """
        if not detections:
            # Age all tracks
            dead = []
            for tid, track in self._tracks.items():
                track.misses += 1
                track.age += 1
                if track.misses > self.max_age:
                    dead.append(tid)
            for tid in dead:
                del self._tracks[tid]
            return list(self._tracks.values())

        # Compute IoU matrix between existing tracks and new detections
        track_ids = list(self._tracks.keys())
        tracks = [self._tracks[tid] for tid in track_ids]

        if tracks:
            iou_matrix = self._compute_iou_matrix(tracks, detections)
            matched, unmatched_tracks, unmatched_detections = self._hungarian_match(
                iou_matrix, track_ids, detections
            )
        else:
            matched = []
            unmatched_tracks = []
            unmatched_detections = list(range(len(detections)))

        # Update matched tracks
        for track_id, det_idx in matched:
            track = self._tracks[track_id]
            track.bbox = detections[det_idx]
            track.hits += 1
            track.misses = 0
            track.age += 1
            track.class_name = detections[det_idx].class_name

        # Age unmatched tracks
        dead = []
        for tid in unmatched_tracks:
            self._tracks[tid].misses += 1
            self._tracks[tid].age += 1
            if self._tracks[tid].misses > self.max_age:
                dead.append(tid)
        for tid in dead:
            del self._tracks[tid]

        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            det = detections[det_idx]
            track = TrackedObject(
                track_id=self._next_id,
                bbox=det,
                class_name=det.class_name,
                last_position=det.center,
            )
            self._tracks[self._next_id] = track
            self._next_id += 1

        return list(self._tracks.values())

    def _compute_iou_matrix(
        self, tracks: List[TrackedObject], detections: List[BoundingBox]
    ) -> np.ndarray:
        """Compute IoU between all tracks and detections."""
        matrix = np.zeros((len(tracks), len(detections)))
        for i, track in enumerate(tracks):
            for j, det in enumerate(detections):
                matrix[i, j] = self._iou(track.bbox, det)
        return matrix

    def _hungarian_match(
        self, iou_matrix: np.ndarray, track_ids: List[int], detections: List[BoundingBox]
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """Greedy matching based on IoU (simple but effective)."""
        matched = []
        used_tracks = set()
        used_dets = set()

        # Sort by IoU descending
        rows, cols = np.where(iou_matrix > self.iou_threshold)
        ious = iou_matrix[rows, cols]
        indices = np.argsort(-ious)

        for idx in indices:
            r, c = rows[idx], cols[idx]
            if r not in used_tracks and c not in used_dets:
                matched.append((track_ids[r], c))
                used_tracks.add(r)
                used_dets.add(c)

        unmatched_tracks = [track_ids[i] for i in range(len(track_ids)) if i not in used_tracks]
        unmatched_dets = [i for i in range(len(detections)) if i not in used_dets]

        return matched, unmatched_tracks, unmatched_dets

    @staticmethod
    def _iou(box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate Intersection over Union between two boxes."""
        x1 = max(box1.x1, box2.x1)
        y1 = max(box1.y1, box2.y1)
        x2 = min(box1.x2, box2.x2)
        y2 = min(box1.y2, box2.y2)

        inter = max(0, x2 - x1) * max(0, y2 - y1)
        if inter == 0:
            return 0.0

        union = box1.area + box2.area - inter
        return inter / union if union > 0 else 0.0

    @property
    def active_track_count(self) -> int:
        return len(self._tracks)

    def get_confirmed_tracks(self) -> List[TrackedObject]:
        """Get tracks that have enough hits to be considered confirmed."""
        return [t for t in self._tracks.values() if t.hits >= self.min_hits]

    def reset(self):
        """Reset all tracks."""
        self._tracks.clear()
        self._next_id = 1
