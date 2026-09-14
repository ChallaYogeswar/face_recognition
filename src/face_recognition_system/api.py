from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .audit import AuditLogger, hash_chain
from .compliance import ComplianceReportGenerator
from .privacy import ConsentManager

app = FastAPI(title="Face Recognition Compliance API")

consent_db = ConsentManager()
consent_db.update_consent("Alice", True)
consent_db.update_consent("Bob", False)
logger = AuditLogger(log_path="audit.log")
reporter = ComplianceReportGenerator()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return """
    <html>
      <head><title>Face Recognition Dashboard</title></head>
      <body>
        <h1>Face Recognition Dashboard</h1>
        <p>Audit logs, consent records, and monitoring metrics</p>
        <ul>
          <li>Camera frames: active</li>
          <li>Edge results: active</li>
          <li>Privacy policy: enforced</li>
          <li>Alerts: monitored</li>
        </ul>
      </body>
    </html>
    """


@app.get("/logs")
def get_logs(user_role: str) -> List[Dict[str, Any]]:
    if user_role != "auditor":
        raise HTTPException(status_code=403, detail="Access denied")
    logs: List[Dict[str, Any]] = []
    with open("audit.log", "rb") as handle:
        for line in handle:
            if not line.strip():
                continue
            logs.append({"encrypted": line.decode("utf-8", errors="ignore").strip()})
    return logs


@app.get("/consent/{identity}")
def get_consent(identity: str) -> Dict[str, Any]:
    return {"identity": identity, "consent": consent_db.check_consent(identity)}


@app.post("/consent/{identity}")
def update_consent(identity: str, status: bool) -> Dict[str, Any]:
    consent_db.update_consent(identity, status)
    return {"identity": identity, "status": status}


@app.get("/report/gdpr/{identity}")
def gdpr_report(identity: str, user_role: str) -> Dict[str, Any]:
    if user_role != "auditor":
        raise HTTPException(status_code=403, detail="Access denied")
    logs = [{"identity": identity, "camera": "A", "confidence": 0.97}]
    return reporter.build_gdpr_report(identity=identity, consent_status=consent_db.check_consent(identity), logs=logs)


@app.get("/report/itact")
def it_act_report(user_role: str) -> Dict[str, Any]:
    if user_role != "auditor":
        raise HTTPException(status_code=403, detail="Access denied")
    return reporter.build_it_act_report(
        logs=[{"identity": "Bob", "camera": "B", "confidence": 0.95}],
        violations=["consent violation for Bob"],
    )


@app.get("/hash-chain")
def get_hash_chain() -> Dict[str, Any]:
    return {"hashes": hash_chain("audit.log")}
