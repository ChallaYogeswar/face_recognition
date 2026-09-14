from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from .config import RecognitionConfig
from .identity_store import IdentityStore
from .utils import normalize_face


@dataclass
class DetectionResult:
    identity: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    unknown: bool = False


class FaceRecognitionPipeline:
    def __init__(self, config: Optional[RecognitionConfig] = None, detector_path: Optional[str] = None) -> None:
        self.config = config or RecognitionConfig(detector_path=detector_path)
        self.identity_store = IdentityStore()
        self.detector = self._load_detector()

    def _load_detector(self):
        path = self.config.detector_path or cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(path)
        if detector.empty():
            raise FileNotFoundError(f"Face detector not found at: {path}")
        return detector

    def add_identity(self, name: str, embedding: np.ndarray) -> None:
        self.identity_store.add_identity(name, embedding)

    def process_frame(self, frame: np.ndarray) -> List[DetectionResult]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.config.min_face_size, self.config.min_face_size),
        )

        results: List[DetectionResult] = []
        for x, y, w, h in faces:
            roi = frame[y:y + h, x:x + w]
            embedding = self._build_embedding(roi)
            identity, score = self.identity_store.find_nearest(embedding)
            is_unknown = identity == "unknown" or score < self.config.threshold
            results.append(
                DetectionResult(
                    identity=(self.config.unknown_label if is_unknown else identity),
                    confidence=float(score if not is_unknown else max(score, 0.0)),
                    bbox=(int(x), int(y), int(w), int(h)),
                    unknown=is_unknown,
                )
            )
        return results

    def _build_embedding(self, face: np.ndarray) -> np.ndarray:
        normalized = normalize_face(face)
        flat = normalized.reshape(-1)
        return flat.astype(np.float32)

    def describe(self) -> Dict[str, Any]:
        return {
            "threshold": self.config.threshold,
            "known_identities": list(self.identity_store.as_dict().keys()),
            "unknown_label": self.config.unknown_label,
        }
