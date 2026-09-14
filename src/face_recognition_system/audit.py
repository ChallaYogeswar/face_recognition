from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

from cryptography.fernet import Fernet


class AuditLogger:
    def __init__(self, key: str | None = None, log_path: str = "audit.log") -> None:
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.log_path = log_path

    def log_event(self, event: Dict[str, Any]) -> str:
        payload = json.dumps(event, sort_keys=True).encode("utf-8")
        encrypted = self.cipher.encrypt(payload)
        with open(self.log_path, "ab") as handle:
            handle.write(encrypted + b"\n")
        return encrypted.decode("utf-8")


def hash_chain(log_file: str = "audit.log") -> List[str]:
    hashes: List[str] = []
    with open(log_file, "rb") as handle:
        for line in handle:
            h = hashlib.sha256(line).hexdigest()
            hashes.append(h)
    return hashes
