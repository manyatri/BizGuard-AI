"""
@monitor-agent — scans for invariant violations and creates Incident records.
"""
from sqlalchemy.orm import Session
from app.models.incidents import Incident
from app.agents.base_agent import BaseAgent, AgentOutput, _utc
from app.services.invariant_detector import InvariantDetector
from typing import Any, Dict


class MonitorAgent(BaseAgent):
    agent_id = "@monitor-agent"
    agent_role = "MonitorAgent"
    message_type = "SCAN_REPORT"

    def run(self, db: Session, incident: Incident, context: Dict[str, Any]) -> AgentOutput:
        task = self._get_or_create_task(
            db, incident.id,
            "Run full invariant scan and report all detected business violations."
        )

        try:
            new_incidents = InvariantDetector.run_full_scan(db)
            all_incidents = InvariantDetector.get_all_incidents(db)

            findings = {
                "new_incidents_found": len(new_incidents),
                "total_incidents_in_db": len(all_incidents),
                "new_incident_codes": [i.incident_code for i in new_incidents],
                "rules_checked": [
                    "RULE_VARIANT_INVENTORY_MISMATCH",
                    "RULE_COLOR_INVENTORY_MISMATCH",
                    "RULE_NEGATIVE_INVENTORY",
                    "RULE_SHIPPED_WITHOUT_PAYMENT",
                    "RULE_DUPLICATE_PAYMENT",
                    "RULE_INVOICE_AMOUNT_MISMATCH",
                ],
            }

            new_codes = ", ".join(f"`{i.incident_code}`" for i in new_incidents) or "none"
            content = (
                f"🔍 **[@monitor-agent] Invariant Scan Complete**\n\n"
                f"**Rules evaluated**: {len(findings['rules_checked'])}\n"
                f"**New incidents detected this scan**: {len(new_incidents)}\n"
                f"**New incident codes**: {new_codes}\n"
                f"**Total incidents in database**: {len(all_incidents)}\n\n"
                f"**Current incident under investigation**: `{incident.incident_code}` — {incident.title}\n\n"
                f"**Detection rule triggered**: `{incident.detection_rule}`\n\n"
                "Handing off to @investigator-agent for root cause analysis."
            )

            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="full_invariant_scan",
                findings=findings,
                content_markdown=content,
                recommended_next_action="INVESTIGATE",
                execution_status="COMPLETED",
                llm_generated=False,
            )
            self._complete_task(db, task, output)
            return output

        except Exception as e:
            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="full_invariant_scan",
                findings={"error": str(e)},
                content_markdown=f"❌ **[@monitor-agent] Scan failed**: {e}",
                recommended_next_action="RETRY",
                execution_status="FAILED",
                error=str(e),
            )
            self._complete_task(db, task, output)
            return output
