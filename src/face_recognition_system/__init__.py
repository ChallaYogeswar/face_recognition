"""Project-specific face recognition package."""

from .anomaly import AnomalyDetector
from .audit import AuditLogger, hash_chain
from .compliance import ComplianceReportGenerator
from .config import RecognitionConfig
from .distributed import AlertConsumer, CameraProducer, DistributedCoordinator, EdgeConsumer, MessageBus, MonitoringConsumer, PrivacyConsumer
from .identity_store import IdentityStore
from .kafka_bus import InMemoryKafkaBus, KafkaAlertConsumer, KafkaCameraProducer, KafkaEdgeConsumer, KafkaMonitoringConsumer, KafkaPrivacyConsumer
from .orchestration import AlertAgent, CameraAgent, EdgeAgent, MonitoringAgent, orchestration_loop
from .pipeline import DetectionResult, FaceRecognitionPipeline
from .privacy import ConsentManager, PrivacyAgent
from .scaling import PredictiveScaler, ScalingEvent
from .simulator import EventBus, SimulationEngine

__all__ = [
    "RecognitionConfig",
    "IdentityStore",
    "DetectionResult",
    "FaceRecognitionPipeline",
    "CameraAgent",
    "EdgeAgent",
    "AlertAgent",
    "MonitoringAgent",
    "orchestration_loop",
    "ConsentManager",
    "PrivacyAgent",
    "AuditLogger",
    "hash_chain",
    "ComplianceReportGenerator",
    "PredictiveScaler",
    "ScalingEvent",
    "AnomalyDetector",
    "EventBus",
    "SimulationEngine",
    "MessageBus",
    "CameraProducer",
    "EdgeConsumer",
    "PrivacyConsumer",
    "AlertConsumer",
    "MonitoringConsumer",
    "DistributedCoordinator",
    "InMemoryKafkaBus",
    "KafkaCameraProducer",
    "KafkaEdgeConsumer",
    "KafkaPrivacyConsumer",
    "KafkaAlertConsumer",
    "KafkaMonitoringConsumer",
]
