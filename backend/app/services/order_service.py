import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from fastapi import HTTPException
from typing import List, Optional
from app.models.catalog import ProductVariant, Product
from app.models.orders import Order, OrderItem, Payment, Invoice, InvoiceItem
from app.models.workflow import WorkflowExecution
from app.schemas.order_schema import CheckoutRequest
from app.services.inventory_service import InventoryService
from app.services.workflow_engine import WorkflowEngine

class OrderService:
    @staticmethod
    def create_order(db: Session, request: CheckoutRequest) -> Order:
        order_id = str(uuid.uuid4())
        existing_orders_count = len(db.scalars(select(Order)).all())
        order_number = f"ORD-2026-{existing_orders_count + 42:04d}"

        # Initialize Order Workflow Execution Saga
        workflow = WorkflowEngine.create_execution(
            db=db,
            correlation_id=order_number,
            order_id=order_id,
            workflow_name="OrderFulfillmentSaga",
            initial_context={"customer": request.customer_name, "email": request.customer_email}
        )

        total_amount = 0.0
        order_items: List[OrderItem] = []

        # Validate variant items and calculate total
        for item_req in request.items:
            stmt = (
                select(ProductVariant)
                .where(ProductVariant.id == item_req.variant_id)
                .options(selectinload(ProductVariant.product), selectinload(ProductVariant.inventory))
            )
            variant = db.scalars(stmt).first()
            if not variant:
                raise HTTPException(status_code=404, detail=f"Variant {item_req.variant_id} does not exist")
            
            unit_price = float(variant.product.base_price) + float(variant.price_adjustment)
            subtotal = unit_price * item_req.quantity
            total_amount += subtotal

            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order_id,
                variant_id=variant.id,
                product_title=variant.product.title,
                ordered_size=variant.size,
                ordered_color=variant.color,
                quantity=item_req.quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )
            order_items.append(order_item)

        # 1. Create Order entity
        order = Order(
            id=order_id,
            order_number=order_number,
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            customer_phone=request.customer_phone,
            shipping_address=request.shipping_address or {"city": "New Delhi", "country": "India"},
            total_amount=total_amount,
            status="PENDING",
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        for oi in order_items:
            db.add(oi)
        db.commit()

        # Step 1 Event: ORDER_PLACED
        WorkflowEngine.log_event(
            db=db,
            execution_id=workflow.id,
            event_name="ORDER_PLACED",
            step_number=1,
            status="SUCCESS",
            payload={"order_number": order_number, "total_amount": total_amount, "items_count": len(order_items)}
        )

        # Step 2: Payment Capture Simulation
        payment_id = str(uuid.uuid4())
        tx_ref = f"tx_rzp_{uuid.uuid4().hex[:10]}"
        idempotency_key = f"idem_{order_number}_{uuid.uuid4().hex[:6]}"
        
        payment = Payment(
            id=payment_id,
            order_id=order_id,
            payment_gateway=request.payment_gateway,
            transaction_reference=tx_ref,
            amount=total_amount,
            currency="USD",
            status="CAPTURED",
            idempotency_key=idempotency_key,
            captured_at=datetime.now(timezone.utc)
        )
        db.add(payment)
        order.status = "PAYMENT_CAPTURED"
        db.commit()

        WorkflowEngine.log_event(
            db=db,
            execution_id=workflow.id,
            event_name="PAYMENT_CAPTURED",
            step_number=2,
            status="SUCCESS",
            payload={"transaction_reference": tx_ref, "amount": total_amount, "gateway": request.payment_gateway}
        )
        WorkflowEngine.transition_step(db, workflow.id, "2_PAYMENT_CAPTURED", "RUNNING")

        # Step 3: Reserve inventory for ordered variants
        for item in order_items:
            InventoryService.reserve_stock(db, item.variant_id, item.quantity)

        order.status = "INVENTORY_ALLOCATED"
        db.commit()

        WorkflowEngine.log_event(
            db=db,
            execution_id=workflow.id,
            event_name="INVENTORY_ALLOCATED",
            step_number=3,
            status="SUCCESS",
            payload={"variants_allocated": [item.variant_id for item in order_items]}
        )
        WorkflowEngine.transition_step(db, workflow.id, "3_INVENTORY_ALLOCATED", "RUNNING")

        # Step 4: Generate Invoice
        invoice_id = str(uuid.uuid4())
        invoice_number = f"INV-2026-{existing_orders_count + 42:04d}"
        invoice = Invoice(
            id=invoice_id,
            order_id=order_id,
            invoice_number=invoice_number,
            tax_amount=0.00,
            total_amount=total_amount,
            status="ISSUED",
            created_at=datetime.now(timezone.utc)
        )
        db.add(invoice)

        for item in order_items:
            var_obj = db.scalars(select(ProductVariant).where(ProductVariant.id == item.variant_id)).first()
            inv_item = InvoiceItem(
                id=str(uuid.uuid4()),
                invoice_id=invoice_id,
                variant_id=item.variant_id,
                sku=var_obj.sku if var_obj else "UNKNOWN",
                description=f"{item.product_title} - Size {item.ordered_size}",
                size=item.ordered_size,
                color=item.ordered_color,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(inv_item)

        order.status = "INVOICED"
        db.commit()

        WorkflowEngine.log_event(
            db=db,
            execution_id=workflow.id,
            event_name="INVOICE_GENERATED",
            step_number=4,
            status="SUCCESS",
            payload={"invoice_number": invoice_number, "total": total_amount}
        )
        WorkflowEngine.transition_step(db, workflow.id, "4_COMPLETED", "COMPLETED")

        return OrderService.get_order_by_id(db, order_id)

    @staticmethod
    def get_orders(db: Session, status: Optional[str] = None) -> List[Order]:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.invoices).selectinload(Invoice.items)
            )
            .order_by(Order.created_at.desc())
        )
        if status:
            stmt = stmt.where(Order.status == status)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments),
                selectinload(Order.invoices).selectinload(Invoice.items),
                selectinload(Order.workflow_executions).selectinload(WorkflowExecution.events)
            )
        )
        return db.scalars(stmt).first()
