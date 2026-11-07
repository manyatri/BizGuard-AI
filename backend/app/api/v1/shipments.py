"""
Shipments API
GET  /api/v1/shipments                       — list all shipments
POST /api/v1/shipments                       — create shipment for INVOICED order
PUT  /api/v1/shipments/{id}/status           — update delivery status
GET  /api/v1/shipments/{id}                  — single shipment
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.orders import Order, Shipment

router = APIRouter(prefix="/shipments", tags=["Shipments"])

VALID_STATUSES = ["MANIFESTED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "ON_HOLD"]


class CreateShipmentRequest(BaseModel):
    order_id: str
    carrier: Optional[str] = "FashionLogistics Express"


class UpdateStatusRequest(BaseModel):
    status: str


def _shipment_dict(s: Shipment) -> dict:
    return {
        "id": s.id,
        "order_id": s.order_id,
        "carrier": s.carrier,
        "tracking_number": s.tracking_number,
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        "order_number": s.order.order_number if s.order else None,
        "customer_name": s.order.customer_name if s.order else None,
    }


@router.get("")
async def list_shipments(db: Session = Depends(get_db)):
    shipments = db.scalars(
        select(Shipment)
        .options(selectinload(Shipment.order))
        .order_by(Shipment.created_at.desc())
    ).all()
    return {"total": len(shipments), "shipments": [_shipment_dict(s) for s in shipments]}


@router.post("")
async def create_shipment(body: CreateShipmentRequest, db: Session = Depends(get_db)):
    order = db.scalars(
        select(Order).where(Order.id == body.order_id)
        .options(selectinload(Order.shipments))
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {body.order_id} not found")
    if order.status not in ("INVOICED", "INVENTORY_ALLOCATED"):
        raise HTTPException(
            status_code=400,
            detail=f"Order must be INVOICED to create shipment. Current status: {order.status}",
        )
    if order.shipments:
        raise HTTPException(status_code=400, detail="Shipment already exists for this order")

    tracking = f"FL{uuid.uuid4().hex[:12].upper()}"
    shipment = Shipment(
        id=str(uuid.uuid4()),
        order_id=body.order_id,
        carrier=body.carrier,
        tracking_number=tracking,
        status="MANIFESTED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(shipment)
    order.status = "SHIPPED"
    db.commit()
    db.refresh(shipment)
    shipment.order = order  # attach for dict
    return _shipment_dict(shipment)


@router.put("/{shipment_id}/status")
async def update_shipment_status(
    shipment_id: str, body: UpdateStatusRequest, db: Session = Depends(get_db)
):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_STATUSES}")
    shipment = db.scalars(
        select(Shipment).where(Shipment.id == shipment_id).options(selectinload(Shipment.order))
    ).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
    shipment.status = body.status
    shipment.updated_at = datetime.now(timezone.utc)
    if body.status == "DELIVERED" and shipment.order:
        shipment.order.status = "DELIVERED"
    db.commit()
    return _shipment_dict(shipment)


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.scalars(
        select(Shipment).where(Shipment.id == shipment_id).options(selectinload(Shipment.order))
    ).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
    return _shipment_dict(shipment)
