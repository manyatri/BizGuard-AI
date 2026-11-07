"""
Phase 2 test suite — Invariant Detection, Simulation, Recovery, Analytics.
All synchronous, uses in-memory SQLite (no asyncio needed).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import *  # noqa: F401,F403 — registers all models

# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def db():
    """In-memory SQLite session pre-seeded with clothing catalog."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed minimal clothing data for tests
    _seed_test_data(session)
    yield session
    session.close()


def _seed_test_data(db):
    """Seed the minimum data needed for Phase 2 tests."""
    import uuid
    from datetime import datetime, timezone
    from app.models.catalog import Category, Product, ProductVariant, Inventory

    cat = Category(id=str(uuid.uuid4()), name="Ethnic Wear", slug="ethnic-wear",
                   created_at=datetime.now(timezone.utc))
    db.add(cat)
    db.flush()

    product = Product(
        id=str(uuid.uuid4()), category_id=cat.id,
        title="Anarkali Black Kurti", base_sku="BG-KRT-BLK",
        fabric="Pure Cotton", base_price=2699.00, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    db.add(product)
    db.flush()

    var_m = ProductVariant(
        id=str(uuid.uuid4()), product_id=product.id,
        sku="BG-KRT-BLK-M", size="M", color="Jet Black",
        color_code="#111111", price_adjustment=0.0,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    var_l = ProductVariant(
        id=str(uuid.uuid4()), product_id=product.id,
        sku="BG-KRT-BLK-L", size="L", color="Jet Black",
        color_code="#111111", price_adjustment=0.0,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    db.add_all([var_m, var_l])
    db.flush()

    inv_m = Inventory(
        id=str(uuid.uuid4()), variant_id=var_m.id,
        quantity_on_hand=18, quantity_reserved=0,
        reorder_threshold=5, warehouse_bin="A-12", version=1,
        updated_at=datetime.now(timezone.utc),
    )
    inv_l = Inventory(
        id=str(uuid.uuid4()), variant_id=var_l.id,
        quantity_on_hand=12, quantity_reserved=0,
        reorder_threshold=5, warehouse_bin="A-13", version=1,
        updated_at=datetime.now(timezone.utc),
    )
    db.add_all([inv_m, inv_l])
    db.commit()


# ------------------------------------------------------------------ #
# Test 1: Invariant detection finds the size mismatch bug
# ------------------------------------------------------------------ #

def test_invariant_detection_finds_bug(db):
    """
    Manually inject the bug (reserve L when M was ordered), then run scan.
    Expect one CRITICAL incident created.
    """
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy import select
    from app.models.catalog import ProductVariant, Inventory
    from app.models.orders import Order, OrderItem
    from app.models.workflow import WorkflowExecution
    from app.services.invariant_detector import InvariantDetector

    # Load variants
    var_m = db.scalars(select(ProductVariant).where(ProductVariant.sku == "BG-KRT-BLK-M")).first()
    var_l = db.scalars(select(ProductVariant).where(ProductVariant.sku == "BG-KRT-BLK-L")).first()
    inv_m = db.scalars(select(Inventory).where(Inventory.variant_id == var_m.id)).first()
    inv_l = db.scalars(select(Inventory).where(Inventory.variant_id == var_l.id)).first()

    assert var_m is not None, "Size M variant must exist"
    assert var_l is not None, "Size L variant must exist"

    # Create the stalled order (ordered M, but we reserve L — the bug)
    order_id = str(uuid.uuid4())
    wf_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    wf = WorkflowExecution(
        id=wf_id, workflow_name="OrderFulfillmentSaga",
        correlation_id="ORD-TEST-0001", order_id=order_id,
        current_step="INVARIANT_BREACH_DETECTED",
        status="STALLED_INCONSISTENT",
        context_payload={}, started_at=now,
    )
    db.add(wf)

    order = Order(
        id=order_id, order_number="ORD-TEST-0001",
        customer_name="Test User", customer_email="test@example.com",
        total_amount=2699.0, status="STALLED_INCONSISTENT",
        created_at=now, updated_at=now,
    )
    db.add(order)

    item = OrderItem(
        id=str(uuid.uuid4()), order_id=order_id,
        variant_id=var_m.id,              # correctly points to M
        product_title="Anarkali Black Kurti",
        ordered_size="M", ordered_color="Jet Black",
        quantity=1, unit_price=2699.0, subtotal=2699.0,
    )
    db.add(item)

    # THE BUG: reserve on L, not M
    inv_l.quantity_reserved += 1
    inv_l.version += 1
    # inv_m stays at 0

    db.commit()

    # Run the invariant scan
    incidents = InvariantDetector.run_full_scan(db)

    assert len(incidents) >= 1, "Expected at least 1 incident"
    inc = incidents[0]
    assert inc.severity == "CRITICAL"
    assert "RULE_VARIANT_INVENTORY_MISMATCH" in inc.detection_rule
    assert inc.affected_order_id == order_id
    assert inc.status in ("DETECTED", "STALLED_INCONSISTENT")

    print(f"\n✅ Incident detected: {inc.incident_code} — {inc.root_cause_summary[:60]}...")


# ------------------------------------------------------------------ #
# Test 2: Simulation inject and reset
# ------------------------------------------------------------------ #

def test_simulation_inject_and_reset():
    """Inject bug via service on seeded bizguard.db, then reset."""
    # NOTE: This test uses the REAL database file (bizguard.db) since
    # SimulationService needs the seeded kurti variants.
    # We skip if the file doesn't exist.
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "bizguard.db")
    if not os.path.exists(db_path):
        pytest.skip("bizguard.db not found — run seed_clothing_data.py first")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()

    from app.services.simulation_service import SimulationService
    from app.models.orders import Order
    from sqlalchemy import select

    # Inject bug
    result = SimulationService.inject_black_kurti_bug(session)
    assert result["status"] == "BUG_INJECTED"
    assert result["affected_variants"]["wrongly_reserved_variant"]["sku"] == "BG-KRT-BLK-L"
    assert result["affected_variants"]["ordered_variant"]["sku"] == "BG-KRT-BLK-M"

    stalled = session.scalars(
        select(Order).where(Order.status == "STALLED_INCONSISTENT")
    ).all()
    assert len(stalled) >= 1

    # Reset
    reset_result = SimulationService.reset_simulation(session)
    assert reset_result["status"] == "RESET_COMPLETE"

    stalled_after = session.scalars(
        select(Order).where(Order.status == "STALLED_INCONSISTENT")
    ).all()
    assert len(stalled_after) == 0

    session.close()
    print("\n✅ Bug injection and reset cycle completed successfully")


# ------------------------------------------------------------------ #
# Test 3: Recovery proposal created with correct steps
# ------------------------------------------------------------------ #

def test_recovery_proposal_created(db):
    """After detection, create a recovery proposal and check its structure."""
    from sqlalchemy import select
    from app.models.incidents import Incident
    from app.services.recovery_service import RecoveryService

    # Find the incident created in test_1 (or any incident in test DB)
    incident = db.scalars(select(Incident)).first()
    if not incident:
        pytest.skip("No incident in test DB — run test_invariant_detection_finds_bug first")

    proposal = RecoveryService.create_proposal(db, incident.id)

    assert proposal.proposal_code.startswith("REC-2026-")
    assert proposal.status == "DRAFTED"
    assert proposal.risk_level == "LOW"
    assert isinstance(proposal.execution_steps, list)
    assert len(proposal.execution_steps) >= 4
    assert isinstance(proposal.rollback_steps, list)
    assert proposal.incident_id == incident.id

    # Verify incident updated
    db.refresh(incident)
    assert incident.status == "PROPOSAL_READY"

    print(f"\n✅ Proposal created: {proposal.proposal_code} with {len(proposal.execution_steps)} steps")


# ------------------------------------------------------------------ #
# Test 4: Analytics dashboard returns live data
# ------------------------------------------------------------------ #

def test_analytics_dashboard_returns_live_data(db):
    """Dashboard metrics must have all expected keys and correct types."""
    from app.services.analytics_service import AnalyticsService

    metrics = AnalyticsService.get_dashboard_metrics(db)

    expected_keys = [
        "total_products", "total_orders", "orders_by_status",
        "total_revenue", "active_incidents", "resolved_incidents",
        "avg_order_value", "low_stock_variants", "out_of_stock_variants",
        "pending_approvals", "mttd_minutes", "mttr_minutes",
        "workflow_success_rate", "generated_at",
    ]
    for key in expected_keys:
        assert key in metrics, f"Missing key: {key}"

    assert isinstance(metrics["total_products"], int)
    assert isinstance(metrics["total_orders"], int)
    assert isinstance(metrics["orders_by_status"], dict)
    assert isinstance(metrics["total_revenue"], float)
    assert isinstance(metrics["workflow_success_rate"], float)
    assert metrics["workflow_success_rate"] >= 0.0

    print(f"\n✅ Dashboard metrics: products={metrics['total_products']}, "
          f"orders={metrics['total_orders']}, revenue={metrics['total_revenue']}, "
          f"incidents={metrics['active_incidents']}")
