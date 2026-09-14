from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from .config import RecognitionConfig
from .pipeline import DetectionResult, FaceRecognitionPipeline


class CameraAgent:
    def __init__(self, camera_id: int = 0) -> None:
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)

    def capture_frame(self) -> Optional[np.ndarray]:
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self) -> None:
        self.cap.release()


class EdgeAgent:
    def __init__(self, pipeline: FaceRecognitionPipeline) -> None:
        self.pipeline = pipeline

    async def run_inference(self, frame: np.ndarray) -> List[DetectionResult]:
        await asyncio.sleep(0.01)
        return self.pipeline.process_frame(frame)


class PrivacyAgent:
    def __init__(self, policy: Optional[RecognitionConfig] = None) -> None:
        self.policy = policy or RecognitionConfig()

    async def enforce_policy(self, results: List[DetectionResult]) -> List[Dict[str, Any]]:
        sanitized: List[Dict[str, Any]] = []
        for result in results:
            entry = {
                "identity": result.identity,
                "confidence": result.confidence,
                "bbox": result.bbox,
                "unknown": result.unknown,
                "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            }
            if self.policy.privacy.mask_unknown_identities and result.unknown:
                entry["identity"] = "masked"
            sanitized.append(entry)
        return sanitized


class AlertAgent:
    async def trigger_alert(self, results: List[Dict[str, Any]]) -> None:
        for result in results:
            if result.get("identity") in {"unknown", "masked"}:
                print(f"ALERT: {result['identity']} detected at {result['timestamp']}")


class MonitoringAgent:
    async def track_metrics(self, results: List[Dict[str, Any]], duration_ms: float = 0.0) -> Dict[str, Any]:
        metrics = {
            "processed_count": len(results),
            "unknown_count": sum(1 for r in results if r.get("identity") in {"unknown", "masked"}),
            "latency_ms": round(duration_ms, 3),
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
        print(f"Monitoring: {metrics}")
        return metrics


async def orchestration_loop(camera_id: int = 0, known_identities: Optional[Dict[str, np.ndarray]] = None) -> None:
    config = RecognitionConfig()
    pipeline = FaceRecognitionPipeline(config=config)

    if known_identities:
        for name, embedding in known_identities.items():
            pipeline.add_identity(name, embedding)

    camera = CameraAgent(camera_id=camera_id)
    edge = EdgeAgent(pipeline=pipeline)
    privacy = PrivacyAgent(policy=config)
    alert = AlertAgent()
    monitor = MonitoringAgent()

    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            start = datetime.utcnow()
            results = await edge.run_inference(frame)
            sanitized = await privacy.enforce_policy(results)
            await alert.trigger_alert(sanitized)
            await monitor.track_metrics(sanitized, duration_ms=(datetime.utcnow() - start).total_seconds() * 1000)
    finally:
        camera.release()
