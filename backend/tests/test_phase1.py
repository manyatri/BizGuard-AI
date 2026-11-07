import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Base
from app.services.catalog_service import CatalogService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.workflow_engine import WorkflowEngine
from app.schemas.order_schema import CheckoutRequest, OrderItemCreate
from scripts.seed_clothing_data import seed

@pytest.fixture(scope="module")
def db():
    # Use isolated test database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    # Run seed on this memory database
    from app.models.catalog import Category, Product, ProductVariant, Inventory
    import uuid
    
    session = TestSessionLocal()
    cat_ethnic = Category(id=str(uuid.uuid4()), name="Ethnic Wear", slug="ethnic-wear")
    cat_western = Category(id=str(uuid.uuid4()), name="Western Dresses", slug="western-dresses")
    session.add_all([cat_ethnic, cat_western])
    session.commit()

    p_kurti = Product(
        id=str(uuid.uuid4()),
        category_id=cat_ethnic.id,
        title="Anarkali Embroidered Black Kurti",
        base_sku="BG-KRT-BLK",
        description="Handcrafted pure Chanderi silk kurti",
        fabric="100% Chanderi Silk",
        base_price=119.00,
        is_active=True
    )
    session.add(p_kurti)
    session.flush()

    for size, on_hand, reserved, bin_loc in [
        ("XS", 25, 2, "BIN-E1-04"),
        ("S", 40, 5, "BIN-E1-05"),
        ("M", 18, 0, "BIN-E1-06"),
        ("L", 12, 2, "BIN-E1-07"),
        ("XL", 8, 1, "BIN-E1-08"),
        ("XXL", 4, 0, "BIN-E1-09")
    ]:
        var = ProductVariant(
            id=str(uuid.uuid4()),
            product_id=p_kurti.id,
            sku=f"BG-KRT-BLK-{size}",
            size=size,
            color="Jet Black",
            color_code="#111111",
            price_adjustment=0.00
        )
        session.add(var)
        session.flush()

        inv = Inventory(
            id=str(uuid.uuid4()),
            variant_id=var.id,
            quantity_on_hand=on_hand,
            quantity_reserved=reserved,
            warehouse_bin=bin_loc,
            version=1
        )
        session.add(inv)

    session.commit()
    yield session
    session.close()

def test_catalog_and_variants_loaded(db):
    categories = CatalogService.get_categories(db)
    assert len(categories) >= 2
    
    products = CatalogService.get_products(db)
    assert len(products) >= 1

    kurti = next((p for p in products if p.base_sku == "BG-KRT-BLK"), None)
    assert kurti is not None
    assert kurti.title == "Anarkali Embroidered Black Kurti"
    assert len(kurti.variants) == 6

def test_variant_isolated_inventory(db):
    # Verify Size M has 18 on-hand, 0 reserved => 18 available
    var_m = CatalogService.get_variant_by_sku(db, "BG-KRT-BLK-M")
    assert var_m is not None
    assert var_m.inventory.quantity_on_hand == 18
    assert var_m.inventory.quantity_reserved == 0
    assert var_m.inventory.quantity_available == 18

    # Verify Size L has 12 on-hand, 2 reserved => 10 available
    var_l = CatalogService.get_variant_by_sku(db, "BG-KRT-BLK-L")
    assert var_l is not None
    assert var_l.inventory.quantity_on_hand == 12
    assert var_l.inventory.quantity_reserved == 2
    assert var_l.inventory.quantity_available == 10

def test_clean_order_checkout_lifecycle(db):
    var_m = CatalogService.get_variant_by_sku(db, "BG-KRT-BLK-M")
    initial_reserved = var_m.inventory.quantity_reserved

    checkout_req = CheckoutRequest(
        customer_name="Deepali Sharma",
        customer_email="deepali@fashionops.com",
        customer_phone="+91-9876543210",
        shipping_address={"city": "New Delhi", "country": "India"},
        items=[OrderItemCreate(variant_id=var_m.id, quantity=1)],
        payment_gateway="Razorpay Mock"
    )

    # Execute checkout
    order = OrderService.create_order(db, checkout_req)
    assert order is not None
    assert order.customer_name == "Deepali Sharma"
    assert order.status == "INVOICED"
    assert len(order.payments) == 1
    assert order.payments[0].status == "CAPTURED"
    assert len(order.invoices) == 1
    assert order.invoices[0].items[0].sku == "BG-KRT-BLK-M"

    # Verify Size M stock incremented reserved count
    db.refresh(var_m.inventory)
    assert var_m.inventory.quantity_reserved == initial_reserved + 1

    # Verify saga workflow events logged
    executions = WorkflowEngine.get_executions(db)
    matching_wf = next((ex for ex in executions if ex.order_id == order.id), None)
    assert matching_wf is not None
    assert len(matching_wf.events) == 4
    event_names = [ev.event_name for ev in matching_wf.events]
    assert "ORDER_PLACED" in event_names
    assert "PAYMENT_CAPTURED" in event_names
    assert "INVENTORY_ALLOCATED" in event_names
    assert "INVOICE_GENERATED" in event_names
