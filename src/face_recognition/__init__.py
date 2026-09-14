"""Face recognition system package."""

from .pipeline import FaceRecognitionPipeline
from .agents import AlertAgent, CameraAgent, EdgeAgent, MonitoringAgent, PrivacyAgent

__all__ = [
    "FaceRecognitionPipeline",
    "AlertAgent",
    "CameraAgent",
    "EdgeAgent",
    "MonitoringAgent",
    "PrivacyAgent",
]
