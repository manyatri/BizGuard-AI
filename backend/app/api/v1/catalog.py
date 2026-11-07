from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.catalog_schema import CategoryRead, ProductRead, VariantRead, InventoryRead
from app.services.catalog_service import CatalogService
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/catalog", tags=["Catalog & Inventory"])

@router.get("/categories", response_model=List[CategoryRead])
async def list_categories(db: Session = Depends(get_db)):
    return CatalogService.get_categories(db)

@router.get("/products", response_model=List[ProductRead])
async def list_products(
    category_slug: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return CatalogService.get_products(db, category_slug)

@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = CatalogService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/variants/{variant_id}", response_model=VariantRead)
async def get_variant(variant_id: str, db: Session = Depends(get_db)):
    variant = CatalogService.get_variant_by_id(db, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant

@router.get("/variants/{variant_id}/inventory", response_model=InventoryRead)
async def get_inventory(variant_id: str, db: Session = Depends(get_db)):
    inventory = InventoryService.get_inventory_for_variant(db, variant_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for variant")
    return inventory
