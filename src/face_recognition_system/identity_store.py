from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


def _normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    emb = np.asarray(embedding, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(emb)
    if norm == 0:
        return emb
    return emb / norm


class IdentityStore:
    def __init__(self) -> None:
        self._identities: Dict[str, np.ndarray] = {}

    def add_identity(self, name: str, embedding: np.ndarray) -> None:
        if not name:
            raise ValueError("Identity name cannot be empty.")
        self._identities[name] = _normalize_embedding(embedding)

    def find_nearest(self, embedding: np.ndarray) -> Tuple[str, float]:
        if not self._identities:
            return "unknown", 0.0

        candidate = _normalize_embedding(embedding)
        best_name = "unknown"
        best_score = 0.0
        for name, known in self._identities.items():
            score = float(np.dot(candidate, known))
            if score > best_score:
                best_score = score
                best_name = name
        return best_name, best_score

    def as_dict(self) -> Dict[str, np.ndarray]:
        return dict(self._identities)

    def clear(self) -> None:
        self._identities.clear()
