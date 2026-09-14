from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from .config import RecognitionConfig
from .identity_store import IdentityStore


def _normalize_face(face: np.ndarray) -> np.ndarray:
    face = np.asarray(face, dtype=np.float32)
    if face.ndim == 2:
        face = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
    if face.shape[-1] == 4:
        face = cv2.cvtColor(face, cv2.COLOR_BGRA2BGR)
    face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_LINEAR)
    face = face / 255.0
    return face.astype(np.float32)


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
        return _normalize_face(face).reshape(-1).astype(np.float32)

    def describe(self) -> Dict[str, Any]:
        return {
            "threshold": self.config.threshold,
            "known_identities": list(self.identity_store.as_dict().keys()),
            "unknown_label": self.config.unknown_label,
        }
