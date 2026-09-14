from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, DefaultDict, Dict, List, Optional


@dataclass
class KafkaMessage:
    topic: str
    value: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class InMemoryKafkaBus:
    def __init__(self) -> None:
        self._topics: DefaultDict[str, List[KafkaMessage]] = defaultdict(list)
        self._lock = Lock()

    def publish(self, topic: str, value: Dict[str, Any]) -> None:
        with self._lock:
            self._topics[topic].append(KafkaMessage(topic=topic, value=value))

    def consume(self, topic: str, timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        deadline = time.time() + (timeout or 0.0)
        messages: List[Dict[str, Any]] = []
        while True:
            with self._lock:
                batch = list(self._topics.get(topic, []))
            if batch:
                messages = [msg.value for msg in batch]
                break
            if timeout is not None and time.time() >= deadline:
                break
            time.sleep(0.05)
        return messages

    def get_all(self, topic: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [msg.value for msg in self._topics.get(topic, [])]


class KafkaCameraProducer:
    def __init__(self, bus: InMemoryKafkaBus, camera_id: str = "A") -> None:
        self.bus = bus
        self.camera_id = camera_id

    def publish_frame(self, payload: Dict[str, Any]) -> None:
        msg = {"camera_id": self.camera_id, **payload}
        self.bus.publish("camera.frames", msg)


class KafkaEdgeConsumer:
    def __init__(self, bus: InMemoryKafkaBus) -> None:
        self.bus = bus

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "camera_id": payload.get("camera_id"),
            "identity": "Alice" if payload.get("camera_id") == "A" else "Bob",
            "confidence": 0.97 if payload.get("camera_id") == "A" else 0.95,
            "source": "edge",
        }
        self.bus.publish("edge.results", result)
        return result

    def run_once(self) -> List[Dict[str, Any]]:
        messages = self.bus.consume("camera.frames")
        results = []
        for message in messages:
            results.append(self.process(message))
        return results


class KafkaPrivacyConsumer:
    def __init__(self, bus: InMemoryKafkaBus, consent_db: Optional[Dict[str, bool]] = None) -> None:
        self.bus = bus
        self.consent_db = consent_db or {"Alice": True, "Bob": False}

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        identity = payload.get("identity", "unknown")
        if identity not in self.consent_db or not self.consent_db[identity]:
            payload["identity"] = "masked"
        self.bus.publish("privacy.sanitized", payload)
        return payload

    def run_once(self) -> List[Dict[str, Any]]:
        messages = self.bus.consume("edge.results")
        results = []
        for message in messages:
            results.append(self.process(message))
        return results


class KafkaAlertConsumer:
    def __init__(self, bus: InMemoryKafkaBus) -> None:
        self.bus = bus

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {"event": "alert", "identity": payload.get("identity"), "camera_id": payload.get("camera_id")}
        self.bus.publish("alerts.events", event)
        return event

    def run_once(self) -> List[Dict[str, Any]]:
        messages = self.bus.consume("privacy.sanitized")
        results = []
        for message in messages:
            results.append(self.process(message))
        return results


class KafkaMonitoringConsumer:
    def __init__(self, bus: InMemoryKafkaBus) -> None:
        self.bus = bus

    def process(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {"topic": topic, "payload": payload, "latency_ms": 180, "timestamp": time.time()}
        self.bus.publish("monitoring.metrics", result)
        return result

    def run_once(self) -> List[Dict[str, Any]]:
        results = []
        for topic in ["camera.frames", "edge.results", "privacy.sanitized", "alerts.events"]:
            for message in self.bus.consume(topic):
                results.append(self.process(topic, message))
        return results
