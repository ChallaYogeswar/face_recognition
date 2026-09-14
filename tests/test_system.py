import json

from face_recognition_system.audit import AuditLogger, hash_chain
from face_recognition_system.compliance import ComplianceReportGenerator
from face_recognition_system.privacy import ConsentManager, PrivacyAgent


def test_privacy_masks_unknown_identity():
    consent = ConsentManager()
    consent.update_consent("Alice", True)
    consent.update_consent("Bob", False)

    agent = PrivacyAgent(consent_manager=consent)
    results = [{"identity": "Alice", "confidence": 0.95}, {"identity": "Bob", "confidence": 0.80}]

    masked = agent.enforce_policy(results)

    assert masked[0]["identity"] == "Alice"
    assert masked[1]["identity"] == "masked"


def test_audit_logger_encrypts_and_hashes_event(tmp_path):
    log_file = tmp_path / "audit.log"
    logger = AuditLogger(log_path=str(log_file))
    event = {"identity": "Alice", "camera": "A", "confidence": 0.97}

    logger.log_event(event)
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()

    assert len(lines) == 1
    payload = json.loads(logger.cipher.decrypt(lines[0].encode("utf-8")))
    assert payload["identity"] == "Alice"
    assert hash_chain(str(log_file))


def test_compliance_report_generation():
    generator = ComplianceReportGenerator()
    report = generator.build_gdpr_report(
        identity="Alice",
        consent_status=True,
        logs=[{"identity": "Alice", "camera": "A", "confidence": 0.97}],
    )

    assert report["identity"] == "Alice"
    assert report["consent"] is True
    assert len(report["logs"]) == 1
