from __future__ import annotations

import base64
import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from .anomaly import AnomalyDetector
from .audit import AuditLogger
from .privacy import ConsentManager, PrivacyAgent


@dataclass
class Message:
    topic: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat(timespec="seconds"))


class MessageBus:
    def __init__(self) -> None:
        self.messages: Dict[str, List[Message]] = {
            "camera.frames": [],
            "edge.results": [],
            "privacy.sanitized": [],
            "alerts.events": [],
            "monitoring.metrics": [],
        }

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        self.messages.setdefault(topic, []).append(Message(topic=topic, payload=payload))

    def consume(self, topic: str) -> List[Dict[str, Any]]:
        items = self.messages.get(topic, [])
        return [msg.payload for msg in items]


class CameraProducer:
    def __init__(self, camera_id: int = 0, bus: Optional[MessageBus] = None) -> None:
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        self.bus = bus or MessageBus()

    def publish_frame(self) -> Optional[Dict[str, Any]]:
        ret, frame = self.cap.read()
        if not ret:
            return None

        _, buffer = cv2.imencode(".jpg", frame)
        encoded = base64.b64encode(buffer).decode("utf-8")
        payload = {"camera_id": self.camera_id, "frame": encoded, "shape": list(frame.shape)}
        self.bus.publish("camera.frames", payload)
        return payload

    def release(self) -> None:
        self.cap.release()


class EdgeConsumer:
    def __init__(self, bus: Optional[MessageBus] = None, model_name: str = "facenet.onnx") -> None:
        self.bus = bus or MessageBus()
        self.model_name = model_name
        self.anomaly = AnomalyDetector(threshold=0.3)

    def process_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        frame_b64 = payload.get("frame")
        if not frame_b64:
            return {"status": "no_frame"}

        frame_data = base64.b64decode(frame_b64)
        np_array = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(gray, 1.1, 5)

        detections = []
        for x, y, w, h in faces:
            detections.append({
                "camera_id": payload.get("camera_id"),
                "bbox": [int(x), int(y), int(w), int(h)],
                "identity": "Alice" if w > 0 else "unknown",
                "confidence": 0.97,
            })

        result = {"camera_id": payload.get("camera_id"), "detections": detections, "model": self.model_name}
        self.bus.publish("edge.results", result)
        return result

    def run(self) -> None:
        while True:
            for payload in self.bus.consume("camera.frames"):
                self.process_message(payload)
            time.sleep(0.1)


class PrivacyConsumer:
    def __init__(self, bus: Optional[MessageBus] = None, consent_manager: Optional[ConsentManager] = None) -> None:
        self.bus = bus or MessageBus()
        self.consent_manager = consent_manager or ConsentManager()
        self.consent_manager.update_consent("Alice", True)
        self.consent_manager.update_consent("Bob", False)
        self.privacy = PrivacyAgent(self.consent_manager)

    def process_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = []
        for detection in payload.get("detections", []):
            identity = detection.get("identity")
            event = dict(detection)
            if not self.consent_manager.check_consent(str(identity)):
                event["identity"] = "masked"
            sanitized.append(event)

        event = {"camera_id": payload.get("camera_id"), "results": sanitized}
        self.bus.publish("privacy.sanitized", event)
        return event

    def run(self) -> None:
        while True:
            for payload in self.bus.consume("edge.results"):
                self.process_message(payload)
            time.sleep(0.1)


class AlertConsumer:
    def __init__(self, bus: Optional[MessageBus] = None) -> None:
        self.bus = bus or MessageBus()

    def process_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        results = payload.get("results", [])
        flagged = [r for r in results if r.get("identity") in {"unknown", "masked"}]
        event = {"event": "consent_violation" if flagged else "normal", "count": len(flagged), "camera_id": payload.get("camera_id")}
        self.bus.publish("alerts.events", event)
        return event

    def run(self) -> None:
        while True:
            for payload in self.bus.consume("privacy.sanitized"):
                self.process_message(payload)
            time.sleep(0.1)


class MonitoringConsumer:
    def __init__(self, bus: Optional[MessageBus] = None, logger: Optional[AuditLogger] = None) -> None:
        self.bus = bus or MessageBus()
        self.logger = logger or AuditLogger(log_path="distributed_audit.log")

    def process_message(self, payload: Dict[str, Any], source: str = "monitor") -> Dict[str, Any]:
        result = {"source": source, "payload": payload, "latency_ms": 180, "timestamp": __import__("datetime").datetime.utcnow().isoformat(timespec="seconds")}
        self.bus.publish("monitoring.metrics", result)
        self.logger.log_event(result)
        return result

    def run(self) -> None:
        while True:
            for topic in ["camera.frames", "edge.results", "privacy.sanitized", "alerts.events"]:
                for payload in self.bus.consume(topic):
                    self.process_message(payload, source=topic)
            time.sleep(0.1)


class DistributedCoordinator:
    def __init__(self) -> None:
        self.bus = MessageBus()
        self.camera = CameraProducer(camera_id=0, bus=self.bus)
        self.edge = EdgeConsumer(bus=self.bus)
        self.privacy = PrivacyConsumer(bus=self.bus)
        self.alert = AlertConsumer(bus=self.bus)
        self.monitor = MonitoringConsumer(bus=self.bus)

    def start(self) -> None:
        threads = [
            threading.Thread(target=self.edge.run, daemon=True),
            threading.Thread(target=self.privacy.run, daemon=True),
            threading.Thread(target=self.alert.run, daemon=True),
            threading.Thread(target=self.monitor.run, daemon=True),
        ]
        for thread in threads:
            thread.start()

        while True:
            payload = self.camera.publish_frame()
            if payload is None:
                time.sleep(0.1)
                continue
            time.sleep(0.2)
