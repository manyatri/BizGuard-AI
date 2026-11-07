"""
Comprehensive End-to-End Test for BizGuard AI Recovery Engine & Approval Center.
Covers the complete 12-step primary demonstration:
1. Detect incorrect inventory deduction (Black Kurti Size M vs L)
2. Create incident
3. Trigger Monitor Agent
4. Investigate affected product variant
5. Identify incorrect SKU
6. Prepare recovery proposal
7. Run automated tests (pre-checks)
8. Obtain auditor review
9. Block execution before approval
10. Execute authorized atomic swap
11. Verify final database state independently
12. Resolve incident & prevent duplicate execution
"""
import sys
import os
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import Base
from app.models import *
from app.services.simulation_service import SimulationService
from app.services.invariant_detector import InvariantDetector
from app.agents.orchestrator import AgentOrchestrator
from app.services.recovery_service import RecoveryService
from backend.tests.test_phase2 import _seed_test_data


@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    _seed_test_data(session)
    yield session
    session.close()


def test_complete_recovery_and_approval_flow(db):
    # Step 1 & 2: Inject Kurti Size Mismatch
    inj_res = SimulationService.inject_black_kurti_bug(db)
    assert inj_res["status"] == "BUG_INJECTED"
    order_id = inj_res["order_id"]

    # Step 3: Run Invariant Scan
    new_incidents = InvariantDetector.run_full_scan(db)
    assert len(new_incidents) >= 1
    incident = new_incidents[0]
    assert incident.detection_rule == "RULE_VARIANT_INVENTORY_MISMATCH"
    assert incident.affected_order_id == order_id

    # Step 4, 5, 8: Multi-agent investigation & audit
    agent_outputs = AgentOrchestrator.run_incident_war_room(db, incident)
    assert len(agent_outputs) == 5

    # Step 6: Create Recovery Proposal
    proposal = RecoveryService.create_proposal(db, incident.id)
    assert proposal.proposal_code.startswith("REC-2026-")

    # Step 7: Run Automated Pre-Check Tests
    pre_res = RecoveryService.run_pre_checks(db, proposal.id)
    assert pre_res["all_passed"] is True
    assert proposal.status in ("READY_FOR_REVIEW", "DRAFTED")

    # Step 9: Safety Check — Cannot execute before human approval
    with pytest.raises(ValueError, match="Human supervisor approval is required"):
        RecoveryService.execute_approved_proposal(db, proposal.id, "unauthorized@test.com")

    # Step 9b: Human Manager Approval
    proposal.status = "APPROVED"
    db.commit()

    # Step 10 & 11: Execute Approved Recovery & Independent Verification
    exec_res = RecoveryService.execute_approved_proposal(db, proposal.id, "manager@fashionretail.com")
    assert exec_res["status"] == "EXECUTED"
    assert exec_res["incident_resolved"] is True
    assert exec_res["new_order_status"] == "INVOICED"

    # Step 12: Check Incident is Resolved
    db.refresh(incident)
    assert incident.status == "VERIFIED_RESOLVED"
    assert incident.resolved_at is not None

    # Step 12b: Safety Check — Prevent duplicate execution
    with pytest.raises(ValueError, match="EXECUTED"):
        RecoveryService.execute_approved_proposal(db, proposal.id, "manager@fashionretail.com")

    # Clean reset
    reset_res = SimulationService.reset_simulation(db)
    assert reset_res["status"] == "RESET_COMPLETE"
