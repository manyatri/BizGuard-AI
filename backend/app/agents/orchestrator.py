"""
Agent Orchestrator — coordinates the 5-agent investigation & proposal workflow.
Pipeline:
  1. @monitor-agent     — Confirms incident and invariant violation state
  2. @investigator-agent— Identifies root cause and assembles forensic evidence
  3. @developer-agent   — Proposes atomic, reversible recovery actions
  4. @tester-agent      — Executes verification queries and checks pre-conditions
  5. @auditor-agent     — Audits safety and submits proposal to Approval Center
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.incidents import Incident
from app.agents.base_agent import AgentOutput
from app.agents.monitor_agent import MonitorAgent
from app.agents.investigator_agent import InvestigatorAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.tester_agent import TesterAgent
from app.agents.auditor_agent import AuditorAgent


class AgentOrchestrator:
    @staticmethod
    def run_incident_war_room(db: Session, incident: Incident) -> List[AgentOutput]:
        """
        Executes the full multi-agent collaborative investigation pipeline for an incident.
        """
        outputs: List[AgentOutput] = []
        context: Dict[str, Any] = {}

        # 1. Monitor agent
        monitor = MonitorAgent()
        out_monitor = monitor.run(db, incident, context)
        outputs.append(out_monitor)
        context["monitor_findings"] = out_monitor.findings

        # 2. Investigator agent
        investigator = InvestigatorAgent()
        out_inv = investigator.run(db, incident, context)
        outputs.append(out_inv)
        context["investigator_findings"] = out_inv.findings

        # 3. Developer agent
        developer = DeveloperAgent()
        out_dev = developer.run(db, incident, context)
        outputs.append(out_dev)
        context["developer_findings"] = out_dev.findings

        # 4. Tester agent
        tester = TesterAgent()
        out_test = tester.run(db, incident, context)
        outputs.append(out_test)
        context["tester_findings"] = out_test.findings

        # 5. Auditor agent
        auditor = AuditorAgent()
        out_audit = auditor.run(db, incident, context)
        outputs.append(out_audit)
        context["auditor_findings"] = out_audit.findings

        # Set incident status to PROPOSAL_READY
        incident.status = "PROPOSAL_READY"
        db.commit()

        return outputs
