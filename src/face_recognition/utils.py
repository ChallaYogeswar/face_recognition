import base64
import hashlib
import json
import os
from typing import Any, Dict, Iterable, List

import cv2
import numpy as np


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def resize_with_padding(image: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    height, width = image.shape[:2]
    target_h, target_w = target_size
    scale = min(target_h / height, target_w / width)
    new_w = max(1, int(width * scale))
    new_h = max(1, int(height * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    y = (target_h - new_h) // 2
    x = (target_w - new_w) // 2
    canvas[y:y + new_h, x:x + new_w] = resized
    return canvas


def normalize_face(face: np.ndarray) -> np.ndarray:
    face = np.asarray(face, dtype=np.float32)
    if face.ndim == 2:
        face = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
    if face.shape[-1] == 4:
        face = cv2.cvtColor(face, cv2.COLOR_BGRA2BGR)
    face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_LINEAR)
    face = face / 255.0
    return face.astype(np.float32)


def image_to_base64(frame: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_dump(obj: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)


def append_event_log(path: str, event: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
