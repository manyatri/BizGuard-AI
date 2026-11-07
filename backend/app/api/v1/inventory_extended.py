"""
Inventory Extended API — variant-level stock management.
GET /api/v1/inventory                     — all inventory records
PUT /api/v1/inventory/{variant_id}/adjust — adjust on-hand stock
GET /api/v1/inventory/low-stock           — below reorder threshold
GET /api/v1/inventory/out-of-stock        — zero available
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.catalog import Inventory, ProductVariant, Product
from app.models.audit import AuditLog

router = APIRouter(prefix="/inventory", tags=["Inventory"])


class StockAdjustRequest(BaseModel):
    quantity_delta: int   # positive = add stock, negative = remove stock
    reason: str


def _inv_dict(inv: Inventory) -> dict:
    variant = inv.variant
    product = variant.product if variant else None
    available = max(0, inv.quantity_on_hand - inv.quantity_reserved)
    if available == 0:
        health = "OUT_OF_STOCK"
    elif available <= inv.reorder_threshold:
        health = "LOW_STOCK"
    else:
        health = "HEALTHY"

    return {
        "inventory_id": inv.id,
        "variant_id": inv.variant_id,
        "sku": variant.sku if variant else None,
        "size": variant.size if variant else None,
        "color": variant.color if variant else None,
        "color_code": variant.color_code if variant else None,
        "product_title": product.title if product else None,
        "product_id": product.id if product else None,
        "quantity_on_hand": inv.quantity_on_hand,
        "quantity_reserved": inv.quantity_reserved,
        "quantity_available": available,
        "reorder_threshold": inv.reorder_threshold,
        "warehouse_bin": inv.warehouse_bin,
        "health_status": health,
        "version": inv.version,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
    }


@router.get("")
async def list_inventory(db: Session = Depends(get_db)):
    """List all inventory records with variant and product details."""
    inventories = db.scalars(
        select(Inventory)
        .options(
            selectinload(Inventory.variant).selectinload(ProductVariant.product)
        )
        .order_by(Inventory.variant_id)
    ).all()
    items = [_inv_dict(i) for i in inventories]
    return {
        "total": len(items),
        "summary": {
            "healthy": sum(1 for i in items if i["health_status"] == "HEALTHY"),
            "low_stock": sum(1 for i in items if i["health_status"] == "LOW_STOCK"),
            "out_of_stock": sum(1 for i in items if i["health_status"] == "OUT_OF_STOCK"),
        },
        "inventory": items,
    }


@router.put("/{variant_id}/adjust")
async def adjust_stock(
    variant_id: str, body: StockAdjustRequest, db: Session = Depends(get_db)
):
    """Adjust on-hand stock quantity for a variant (positive=add, negative=remove)."""
    inv = db.scalars(
        select(Inventory)
        .where(Inventory.variant_id == variant_id)
        .options(selectinload(Inventory.variant))
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"Inventory for variant {variant_id} not found")

    new_qty = inv.quantity_on_hand + body.quantity_delta
    if new_qty < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reduce stock below 0. Current: {inv.quantity_on_hand}, Delta: {body.quantity_delta}",
        )
    if new_qty < inv.quantity_reserved:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reduce on-hand below reserved ({inv.quantity_reserved}). New qty would be {new_qty}.",
        )

    before = {"quantity_on_hand": inv.quantity_on_hand}
    inv.quantity_on_hand = new_qty
    inv.version += 1

    # Audit log
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        entity_name="inventories",
        entity_id=inv.id,
        action_type="STOCK_ADJUSTED",
        actor_type="OPERATOR",
        actor_id="system",
        before_state=before,
        after_state={"quantity_on_hand": new_qty},
        notes=body.reason,
        timestamp=datetime.now(timezone.utc),
    ))
    db.commit()
    db.refresh(inv)

    return {
        "variant_id": variant_id,
        "sku": inv.variant.sku if inv.variant else None,
        "quantity_on_hand": inv.quantity_on_hand,
        "quantity_reserved": inv.quantity_reserved,
        "quantity_available": inv.quantity_available,
        "adjustment": body.quantity_delta,
        "reason": body.reason,
    }


@router.get("/low-stock")
async def low_stock_variants(db: Session = Depends(get_db)):
    """Returns variants at or below reorder threshold."""
    inventories = db.scalars(
        select(Inventory)
        .where(
            (Inventory.quantity_on_hand - Inventory.quantity_reserved) <= Inventory.reorder_threshold,
            (Inventory.quantity_on_hand - Inventory.quantity_reserved) > 0,
        )
        .options(selectinload(Inventory.variant).selectinload(ProductVariant.product))
    ).all()
    return {"total": len(inventories), "variants": [_inv_dict(i) for i in inventories]}


@router.get("/out-of-stock")
async def out_of_stock_variants(db: Session = Depends(get_db)):
    """Returns variants with zero available stock."""
    inventories = db.scalars(
        select(Inventory)
        .where((Inventory.quantity_on_hand - Inventory.quantity_reserved) <= 0)
        .options(selectinload(Inventory.variant).selectinload(ProductVariant.product))
    ).all()
    return {"total": len(inventories), "variants": [_inv_dict(i) for i in inventories]}
