import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import root, health
from app.api.v1.catalog import list_categories, list_products
from app.api.v1.orders import list_orders
from app.api.v1.workflows import list_workflows
from app.core.database import Base
from app.services.catalog_service import CatalogService

@pytest.fixture(scope="module")
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    CatalogService.seed_catalog(session)
    yield session
    session.close()

@pytest.mark.asyncio
async def test_root_endpoint():
    data = await root()
    assert data["platform"] == "BizGuard AI"
    assert data["status"] == "OPERATIONAL"

@pytest.mark.asyncio
async def test_health_endpoint():
    data = await health()
    assert data["status"] == "HEALTHY"

@pytest.mark.asyncio
async def test_catalog_products_api(db):
    products = await list_products(db=db)
    assert len(products) >= 5
    kurti = next((p for p in products if p.base_sku == "BG-KRT-BLK"), None)
    assert kurti is not None
    assert kurti.title == "Anarkali Embroidered Black Kurti"

@pytest.mark.asyncio
async def test_catalog_categories_api(db):
    categories = await list_categories(db=db)
    assert len(categories) >= 4
    slugs = [c.slug for c in categories]
    assert "ethnic-wear" in slugs
    assert "western-dresses" in slugs

@pytest.mark.asyncio
async def test_orders_list_api(db):
    orders = await list_orders(db=db)
    assert isinstance(orders, list)

@pytest.mark.asyncio
async def test_workflows_list_api(db):
    workflows = await list_workflows(db=db)
    assert isinstance(workflows, list)
