"""
Returns & Refunds API
GET  /api/v1/returns               — list all returns
POST /api/v1/returns               — create return request
PUT  /api/v1/returns/{id}/approve  — approve and optionally restock
PUT  /api/v1/returns/{id}/reject   — reject return
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.orders import Order, ReturnRecord
from app.models.catalog import Inventory
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/returns", tags=["Returns"])


class CreateReturnRequest(BaseModel):
    order_id: str
    reason: str


class ApproveRequest(BaseModel):
    restock: Optional[bool] = True


def _return_dict(r: ReturnRecord) -> dict:
    return {
        "id": r.id,
        "order_id": r.order_id,
        "reason": r.reason,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "order_number": r.order.order_number if r.order else None,
        "customer_name": r.order.customer_name if r.order else None,
    }


@router.get("")
async def list_returns(db: Session = Depends(get_db)):
    returns = db.scalars(
        select(ReturnRecord)
        .options(selectinload(ReturnRecord.order))
        .order_by(ReturnRecord.created_at.desc())
    ).all()
    return {"total": len(returns), "returns": [_return_dict(r) for r in returns]}


@router.post("")
async def create_return(body: CreateReturnRequest, db: Session = Depends(get_db)):
    order = db.scalars(
        select(Order).where(Order.id == body.order_id)
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {body.order_id} not found")
    if order.status not in ("DELIVERED", "SHIPPED"):
        raise HTTPException(
            status_code=400,
            detail=f"Can only return DELIVERED or SHIPPED orders. Current: {order.status}",
        )
    ret = ReturnRecord(
        id=str(uuid.uuid4()),
        order_id=body.order_id,
        reason=body.reason,
        status="REQUESTED",
        created_at=datetime.now(timezone.utc),
    )
    db.add(ret)
    db.commit()
    db.refresh(ret)
    ret.order = order
    return _return_dict(ret)


@router.put("/{return_id}/approve")
async def approve_return(
    return_id: str, body: ApproveRequest, db: Session = Depends(get_db)
):
    ret = db.scalars(
        select(ReturnRecord)
        .where(ReturnRecord.id == return_id)
        .options(selectinload(ReturnRecord.order).selectinload(Order.items))
    ).first()
    if not ret:
        raise HTTPException(status_code=404, detail=f"Return {return_id} not found")
    if ret.status != "REQUESTED":
        raise HTTPException(status_code=400, detail=f"Return is already {ret.status}")

    ret.status = "APPROVED"

    if body.restock and ret.order and ret.order.items:
        for item in ret.order.items:
            inv = db.scalars(
                select(Inventory).where(Inventory.variant_id == item.variant_id)
            ).first()
            if inv:
                inv.quantity_on_hand += item.quantity
                # Release reservation too if still active
                inv.quantity_reserved = max(0, inv.quantity_reserved - item.quantity)
                inv.version += 1

    db.commit()
    return {"return_id": return_id, "status": "APPROVED", "restocked": body.restock}


@router.put("/{return_id}/reject")
async def reject_return(return_id: str, db: Session = Depends(get_db)):
    ret = db.scalars(
        select(ReturnRecord).where(ReturnRecord.id == return_id)
    ).first()
    if not ret:
        raise HTTPException(status_code=404, detail=f"Return {return_id} not found")
    ret.status = "REJECTED"
    db.commit()
    return {"return_id": return_id, "status": "REJECTED"}
