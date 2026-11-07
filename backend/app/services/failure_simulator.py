"""
Extended Failure Simulation Engine — 15+ failure scenarios for demo.
Each scenario produces real backend state changes, not just notifications.
"""
import uuid
import random
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, delete
from app.models.catalog import ProductVariant, Inventory, Product
from app.models.orders import Order, OrderItem, Payment, Invoice, InvoiceItem
from app.models.workflow import WorkflowExecution, WorkflowEvent
from app.models.incidents import Incident
from app.models.audit import AuditLog


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def _seq_num(db, model) -> int:
    from sqlalchemy import func
    return (db.scalar(select(func.count()).select_from(model)) or 0) + 1


class FailureSimulator:
    """Injects realistic failure states into the database for each scenario."""

    # ------------------------------------------------------------------ #
    # TECHNICAL FAILURES
    # ------------------------------------------------------------------ #

    @staticmethod
    def inject_inventory_api_timeout(db: Session) -> dict:
        """Simulates: Inventory API times out after payment — order stuck at PAYMENT_CAPTURED."""
        variant = db.scalars(
            select(ProductVariant)
            .where(ProductVariant.sku == "BG-KRT-BLK-M")
            .options(selectinload(ProductVariant.product))
        ).first()
        if not variant:
            raise ValueError("Seed data missing. Run seed_clothing_data.py")

        order_id = str(uuid.uuid4())
        order_number = f"ORD-TECH-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(variant.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Kavya Reddy", customer_email="kavya@example.com",
                      total_amount=unit_price, status="PAYMENT_CAPTURED",
                      created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=variant.id, product_title=variant.product.title,
                         ordered_size=variant.size, ordered_color=variant.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        db.add(Payment(id=str(uuid.uuid4()), order_id=order_id,
                       payment_gateway="Razorpay Mock",
                       transaction_reference=f"tx_rzp_{uuid.uuid4().hex[:10]}",
                       amount=unit_price, currency="INR", status="CAPTURED",
                       idempotency_key=f"idem_{order_number}_{uuid.uuid4().hex[:6]}",
                       captured_at=_utc()))

        wf = WorkflowExecution(id=str(uuid.uuid4()), workflow_name="OrderFulfillmentSaga",
                               correlation_id=order_number, order_id=order_id,
                               current_step="INVENTORY_API_TIMEOUT",
                               status="STALLED_INCONSISTENT",
                               context_payload={"failure": "INVENTORY_API_TIMEOUT"},
                               started_at=_utc())
        db.add(wf)
        db.commit()

        for name, step, status, payload, error in [
            ("ORDER_PLACED", 1, "SUCCESS", {"order": order_number}, None),
            ("PAYMENT_CAPTURED", 2, "SUCCESS", {"amount": unit_price}, None),
            ("INVENTORY_API_TIMEOUT", 3, "FAILED", {}, "ReadTimeoutError: inventory-service did not respond within 5000ms"),
        ]:
            db.add(WorkflowEvent(id=str(uuid.uuid4()), workflow_execution_id=wf.id,
                                 event_name=name, step_number=step, status=status,
                                 event_payload=payload, error_message=error, created_at=_utc()))
        db.commit()
        return {"scenario": "INVENTORY_API_TIMEOUT", "order_number": order_number, "order_id": order_id,
                "description": "Payment captured but inventory reservation timed out. Order stuck at PAYMENT_CAPTURED.",
                "order_status": "PAYMENT_CAPTURED", "inventory_reserved": False}

    @staticmethod
    def inject_payment_sync_failure(db: Session) -> dict:
        """Simulates: Payment gateway returns 200 but webhook delivery fails — payment shows INITIATED."""
        variant = db.scalars(
            select(ProductVariant).where(ProductVariant.sku == "BG-DRS-SGE-S")
            .options(selectinload(ProductVariant.product))
        ).first()
        if not variant:
            variant = db.scalars(select(ProductVariant).options(selectinload(ProductVariant.product))).first()

        order_id = str(uuid.uuid4())
        order_number = f"ORD-PSYNC-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(variant.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Meera Nair", customer_email="meera@example.com",
                      total_amount=unit_price, status="PENDING", created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=variant.id, product_title=variant.product.title,
                         ordered_size=variant.size, ordered_color=variant.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        # Payment stays INITIATED (webhook never arrived)
        db.add(Payment(id=str(uuid.uuid4()), order_id=order_id,
                       payment_gateway="Stripe Mock",
                       transaction_reference=f"pi_{uuid.uuid4().hex[:20]}",
                       amount=unit_price, currency="INR", status="INITIATED",  # Bug: should be CAPTURED
                       idempotency_key=f"idem_{order_number}_{uuid.uuid4().hex[:6]}"))

        wf = WorkflowExecution(id=str(uuid.uuid4()), workflow_name="OrderFulfillmentSaga",
                               correlation_id=order_number, order_id=order_id,
                               current_step="PAYMENT_WEBHOOK_MISSED",
                               status="STALLED_INCONSISTENT",
                               context_payload={"failure": "PAYMENT_SYNC_FAILURE"},
                               started_at=_utc())
        db.add(wf)
        db.commit()
        db.add(WorkflowEvent(id=str(uuid.uuid4()), workflow_execution_id=wf.id,
                             event_name="PAYMENT_WEBHOOK_FAILED", step_number=2, status="FAILED",
                             event_payload={}, error_message="Stripe webhook delivery failed (HTTP 503 from BizGuard endpoint)",
                             created_at=_utc()))
        db.commit()
        return {"scenario": "PAYMENT_SYNC_FAILURE", "order_number": order_number,
                "description": "Stripe payment succeeded but webhook was never delivered. Order sits at PENDING with INITIATED payment.",
                "order_status": "PENDING", "payment_status": "INITIATED"}

    @staticmethod
    def inject_invoice_generation_failure(db: Session) -> dict:
        """Simulates: Invoice service crashes after inventory is allocated — no invoice generated."""
        variant = db.scalars(
            select(ProductVariant).where(ProductVariant.sku == "BG-KRT-BLK-L")
            .options(selectinload(ProductVariant.product), selectinload(ProductVariant.inventory))
        ).first()

        order_id = str(uuid.uuid4())
        order_number = f"ORD-INV-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(variant.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Deepa Pillai", customer_email="deepa@example.com",
                      total_amount=unit_price, status="INVENTORY_ALLOCATED",
                      created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=variant.id, product_title=variant.product.title,
                         ordered_size=variant.size, ordered_color=variant.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        db.add(Payment(id=str(uuid.uuid4()), order_id=order_id,
                       payment_gateway="Razorpay Mock",
                       transaction_reference=f"tx_rzp_{uuid.uuid4().hex[:10]}",
                       amount=unit_price, currency="INR", status="CAPTURED",
                       idempotency_key=f"idem_{order_number}_{uuid.uuid4().hex[:6]}",
                       captured_at=_utc()))
        # Reserve inventory
        if variant.inventory:
            variant.inventory.quantity_reserved += 1
            variant.inventory.version += 1

        wf = WorkflowExecution(id=str(uuid.uuid4()), workflow_name="OrderFulfillmentSaga",
                               correlation_id=order_number, order_id=order_id,
                               current_step="INVOICE_SERVICE_CRASHED",
                               status="STALLED_INCONSISTENT",
                               context_payload={"failure": "INVOICE_GENERATION_FAILURE"},
                               started_at=_utc())
        db.add(wf)
        db.commit()
        for name, step, status, payload, error in [
            ("ORDER_PLACED", 1, "SUCCESS", {}, None),
            ("PAYMENT_CAPTURED", 2, "SUCCESS", {}, None),
            ("INVENTORY_ALLOCATED", 3, "SUCCESS", {}, None),
            ("INVOICE_SERVICE_CRASHED", 4, "FAILED", {}, "java.lang.OutOfMemoryError: invoice-service heap exhausted"),
        ]:
            db.add(WorkflowEvent(id=str(uuid.uuid4()), workflow_execution_id=wf.id,
                                 event_name=name, step_number=step, status=status,
                                 event_payload=payload, error_message=error, created_at=_utc()))
        db.commit()
        return {"scenario": "INVOICE_GENERATION_FAILURE", "order_number": order_number,
                "description": "Invoice service OOM-killed. Order is INVENTORY_ALLOCATED with no invoice record.",
                "order_status": "INVENTORY_ALLOCATED", "invoice_generated": False}

    # ------------------------------------------------------------------ #
    # BUSINESS LOGIC FAILURES
    # ------------------------------------------------------------------ #

    @staticmethod
    def inject_wrong_color_inventory(db: Session) -> dict:
        """Reserves stock on wrong color (e.g. White Kurti instead of Black Kurti)."""
        blk = db.scalars(select(ProductVariant).where(ProductVariant.sku == "BG-KRT-BLK-M")
                         .options(selectinload(ProductVariant.product), selectinload(ProductVariant.inventory))).first()
        # Find another color variant of the same product
        other_color = db.scalars(
            select(ProductVariant)
            .where(ProductVariant.product_id == blk.product_id, ProductVariant.id != blk.id,
                   ProductVariant.size == "M")
            .options(selectinload(ProductVariant.inventory))
        ).first()
        if not other_color:
            other_color = db.scalars(
                select(ProductVariant)
                .where(ProductVariant.product_id == blk.product_id, ProductVariant.id != blk.id)
                .options(selectinload(ProductVariant.inventory))
            ).first()

        order_id = str(uuid.uuid4())
        order_number = f"ORD-CLRBUG-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(blk.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Pooja Iyer", customer_email="pooja@example.com",
                      total_amount=unit_price, status="STALLED_INCONSISTENT",
                      created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=blk.id, product_title=blk.product.title,
                         ordered_size=blk.size, ordered_color=blk.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        db.add(Payment(id=str(uuid.uuid4()), order_id=order_id,
                       payment_gateway="Razorpay Mock",
                       transaction_reference=f"tx_rzp_{uuid.uuid4().hex[:10]}",
                       amount=unit_price, currency="INR", status="CAPTURED",
                       idempotency_key=f"idem_{order_number}_{uuid.uuid4().hex[:6]}",
                       captured_at=_utc()))

        if other_color and other_color.inventory:
            other_color.inventory.quantity_reserved += 1
            other_color.inventory.version += 1

        wf = WorkflowExecution(id=str(uuid.uuid4()), workflow_name="OrderFulfillmentSaga",
                               correlation_id=order_number, order_id=order_id,
                               current_step="INVARIANT_BREACH_DETECTED",
                               status="STALLED_INCONSISTENT",
                               context_payload={"failure": "WRONG_COLOR_INVENTORY"}, started_at=_utc())
        db.add(wf)
        db.commit()
        db.add(WorkflowEvent(id=str(uuid.uuid4()), workflow_execution_id=wf.id,
                             event_name="INVARIANT_BREACH", step_number=99, status="INVARIANT_BREACH",
                             event_payload={"ordered_color": blk.color, "reserved_color": other_color.color if other_color else "unknown",
                                            "rule": "RULE_COLOR_INVENTORY_MISMATCH"},
                             error_message="Inventory reserved on wrong color variant", created_at=_utc()))
        db.commit()
        return {"scenario": "WRONG_COLOR_INVENTORY", "order_number": order_number,
                "ordered_color": blk.color,
                "wrongly_reserved_color": other_color.color if other_color else "unknown",
                "description": f"Order for {blk.color} but stock reserved on {other_color.color if other_color else 'different color'}."}

    @staticmethod
    def inject_negative_inventory(db: Session) -> dict:
        """Forces quantity_reserved > quantity_on_hand on a variant — negative available."""
        inv = db.scalars(
            select(Inventory)
            .join(Inventory.variant)
            .where(Inventory.quantity_on_hand > 0)
            .options(selectinload(Inventory.variant).selectinload(ProductVariant.product))
        ).first()
        if not inv:
            raise ValueError("No inventory records found")

        before = {"quantity_reserved": inv.quantity_reserved}
        # Over-reserve
        inv.quantity_reserved = inv.quantity_on_hand + 5
        inv.version += 1
        db.add(AuditLog(id=str(uuid.uuid4()), entity_name="inventories", entity_id=inv.id,
                        action_type="NEGATIVE_INVENTORY_INJECTED", actor_type="SIMULATOR",
                        actor_id="failure-sim", before_state=before,
                        after_state={"quantity_reserved": inv.quantity_reserved},
                        notes="Simulated negative inventory for demo",
                        timestamp=_utc()))
        db.commit()
        return {"scenario": "NEGATIVE_INVENTORY", "sku": inv.variant.sku,
                "quantity_on_hand": inv.quantity_on_hand, "quantity_reserved": inv.quantity_reserved,
                "quantity_available": inv.quantity_available,
                "description": f"SKU {inv.variant.sku} now has negative available stock ({inv.quantity_available}). Reserved exceeds on-hand."}

    @staticmethod
    def inject_duplicate_payment(db: Session) -> dict:
        """Creates two CAPTURED payment records for the same order."""
        # Find an existing invoiced order
        order = db.scalars(
            select(Order).where(Order.status == "INVOICED")
            .options(selectinload(Order.payments))
        ).first()
        if not order:
            raise ValueError("No INVOICED orders found. Place an order first.")

        dup_payment = Payment(
            id=str(uuid.uuid4()), order_id=order.id,
            payment_gateway="Razorpay Mock",
            transaction_reference=f"tx_dup_{uuid.uuid4().hex[:10]}",
            amount=float(order.total_amount), currency="INR", status="CAPTURED",
            idempotency_key=f"dup_idem_{uuid.uuid4().hex[:12]}",
            captured_at=_utc()
        )
        db.add(dup_payment)
        db.commit()
        return {"scenario": "DUPLICATE_PAYMENT", "order_number": order.order_number,
                "original_payments": len(order.payments), "new_total_payments": len(order.payments) + 1,
                "description": f"Order {order.order_number} now has 2 CAPTURED payments. Customer was charged twice."}

    @staticmethod
    def inject_incorrect_invoice_amount(db: Session) -> dict:
        """Sets invoice total_amount to wrong value (less than order total)."""
        invoice = db.scalars(
            select(Invoice).join(Invoice.order).where(Invoice.status == "ISSUED")
        ).first()
        if not invoice:
            raise ValueError("No ISSUED invoices found.")

        order = db.scalars(select(Order).where(Order.id == invoice.order_id)).first()
        correct_amount = float(order.total_amount)
        wrong_amount = round(correct_amount * 0.7, 2)  # 30% less

        before = {"total_amount": float(invoice.total_amount)}
        invoice.total_amount = wrong_amount
        db.add(AuditLog(id=str(uuid.uuid4()), entity_name="invoices", entity_id=invoice.id,
                        action_type="INCORRECT_AMOUNT_INJECTED", actor_type="SIMULATOR", actor_id="failure-sim",
                        before_state=before, after_state={"total_amount": wrong_amount},
                        notes="Simulated invoice amount mismatch", timestamp=_utc()))
        db.commit()
        return {"scenario": "INCORRECT_INVOICE_AMOUNT", "invoice_number": invoice.invoice_number,
                "order_total": correct_amount, "invoice_total": wrong_amount,
                "discrepancy": round(correct_amount - wrong_amount, 2),
                "description": f"Invoice {invoice.invoice_number} shows ₹{wrong_amount} but order total is ₹{correct_amount}."}

    @staticmethod
    def inject_shipped_without_payment(db: Session) -> dict:
        """Sets order to SHIPPED even though payment is not CAPTURED."""
        # Create a fresh order at PENDING with no payment
        variant = db.scalars(
            select(ProductVariant).where(ProductVariant.sku == "BG-TOP-BLS-M")
            .options(selectinload(ProductVariant.product))
        ).first()
        if not variant:
            variant = db.scalars(select(ProductVariant).options(selectinload(ProductVariant.product))).first()

        order_id = str(uuid.uuid4())
        order_number = f"ORD-SHIPBUG-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(variant.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Rashida Khan", customer_email="rashida@example.com",
                      total_amount=unit_price, status="SHIPPED",  # Bug: shipped without payment
                      created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=variant.id, product_title=variant.product.title,
                         ordered_size=variant.size, ordered_color=variant.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        # NO Payment record added — intentionally missing
        db.commit()
        return {"scenario": "SHIPPED_WITHOUT_PAYMENT", "order_number": order_number,
                "order_status": "SHIPPED", "payment_status": "NONE",
                "description": f"Order {order_number} marked SHIPPED with no payment record. Revenue not collected."}

    @staticmethod
    def inject_out_of_stock_sale(db: Session) -> dict:
        """Sets a variant's on_hand to 0 then creates an order that allocated it."""
        variant = db.scalars(
            select(ProductVariant).where(ProductVariant.sku == "BG-JNS-VNT-32")
            .options(selectinload(ProductVariant.product), selectinload(ProductVariant.inventory))
        ).first()
        if not variant:
            variant = db.scalars(
                select(ProductVariant)
                .options(selectinload(ProductVariant.product), selectinload(ProductVariant.inventory))
            ).first()

        if variant.inventory:
            variant.inventory.quantity_on_hand = 0
            variant.inventory.quantity_reserved = 0
            variant.inventory.version += 1

        order_id = str(uuid.uuid4())
        order_number = f"ORD-OOS-{uuid.uuid4().hex[:6].upper()}"
        unit_price = float(variant.product.base_price)

        order = Order(id=order_id, order_number=order_number,
                      customer_name="Fatima Sheikh", customer_email="fatima@example.com",
                      total_amount=unit_price, status="STALLED_INCONSISTENT",
                      created_at=_utc(), updated_at=_utc())
        db.add(order)
        db.add(OrderItem(id=str(uuid.uuid4()), order_id=order_id,
                         variant_id=variant.id, product_title=variant.product.title,
                         ordered_size=variant.size, ordered_color=variant.color,
                         quantity=1, unit_price=unit_price, subtotal=unit_price))
        db.commit()
        return {"scenario": "OUT_OF_STOCK_SALE", "sku": variant.sku, "order_number": order_number,
                "quantity_on_hand": 0,
                "description": f"Order {order_number} placed for {variant.sku} which has 0 stock. Product should have been blocked."}

    # ------------------------------------------------------------------ #
    # WORKFLOW FAILURES
    # ------------------------------------------------------------------ #

    @staticmethod
    def inject_refund_not_synced(db: Session) -> dict:
        """Creates an approved return but the payment stays CAPTURED (no refund record)."""
        from app.models.orders import ReturnRecord
        order = db.scalars(
            select(Order).where(Order.status.in_(["DELIVERED", "SHIPPED"]))
            .options(selectinload(Order.payments))
        ).first()
        if not order:
            raise ValueError("No DELIVERED/SHIPPED orders to create return for.")

        ret = ReturnRecord(id=str(uuid.uuid4()), order_id=order.id,
                           reason="Customer changed mind after delivery",
                           status="APPROVED", created_at=_utc())
        db.add(ret)
        # Payment intentionally stays CAPTURED — no REFUNDED update
        db.commit()
        return {"scenario": "REFUND_NOT_SYNCED", "order_number": order.order_number,
                "return_status": "APPROVED", "payment_status": order.payments[0].status if order.payments else "unknown",
                "description": f"Return approved for {order.order_number} but refund was never processed. Customer owed money."}

    # ------------------------------------------------------------------ #
    # Catalog endpoint (all scenarios)
    # ------------------------------------------------------------------ #

    SCENARIOS = {
        "inventory_api_timeout": inject_inventory_api_timeout.__func__,
        "payment_sync_failure": inject_payment_sync_failure.__func__,
        "invoice_generation_failure": inject_invoice_generation_failure.__func__,
        "wrong_color_inventory": inject_wrong_color_inventory.__func__,
        "negative_inventory": inject_negative_inventory.__func__,
        "duplicate_payment": inject_duplicate_payment.__func__,
        "incorrect_invoice_amount": inject_incorrect_invoice_amount.__func__,
        "shipped_without_payment": inject_shipped_without_payment.__func__,
        "out_of_stock_sale": inject_out_of_stock_sale.__func__,
        "refund_not_synced": inject_refund_not_synced.__func__,
        # original kurti bug (Phase 2)
        "black_kurti_size_mismatch": None,  # delegates to SimulationService
    }

    @staticmethod
    def inject_scenario(db: Session, scenario_key: str) -> dict:
        if scenario_key == "black_kurti_size_mismatch":
            from app.services.simulation_service import SimulationService
            return SimulationService.inject_black_kurti_bug(db)

        fn = FailureSimulator.SCENARIOS.get(scenario_key)
        if not fn:
            raise ValueError(f"Unknown scenario: {scenario_key}. Available: {list(FailureSimulator.SCENARIOS.keys())}")
        return fn(db)
