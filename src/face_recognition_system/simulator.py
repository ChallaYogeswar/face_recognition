from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .anomaly import AnomalyDetector
from .audit import AuditLogger
from .privacy import ConsentManager, PrivacyAgent
from .scaling import PredictiveScaler


@dataclass
class SimulationEvent:
    event_type: str
    camera: str
    identity: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds"))


class EventBus:
    def __init__(self) -> None:
        self.topics: Dict[str, List[Dict[str, Any]]] = {
            "camera.frames": [],
            "edge.results": [],
            "privacy.sanitized": [],
            "alerts.events": [],
            "monitoring.metrics": [],
        }

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        self.topics.setdefault(topic, []).append(payload)

    def consume(self, topic: str) -> List[Dict[str, Any]]:
        return list(self.topics.get(topic, []))


class SimulationEngine:
    def __init__(self, bus: Optional[EventBus] = None) -> None:
        self.bus = bus or EventBus()
        self.consent_manager = ConsentManager()
        self.consent_manager.update_consent("Alice", True)
        self.consent_manager.update_consent("Bob", False)
        self.privacy_agent = PrivacyAgent(self.consent_manager)
        self.audit_logger = AuditLogger(log_path="simulation_audit.log")
        self.scaler = PredictiveScaler()
        self.anomaly_detector = AnomalyDetector(threshold=0.3)

    async def run(self) -> Dict[str, Any]:
        camera_a = SimulationEvent("detection", "A", "Alice", 0.97)
        camera_b = SimulationEvent("detection", "B", "Bob", 0.95)

        self.bus.publish("camera.frames", camera_a.__dict__)
        self.bus.publish("camera.frames", camera_b.__dict__)

        results = [
            {"identity": "Alice", "confidence": 0.97, "camera": "A"},
            {"identity": "Bob", "confidence": 0.95, "camera": "B"},
        ]
        self.bus.publish("edge.results", {"results": results})

        sanitized = self.privacy_agent.enforce_policy(results)
        self.bus.publish("privacy.sanitized", {"results": sanitized})

        for item in sanitized:
            self.audit_logger.log_event(item)

        violations = [entry for entry in sanitized if entry.get("identity") == "masked"]
        if violations:
            self.bus.publish("alerts.events", {"event": "consent_violation", "count": len(violations)})

        actual_load = 120.0
        forecast_load = 100.0
        self.scaler.record_load(actual_load)
        scaling_event = self.scaler.evaluate(threshold=100.0)

        anomaly_flag = self.anomaly_detector.detect(actual_load, forecast_load)
        monitoring_payload = {
            "latency_ms": 180,
            "throughput": "2 frames/sec",
            "alert_frequency": len(violations),
            "scaling": scaling_event.action,
            "anomaly": anomaly_flag,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
        self.bus.publish("monitoring.metrics", monitoring_payload)

        return {
            "sanitized_results": sanitized,
            "alerts": self.bus.consume("alerts.events"),
            "metrics": monitoring_payload,
            "scaling_event": scaling_event.action,
            "anomaly_detected": anomaly_flag,
        }
