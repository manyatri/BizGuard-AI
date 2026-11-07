from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.order_schema import CheckoutRequest, OrderRead
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders & Fulfillment"])

@router.post("/checkout", response_model=OrderRead)
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    return OrderService.create_order(db, request)

@router.get("", response_model=List[OrderRead])
async def list_orders(
    status: Optional[str] = Query(None, description="Filter by status e.g. STALLED_INCONSISTENT"),
    db: Session = Depends(get_db)
):
    return OrderService.get_orders(db, status)

@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
