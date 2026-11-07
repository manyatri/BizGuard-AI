"""
Tests for extended failure simulation and invariant rules.
"""
import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import Base
from app.models import *
from app.services.failure_simulator import FailureSimulator
from app.services.invariant_detector import InvariantDetector
from app.services.simulation_service import SimulationService
from app.agents.orchestrator import AgentOrchestrator
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


def test_failure_scenarios_and_invariant_detection(db):
    # 1. Test black kurti size mismatch injection
    kurti_res = SimulationService.inject_black_kurti_bug(db)
    assert kurti_res["status"] == "BUG_INJECTED"

    # 2. Invariant detector catches size mismatch
    incidents = InvariantDetector.run_full_scan(db)
    assert len(incidents) >= 1
    inc = incidents[0]
    assert inc.detection_rule == "RULE_VARIANT_INVENTORY_MISMATCH"

    # 3. Test multi-agent war room orchestration
    outputs = AgentOrchestrator.run_incident_war_room(db, inc)
    assert len(outputs) == 5
    assert any(o.agent_id == "@investigator-agent" for o in outputs)
    assert any(o.agent_id == "@auditor-agent" for o in outputs)

    # 4. Clean simulation reset
    reset_res = SimulationService.reset_simulation(db)
    assert reset_res["status"] == "RESET_COMPLETE"
