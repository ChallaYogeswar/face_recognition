from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScalingEvent:
    predicted_load: float
    threshold: float
    action: str


class PredictiveScaler:
    def __init__(self) -> None:
        self.history: List[float] = []

    def record_load(self, value: float) -> None:
        self.history.append(value)

    def predict(self) -> float:
        if not self.history:
            return 0.0
        return sum(self.history[-5:]) / max(len(self.history[-5:]), 1)

    def evaluate(self, threshold: float = 100.0) -> ScalingEvent:
        predicted = self.predict()
        if predicted > threshold:
            return ScalingEvent(predicted_load=predicted, threshold=threshold, action="scale_up")
        return ScalingEvent(predicted_load=predicted, threshold=threshold, action="scale_down")
