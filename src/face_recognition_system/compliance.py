from __future__ import annotations

from typing import Any, Dict, List


class ComplianceReportGenerator:
    def build_gdpr_report(self, identity: str, consent_status: bool, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "report_type": "GDPR",
            "identity": identity,
            "consent": consent_status,
            "logs": logs,
            "anonymized_entries": sum(1 for item in logs if item.get("identity") == "masked"),
        }

    def build_it_act_report(self, logs: List[Dict[str, Any]], violations: List[str]) -> Dict[str, Any]:
        return {
            "report_type": "IT Act",
            "total_logs": len(logs),
            "consent_violations": len(violations),
            "violations": violations,
        }
