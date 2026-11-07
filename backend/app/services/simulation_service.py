"""
SimulationService — injects a realistic Black Kurti bug into the database
and provides a reset method that cleans up all simulation artifacts.

Bug scenario:
  A customer orders Black Kurti Size M.
  Payment is captured correctly.
  BUT inventory is reserved on Size L instead of Size M (wrong variant ID
  passed to InventoryService.reserve_stock).
  The order is then set to STALLED_INCONSISTENT and the workflow is halted.
"""

import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import ProductVariant, Inventory
from app.models.orders import Order, OrderItem, Payment, Invoice, InvoiceItem
from app.models.workflow import WorkflowExecution, WorkflowEvent
from app.models.incidents import Incident, AgentTask, AgentMessage
from app.models.recovery import RecoveryProposal, Approval
from app.services.workflow_engine import WorkflowEngine


class SimulationService:

    # ------------------------------------------------------------------ #
    #  Bug injection                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def inject_black_kurti_bug(db: Session) -> dict:
        """
        Creates a realistic order for Black Kurti Size M but reserves stock
        on Size L — simulating the classic variant-ID bug.
        """
        # 1. Find the two key variants
        var_m_stmt = select(ProductVariant).where(
            ProductVariant.sku == "BG-KRT-BLK-M"
        ).options(selectinload(ProductVariant.inventory),
                   selectinload(ProductVariant.product))
        var_l_stmt = select(ProductVariant).where(
            ProductVariant.sku == "BG-KRT-BLK-L"
        ).options(selectinload(ProductVariant.inventory))

        variant_m = db.scalars(var_m_stmt).first()
        variant_l = db.scalars(var_l_stmt).first()

        if not variant_m:
            raise ValueError("BG-KRT-BLK-M variant not found in database. Run seed first.")
        if not variant_l:
            raise ValueError("BG-KRT-BLK-L variant not found in database. Run seed first.")

        # 2. Build order metadata
        from sqlalchemy import func as sqlfunc
        order_count = db.scalar(
            select(sqlfunc.count()).select_from(Order)
        ) or 0
        order_number = f"ORD-BUG-{uuid.uuid4().hex[:6].upper()}"
        order_id = str(uuid.uuid4())

        unit_price = float(variant_m.product.base_price) + float(variant_m.price_adjustment)
        total_amount = unit_price * 1

        # 3. Create the workflow execution FIRST (before the order, so order_id can link)
        wf_id = str(uuid.uuid4())
        wf_exec = WorkflowExecution(
            id=wf_id,
            workflow_name="OrderFulfillmentSaga",
            correlation_id=order_number,
            order_id=order_id,
            current_step="INVARIANT_BREACH_DETECTED",
            status="STALLED_INCONSISTENT",
            context_payload={
                "customer": "Priya Kapoor",
                "email": "priya.kapoor@test.com",
                "bug": "inventory reserved on wrong variant (Size L instead of Size M)",
            },
            started_at=datetime.now(timezone.utc),
        )
        db.add(wf_exec)
        db.flush()

        # 4. Create Order
        order = Order(
            id=order_id,
            order_number=order_number,
            customer_name="Priya Kapoor",
            customer_email="priya.kapoor@test.com",
            customer_phone="+91-9123456789",
            shipping_address={"city": "Mumbai", "state": "Maharashtra", "country": "India"},
            total_amount=total_amount,
            status="STALLED_INCONSISTENT",
            created_at=datetime.now(timezone.utc),
        )
        db.add(order)
        db.flush()

        # 5. Order item referencing Size M (what customer ordered)
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order_id,
            variant_id=variant_m.id,          # ← CORRECT variant in the item
            product_title=variant_m.product.title,
            ordered_size=variant_m.size,       # M
            ordered_color=variant_m.color,
            quantity=1,
            unit_price=unit_price,
            subtotal=total_amount,
        )
        db.add(order_item)
        db.flush()

        # 6. Payment captured normally
        tx_ref = f"tx_rzp_{uuid.uuid4().hex[:10]}"
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order_id,
            payment_gateway="Razorpay Mock",
            transaction_reference=tx_ref,
            amount=total_amount,
            currency="USD",
            status="CAPTURED",
            idempotency_key=f"idem_{order_number}_{uuid.uuid4().hex[:6]}",
            captured_at=datetime.now(timezone.utc),
        )
        db.add(payment)
        db.flush()

        # 7. BUG: Reserve stock on Size L instead of Size M
        inv_l = variant_l.inventory
        if inv_l:
            inv_l.quantity_reserved += 1
            inv_l.version += 1

        # Size M inventory is intentionally NOT touched — 0 reserved even though order says M
        db.flush()

        # 8. Log workflow events
        events = [
            WorkflowEvent(
                id=str(uuid.uuid4()),
                workflow_execution_id=wf_id,
                event_name="ORDER_PLACED",
                step_number=1,
                status="SUCCESS",
                event_payload={"order_number": order_number, "total_amount": total_amount},
                created_at=datetime.now(timezone.utc),
            ),
            WorkflowEvent(
                id=str(uuid.uuid4()),
                workflow_execution_id=wf_id,
                event_name="PAYMENT_CAPTURED",
                step_number=2,
                status="SUCCESS",
                event_payload={"transaction_reference": tx_ref, "amount": total_amount},
                created_at=datetime.now(timezone.utc),
            ),
            WorkflowEvent(
                id=str(uuid.uuid4()),
                workflow_execution_id=wf_id,
                event_name="INVENTORY_RESERVED_WRONG_VARIANT",
                step_number=3,
                status="FAILED",
                event_payload={
                    "intended_variant": "BG-KRT-BLK-M",
                    "actual_variant_reserved": "BG-KRT-BLK-L",
                },
                error_message="Bug: variant_id resolved to Size L instead of Size M",
                created_at=datetime.now(timezone.utc),
            ),
            WorkflowEvent(
                id=str(uuid.uuid4()),
                workflow_execution_id=wf_id,
                event_name="INVARIANT_BREACH",
                step_number=99,
                status="INVARIANT_BREACH",
                event_payload={
                    "rule": "RULE_VARIANT_INVENTORY_MISMATCH",
                    "affected_order": order_number,
                },
                error_message="Invariant check failed: Size M has 0 reservations; Size L has unexpected reservation.",
                created_at=datetime.now(timezone.utc),
            ),
        ]
        for ev in events:
            db.add(ev)

        db.commit()

        return {
            "status": "BUG_INJECTED",
            "order_number": order_number,
            "order_id": order_id,
            "workflow_execution_id": wf_id,
            "bug_description": (
                "Order placed for Black Kurti Size M. Payment captured correctly. "
                "However, inventory reservation was incorrectly applied to Size L "
                "(BG-KRT-BLK-L) instead of Size M (BG-KRT-BLK-M). "
                "Order is now STALLED_INCONSISTENT."
            ),
            "affected_variants": {
                "ordered_variant": {
                    "sku": variant_m.sku,
                    "size": variant_m.size,
                    "reserved_after_bug": 0,
                },
                "wrongly_reserved_variant": {
                    "sku": variant_l.sku,
                    "size": variant_l.size,
                    "reserved_after_bug": inv_l.quantity_reserved if inv_l else "unknown",
                },
            },
            "customer": "Priya Kapoor",
            "total_amount": total_amount,
        }

    # ------------------------------------------------------------------ #
    #  Reset                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def reset_simulation(db: Session) -> dict:
        """
        Removes all simulation artifacts:
          - All Incidents, AgentTasks, AgentMessages, RecoveryProposals, Approvals
          - All STALLED_INCONSISTENT orders and their related rows
          - Resets all inventory reserved quantities to 0
        """
        # 1. Delete dependent rows first (FK order matters for SQLite)
        db.execute(delete(Approval))
        db.execute(delete(RecoveryProposal))
        db.execute(delete(AgentMessage))
        db.execute(delete(AgentTask))
        db.execute(delete(Incident))
        db.flush()

        # 2. Find stalled orders
        stalled_orders = list(
            db.scalars(select(Order).where(Order.status == "STALLED_INCONSISTENT")).all()
        )
        stalled_order_ids = [o.id for o in stalled_orders]

        if stalled_order_ids:
            # Delete workflow events → executions
            wf_execs = list(
                db.scalars(
                    select(WorkflowExecution).where(WorkflowExecution.order_id.in_(stalled_order_ids))
                ).all()
            )
            wf_exec_ids = [w.id for w in wf_execs]
            if wf_exec_ids:
                db.execute(delete(WorkflowEvent).where(WorkflowEvent.workflow_execution_id.in_(wf_exec_ids)))
                db.execute(delete(WorkflowExecution).where(WorkflowExecution.id.in_(wf_exec_ids)))
            db.flush()

            # Delete order items, payments, invoices (cascade would handle items/invoice_items but be explicit)
            from app.models.orders import Payment, InvoiceItem, Invoice
            payments = list(db.scalars(select(Payment).where(Payment.order_id.in_(stalled_order_ids))).all())
            invoices = list(db.scalars(select(Invoice).where(Invoice.order_id.in_(stalled_order_ids))).all())
            invoice_ids = [inv.id for inv in invoices]
            if invoice_ids:
                db.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id.in_(invoice_ids)))
                db.execute(delete(Invoice).where(Invoice.id.in_(invoice_ids)))
            db.execute(delete(Payment).where(Payment.order_id.in_(stalled_order_ids)))
            db.execute(delete(OrderItem).where(OrderItem.order_id.in_(stalled_order_ids)))
            db.execute(delete(Order).where(Order.id.in_(stalled_order_ids)))
            db.flush()

        # 3. Reset ALL inventory reservations to 0
        all_inventories = list(db.scalars(select(Inventory)).all())
        for inv in all_inventories:
            inv.quantity_reserved = 0
            inv.version += 1

        db.commit()

        return {
            "status": "RESET_COMPLETE",
            "stalled_orders_removed": len(stalled_order_ids),
            "incidents_cleared": True,
            "inventory_reservations_reset": len(all_inventories),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_status(db: Session) -> dict:
        """Returns current simulation state: count of active incidents, stalled orders, etc."""
        from sqlalchemy import func as sqlfunc
        stalled_orders = db.scalar(
            select(sqlfunc.count()).select_from(Order).where(Order.status == "STALLED_INCONSISTENT")
        ) or 0
        active_incidents = db.scalar(
            select(sqlfunc.count()).select_from(Incident).where(Incident.status.notin_(["VERIFIED_RESOLVED", "CLOSED"]))
        ) or 0
        total_proposals = db.scalar(select(sqlfunc.count()).select_from(RecoveryProposal)) or 0

        return {
            "bug_injected": stalled_orders > 0 or active_incidents > 0,
            "stalled_orders": stalled_orders,
            "active_incidents": active_incidents,
            "proposals_count": total_proposals,
            "simulation_ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

