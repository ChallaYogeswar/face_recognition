from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PrivacyPolicy:
    require_consent: bool = True
    mask_unknown_identities: bool = True
    retention_days: int = 90
    anonymize_logs: bool = True


@dataclass
class RecognitionConfig:
    detector_path: Optional[str] = None
    threshold: float = 0.62
    unknown_label: str = "unknown"
    min_face_size: int = 40
    privacy: PrivacyPolicy = field(default_factory=PrivacyPolicy)
    allowed_labels: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.allowed_labels is None:
            self.allowed_labels = []
