from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from .config import RecognitionConfig
from .pipeline import FaceRecognitionPipeline


@dataclass
class EventMessage:
    source: str
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)


class CameraAgent:
    def __init__(self, camera_id: int = 0, message_queue: Optional[List[EventMessage]] = None) -> None:
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        self.messages = message_queue if message_queue is not None else []

    def capture_frame(self) -> Optional[np.ndarray]:
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def publish_frame(self, frame: np.ndarray) -> None:
        self.messages.append(
            EventMessage(
                source=f"camera_{self.camera_id}",
                topic="camera.frames",
                payload={"camera_id": self.camera_id, "frame_shape": list(frame.shape)},
            )
        )

    def release(self) -> None:
        self.cap.release()


class EdgeAgent:
    def __init__(self, pipeline: FaceRecognitionPipeline) -> None:
        self.pipeline = pipeline

    async def run_inference(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        detections = self.pipeline.process_frame(frame)
        return [
            {
                "identity": d.identity,
                "confidence": d.confidence,
                "bbox": list(d.bbox),
                "unknown": d.unknown,
            }
            for d in detections
        ]


class AlertAgent:
    async def trigger_alert(self, results: List[Dict[str, Any]]) -> None:
        for result in results:
            if result.get("identity") in {"unknown", "masked"}:
                print(f"ALERT: {result['identity']} detected")


class MonitoringAgent:
    async def track_metrics(self, results: List[Dict[str, Any]], latency_ms: float = 0.0) -> Dict[str, Any]:
        return {
            "processed_count": len(results),
            "latency_ms": latency_ms,
            "unknown_count": sum(1 for r in results if r.get("identity") in {"unknown", "masked"}),
        }


async def orchestration_loop(camera_id: int = 0, pipeline: Optional[FaceRecognitionPipeline] = None) -> None:
    config = RecognitionConfig()
    recognition_pipeline = pipeline or FaceRecognitionPipeline(config=config)
    camera = CameraAgent(camera_id=camera_id)
    edge = EdgeAgent(recognition_pipeline)
    alert = AlertAgent()
    monitor = MonitoringAgent()

    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            results = await edge.run_inference(frame)
            await alert.trigger_alert(results)
            await monitor.track_metrics(results)
    finally:
        camera.release()
