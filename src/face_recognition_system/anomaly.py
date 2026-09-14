from __future__ import annotations

from typing import List


class AnomalyDetector:
    def __init__(self, threshold: float = 0.3) -> None:
        self.threshold = threshold

    def detect(self, actual: float, forecast: float) -> bool:
        if forecast == 0:
            return actual > 0
        deviation = abs(actual - forecast) / forecast
        return deviation > self.threshold

    def detect_many(self, actual_values: List[float], forecast_values: List[float]) -> List[bool]:
        return [self.detect(actual, forecast) for actual, forecast in zip(actual_values, forecast_values)]
