from fastapi.testclient import TestClient

from face_recognition_system.api import app
from face_recognition_system.kafka_bus import InMemoryKafkaBus


def test_in_memory_bus_round_trip():
    bus = InMemoryKafkaBus()
    bus.publish("camera.frames", {"camera": "A", "status": "ok"})
    messages = bus.consume("camera.frames")

    assert len(messages) == 1
    assert messages[0]["camera"] == "A"


def test_dashboard_route_serves_html():
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Face Recognition Dashboard" in response.text
