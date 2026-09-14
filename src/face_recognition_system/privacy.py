from __future__ import annotations

from typing import Any, Dict, List, Optional


class ConsentManager:
    def __init__(self) -> None:
        self.consent_db: Dict[str, bool] = {}

    def check_consent(self, identity: str) -> bool:
        return bool(self.consent_db.get(identity, False))

    def update_consent(self, identity: str, status: bool) -> None:
        self.consent_db[identity] = bool(status)


class PrivacyAgent:
    def __init__(self, consent_manager: Optional[ConsentManager] = None) -> None:
        self.consent_manager = consent_manager or ConsentManager()

    def enforce_policy(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sanitized: List[Dict[str, Any]] = []
        for result in results:
            entry = dict(result)
            identity = str(entry.get("identity", "unknown"))
            if not self.consent_manager.check_consent(identity):
                entry["identity"] = "masked"
            sanitized.append(entry)
        return sanitized
