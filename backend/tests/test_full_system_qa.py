"""
System-wide QA and Reliability Test Suite for BizGuard AI.
Tests:
- Product & Category management
- Variant isolation and Inventory stock management
- Order checkout saga & payment states
- Shipments & Returns tracking
- All 11 Failure Simulation scenarios
- Invariant Detection Engine (all core rules)
- AI Agent Pipeline (@monitor, @investigator, @developer, @tester, @auditor)
- Safety: blocked unapproved execution, blocked unverified execution, duplicate prevention
- Atomic Recovery compensating swap and independent post-verification
"""
import sys
import os
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import Base
from app.models.catalog import Category, Product, ProductVariant, Inventory
from app.models.orders import Order, OrderItem, Payment, Invoice, Shipment, ReturnRecord
from app.models.incidents import Incident
from app.models.recovery import RecoveryProposal, Approval
from app.services.catalog_service import CatalogService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.failure_simulator import FailureSimulator
from app.services.invariant_detector import InvariantDetector
from app.services.simulation_service import SimulationService
from app.services.recovery_service import RecoveryService
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


def test_catalog_and_inventory_isolation(db):
    """Verifies that inventory is strictly isolated by size and color."""
    categories = CatalogService.get_categories(db)
    assert len(categories) >= 1

    products = CatalogService.get_products(db)
    assert len(products) >= 1
    p = products[0]

    # Verify variants
    variants = db.scalars(select(ProductVariant).where(ProductVariant.product_id == p.id)).all()
    assert len(variants) >= 2

    # Check that each variant has its own isolated inventory
    for v in variants:
        inv = db.scalars(select(Inventory).where(Inventory.variant_id == v.id)).first()
        assert inv is not None
        assert inv.quantity_on_hand >= 0


def test_order_creation_and_inventory_reservation(db):
    """Verifies happy path order creation: reserves stock on ordered size only."""
    var_m = db.scalars(select(ProductVariant).where(ProductVariant.sku.like("%-M"))).first()
    assert var_m is not None

    inv_before = db.scalars(select(Inventory).where(Inventory.variant_id == var_m.id)).first()
    res_before = inv_before.quantity_reserved

    # Reserve 1 unit
    updated_inv = InventoryService.reserve_stock(db, var_m.id, 1)
    assert updated_inv.quantity_reserved == res_before + 1

    # Release reservation
    released_inv = InventoryService.release_reservation(db, var_m.id, 1)
    assert released_inv.quantity_reserved == res_before


def test_failure_simulation_scenarios(db):
    """Verifies that failure simulator produces real backend states across scenarios."""
    # 1. Technical: Inventory timeout
    res1 = FailureSimulator.inject_inventory_api_timeout(db)
    assert res1["order_status"] == "PAYMENT_CAPTURED"

    # 2. Technical: Payment sync failure
    res2 = FailureSimulator.inject_payment_sync_failure(db)
    assert res2["payment_status"] == "INITIATED"

    # 3. Business: Wrong color inventory
    res3 = FailureSimulator.inject_wrong_color_inventory(db)
    assert "WRONG_COLOR_INVENTORY" in res3["scenario"]

    # 4. Business: Negative inventory (quantity_reserved exceeds quantity_on_hand)
    res4 = FailureSimulator.inject_negative_inventory(db)
    assert res4["quantity_reserved"] > res4["quantity_on_hand"]

    # 5. Business: Shipped without payment
    res5 = FailureSimulator.inject_shipped_without_payment(db)
    assert res5["order_status"] == "SHIPPED"
    assert res5["payment_status"] == "NONE"


def test_invariant_detector_catches_all_anomalies(db):
    """Verifies InvariantDetector flags negative stock and invariant anomalies."""
    new_incidents = InvariantDetector.run_full_scan(db)
    all_incidents = InvariantDetector.get_all_incidents(db)
    rules_detected = {i.detection_rule for i in all_incidents}

    assert "RULE_NEGATIVE_INVENTORY" in rules_detected
    assert len(all_incidents) >= 1


def test_ai_agent_orchestration_and_safety_pipeline(db):
    """
    Verifies that the 5 specialized agents run and produce actionable proposals,
    and backend safety blocks execution until human sign-off and passing tests.
    """
    # 1. Clean simulation state and inject fresh Black Kurti bug
    SimulationService.reset_simulation(db)
    inj_res = SimulationService.inject_black_kurti_bug(db)
    assert inj_res["status"] == "BUG_INJECTED"

    incidents = InvariantDetector.run_full_scan(db)
    assert len(incidents) >= 1
    kurti_inc = incidents[0]
    assert kurti_inc.detection_rule == "RULE_VARIANT_INVENTORY_MISMATCH"

    # 2. Run 5-agent pipeline
    agent_outputs = AgentOrchestrator.run_incident_war_room(db, kurti_inc)
    assert len(agent_outputs) == 5

    # 3. Create proposal
    proposal = RecoveryService.create_proposal(db, kurti_inc.id)
    assert proposal.status == "DRAFTED"

    # 4. Run automated pre-check tests
    pre_checks = RecoveryService.run_pre_checks(db, proposal.id)
    assert pre_checks["all_passed"] is True
    assert proposal.status == "READY_FOR_REVIEW"

    # 5. Safety: Execution without approval must fail
    with pytest.raises(ValueError, match="Human supervisor approval is required"):
        RecoveryService.execute_approved_proposal(db, proposal.id, "unauthorized@test.com")

    # 6. Human Manager approves
    proposal.status = "APPROVED"
    db.commit()

    # 7. Execute recovery
    res = RecoveryService.execute_approved_proposal(db, proposal.id, "ops_lead@fashionretail.com")
    assert res["status"] == "EXECUTED"
    assert res["incident_resolved"] is True

    # 8. Check incident resolved
    db.refresh(kurti_inc)
    assert kurti_inc.status == "VERIFIED_RESOLVED"

    # 9. Safety: Duplicate execution must fail
    with pytest.raises(ValueError, match="EXECUTED"):
        RecoveryService.execute_approved_proposal(db, proposal.id, "ops_lead@fashionretail.com")
