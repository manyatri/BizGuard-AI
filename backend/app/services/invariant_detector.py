"""
InvariantDetector — full rule engine for clothing e-commerce business invariants.

Rules implemented:
  RULE_VARIANT_INVENTORY_MISMATCH   — ordered variant has 0 reservations, sibling has unexpected ones
  RULE_COLOR_INVENTORY_MISMATCH     — inventory reserved on wrong color variant
  RULE_NEGATIVE_INVENTORY           — quantity_reserved > quantity_on_hand
  RULE_SHIPPED_WITHOUT_PAYMENT      — SHIPPED order with no CAPTURED payment
  RULE_DUPLICATE_PAYMENT            — order has 2+ CAPTURED payments
  RULE_INVOICE_AMOUNT_MISMATCH      — invoice total != order total (> 1% tolerance)
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import ProductVariant, Inventory
from app.models.orders import Order, OrderItem, Payment, Invoice
from app.models.incidents import Incident
from app.models.workflow import WorkflowExecution, WorkflowEvent
from app.services.workflow_engine import WorkflowEngine


def _utc() -> datetime:
    return datetime.now(timezone.utc)


class InvariantDetector:
    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def run_full_scan(db: Session) -> List[Incident]:
        """
        Run all invariant rules and return newly created Incident records.
        Each rule method is responsible for deduplication (skip if incident
        already exists for the same order/entity).
        """
        new_incidents: List[Incident] = []

        # Rule 1 & 2 — variant/color inventory mismatches (order-level)
        new_incidents.extend(InvariantDetector._scan_order_variant_mismatches(db))

        # Rule 3 — negative inventory (inventory-level)
        new_incidents.extend(InvariantDetector._scan_negative_inventory(db))

        # Rule 4 — shipped without payment (order-level)
        new_incidents.extend(InvariantDetector._scan_shipped_without_payment(db))

        # Rule 5 — duplicate payments (order-level)
        new_incidents.extend(InvariantDetector._scan_duplicate_payments(db))

        # Rule 6 — invoice amount mismatch (invoice-level)
        new_incidents.extend(InvariantDetector._scan_invoice_amount_mismatch(db))

        return new_incidents

    @staticmethod
    def get_all_incidents(db: Session) -> List[Incident]:
        """Return all Incident rows with related data."""
        stmt = (
            select(Incident)
            .options(
                selectinload(Incident.order),
                selectinload(Incident.workflow_execution),
                selectinload(Incident.tasks),
                selectinload(Incident.messages),
                selectinload(Incident.recovery_proposals),
            )
            .order_by(Incident.detected_at.desc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: str) -> Optional[Incident]:
        """Return a single Incident by its UUID primary key."""
        stmt = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(
                selectinload(Incident.order),
                selectinload(Incident.workflow_execution)
                    .selectinload(WorkflowExecution.events),
                selectinload(Incident.tasks),
                selectinload(Incident.messages),
                selectinload(Incident.recovery_proposals),
            )
        )
        return db.scalars(stmt).first()

    # ------------------------------------------------------------------ #
    #  Rule 1 + 2 — Variant / Color Inventory Mismatch                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _scan_order_variant_mismatches(db: Session) -> List[Incident]:
        """
        RULE_VARIANT_INVENTORY_MISMATCH / RULE_COLOR_INVENTORY_MISMATCH
        For each STALLED or INVENTORY_ALLOCATED order, check whether the
        reservation landed on the wrong sibling variant.
        """
        target_statuses = ["STALLED_INCONSISTENT", "INVENTORY_ALLOCATED"]
        stmt = (
            select(Order)
            .where(Order.status.in_(target_statuses))
            .options(
                selectinload(Order.items).selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.inventory),
                selectinload(Order.items).selectinload(OrderItem.variant)
                    .selectinload(ProductVariant.product),
                selectinload(Order.workflow_executions),
            )
        )
        orders = list(db.scalars(stmt).all())
        incidents: List[Incident] = []
        for order in orders:
            inc = InvariantDetector._check_order_variant_mismatch(db, order)
            if inc:
                incidents.append(inc)
        return incidents

    @staticmethod
    def _check_order_variant_mismatch(db: Session, order: Order) -> Optional[Incident]:
        for item in order.items:
            variant = item.variant
            if not variant or not variant.inventory:
                continue

            ordered_inv: Inventory = variant.inventory
            ordered_reserved = ordered_inv.quantity_reserved

            # Load all sibling variants (same product_id, different variant)
            sibling_stmt = (
                select(ProductVariant)
                .where(
                    ProductVariant.product_id == variant.product_id,
                    ProductVariant.id != variant.id,
                )
                .options(selectinload(ProductVariant.inventory))
            )
            siblings = list(db.scalars(sibling_stmt).all())

            sibling_has_unexpected = any(
                sib.inventory and sib.inventory.quantity_reserved > 0
                for sib in siblings
            )

            if ordered_reserved == 0 and sibling_has_unexpected:
                # Dedup check
                existing = db.scalars(
                    select(Incident).where(Incident.affected_order_id == order.id)
                ).first()
                if existing:
                    return None

                bad_sibling = next(
                    (s for s in siblings if s.inventory and s.inventory.quantity_reserved > 0),
                    None,
                )

                # Determine rule — size vs color mismatch
                if bad_sibling and bad_sibling.size != variant.size:
                    rule = "RULE_VARIANT_INVENTORY_MISMATCH"
                    title = (
                        f"Size Inventory Mismatch — Order {order.order_number}: "
                        f"Reserved on {bad_sibling.sku} instead of {variant.sku}"
                    )
                    root_cause = (
                        f"Order {order.order_number} requested {variant.sku} "
                        f"(Size {variant.size}) but inventory reserved on sibling "
                        f"{bad_sibling.sku} (Size {bad_sibling.size}). "
                        "Wrong variant_id passed to inventory reservation call."
                    )
                elif bad_sibling and bad_sibling.color != variant.color:
                    rule = "RULE_COLOR_INVENTORY_MISMATCH"
                    title = (
                        f"Color Inventory Mismatch — Order {order.order_number}: "
                        f"Reserved {bad_sibling.color} instead of {variant.color}"
                    )
                    root_cause = (
                        f"Order {order.order_number} requested {variant.color} variant "
                        f"({variant.sku}) but inventory reserved on "
                        f"{bad_sibling.color} variant ({bad_sibling.sku}). "
                        "Color lookup bug in variant selection logic."
                    )
                else:
                    rule = "RULE_VARIANT_INVENTORY_MISMATCH"
                    title = (
                        f"Variant Inventory Mismatch — Order {order.order_number}: "
                        f"Reserved on {bad_sibling.sku if bad_sibling else 'unknown'} "
                        f"instead of {variant.sku}"
                    )
                    root_cause = (
                        f"Inventory reserved on wrong sibling variant for order {order.order_number}."
                    )

                total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0
                seq = total_incidents + 1
                incident_code = f"INC-2026-{seq:04d}"

                wf_exec: Optional[WorkflowExecution] = None
                if order.workflow_executions:
                    wf_exec = order.workflow_executions[0]

                incident = Incident(
                    id=str(uuid.uuid4()),
                    incident_code=incident_code,
                    title=title,
                    severity="CRITICAL",
                    status="DETECTED",
                    detection_rule=rule,
                    affected_order_id=order.id,
                    workflow_execution_id=wf_exec.id if wf_exec else None,
                    root_cause_summary=root_cause,
                    blast_radius_analysis={
                        "ordered_variant_sku": variant.sku,
                        "ordered_variant_reserved": ordered_reserved,
                        "bad_sibling_sku": bad_sibling.sku if bad_sibling else None,
                        "bad_sibling_reserved": (
                            bad_sibling.inventory.quantity_reserved
                            if bad_sibling and bad_sibling.inventory
                            else None
                        ),
                        "order_status": order.status,
                        "order_number": order.order_number,
                    },
                    detected_at=_utc(),
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)

                if wf_exec:
                    WorkflowEngine.log_event(
                        db=db, execution_id=wf_exec.id,
                        event_name="INVARIANT_BREACH", step_number=99,
                        status="INVARIANT_BREACH",
                        payload={"incident_code": incident_code, "rule": rule,
                                 "affected_order": order.order_number},
                        error_message=f"Inventory reserved on wrong variant. "
                                      f"Expected: {variant.sku}, Got: {bad_sibling.sku if bad_sibling else 'unknown'}",
                    )
                return incident

        return None

    # ------------------------------------------------------------------ #
    #  Rule 3 — Negative Inventory                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _scan_negative_inventory(db: Session) -> List[Incident]:
        """
        RULE_NEGATIVE_INVENTORY
        Flag any Inventory record where quantity_reserved > quantity_on_hand.
        """
        stmt = (
            select(Inventory)
            .where(Inventory.quantity_reserved > Inventory.quantity_on_hand)
            .options(
                selectinload(Inventory.variant).selectinload(ProductVariant.product)
            )
        )
        bad_inventories = list(db.scalars(stmt).all())
        incidents: List[Incident] = []

        for inv in bad_inventories:
            # Dedup: check if incident exists for this inventory id
            existing = db.scalars(
                select(Incident)
                .where(
                    Incident.detection_rule == "RULE_NEGATIVE_INVENTORY",
                    Incident.blast_radius_analysis["inventory_id"].as_string() == inv.id,
                )
            ).first()
            # Simpler dedup: check by title prefix containing SKU
            existing2 = db.scalars(
                select(Incident)
                .where(
                    Incident.detection_rule == "RULE_NEGATIVE_INVENTORY",
                    Incident.title.contains(inv.variant.sku if inv.variant else inv.id),
                )
            ).first()
            if existing or existing2:
                continue

            total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0
            seq = total_incidents + 1
            incident_code = f"INC-2026-{seq:04d}"
            sku = inv.variant.sku if inv.variant else inv.id
            avail = inv.quantity_on_hand - inv.quantity_reserved

            incident = Incident(
                id=str(uuid.uuid4()),
                incident_code=incident_code,
                title=f"Negative Inventory — SKU {sku}: available={avail} (on_hand={inv.quantity_on_hand}, reserved={inv.quantity_reserved})",
                severity="CRITICAL",
                status="DETECTED",
                detection_rule="RULE_NEGATIVE_INVENTORY",
                root_cause_summary=(
                    f"SKU {sku} has quantity_reserved ({inv.quantity_reserved}) "
                    f"exceeding quantity_on_hand ({inv.quantity_on_hand}). "
                    f"Available stock is {avail}. This indicates over-reservation or "
                    "a missing stock replenishment. Customer orders may be unfulfillable."
                ),
                blast_radius_analysis={
                    "inventory_id": inv.id,
                    "sku": sku,
                    "quantity_on_hand": inv.quantity_on_hand,
                    "quantity_reserved": inv.quantity_reserved,
                    "quantity_available": avail,
                },
                detected_at=_utc(),
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            incidents.append(incident)

        return incidents

    # ------------------------------------------------------------------ #
    #  Rule 4 — Shipped Without Payment                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _scan_shipped_without_payment(db: Session) -> List[Incident]:
        """
        RULE_SHIPPED_WITHOUT_PAYMENT
        Orders in SHIPPED/DELIVERED status that have no CAPTURED payment.
        """
        stmt = (
            select(Order)
            .where(Order.status.in_(["SHIPPED", "DELIVERED"]))
            .options(selectinload(Order.payments))
        )
        orders = list(db.scalars(stmt).all())
        incidents: List[Incident] = []

        for order in orders:
            captured = [p for p in order.payments if p.status == "CAPTURED"]
            if captured:
                continue  # Healthy — has payment

            # Dedup
            existing = db.scalars(
                select(Incident)
                .where(
                    Incident.affected_order_id == order.id,
                    Incident.detection_rule == "RULE_SHIPPED_WITHOUT_PAYMENT",
                )
            ).first()
            if existing:
                continue

            total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0
            seq = total_incidents + 1
            incident_code = f"INC-2026-{seq:04d}"

            incident = Incident(
                id=str(uuid.uuid4()),
                incident_code=incident_code,
                title=f"Shipped Without Payment — Order {order.order_number} is {order.status} with no captured payment",
                severity="CRITICAL",
                status="DETECTED",
                detection_rule="RULE_SHIPPED_WITHOUT_PAYMENT",
                affected_order_id=order.id,
                root_cause_summary=(
                    f"Order {order.order_number} reached status '{order.status}' "
                    f"but has {len(order.payments)} payment record(s), none CAPTURED. "
                    "The fulfillment workflow bypassed payment verification. "
                    "Revenue has not been collected for this shipment."
                ),
                blast_radius_analysis={
                    "order_number": order.order_number,
                    "order_status": order.status,
                    "order_total": float(order.total_amount),
                    "payment_count": len(order.payments),
                    "payment_statuses": [p.status for p in order.payments],
                },
                detected_at=_utc(),
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            incidents.append(incident)

        return incidents

    # ------------------------------------------------------------------ #
    #  Rule 5 — Duplicate Payment                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _scan_duplicate_payments(db: Session) -> List[Incident]:
        """
        RULE_DUPLICATE_PAYMENT
        Orders that have more than one CAPTURED payment record.
        """
        stmt = (
            select(Order)
            .options(selectinload(Order.payments))
        )
        orders = list(db.scalars(stmt).all())
        incidents: List[Incident] = []

        for order in orders:
            captured = [p for p in order.payments if p.status == "CAPTURED"]
            if len(captured) < 2:
                continue

            # Dedup
            existing = db.scalars(
                select(Incident)
                .where(
                    Incident.affected_order_id == order.id,
                    Incident.detection_rule == "RULE_DUPLICATE_PAYMENT",
                )
            ).first()
            if existing:
                continue

            total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0
            seq = total_incidents + 1
            incident_code = f"INC-2026-{seq:04d}"
            total_charged = sum(float(p.amount) for p in captured)

            incident = Incident(
                id=str(uuid.uuid4()),
                incident_code=incident_code,
                title=f"Duplicate Payment — Order {order.order_number}: {len(captured)} CAPTURED payments totalling ₹{total_charged:.2f}",
                severity="CRITICAL",
                status="DETECTED",
                detection_rule="RULE_DUPLICATE_PAYMENT",
                affected_order_id=order.id,
                root_cause_summary=(
                    f"Order {order.order_number} (total ₹{float(order.total_amount):.2f}) "
                    f"has {len(captured)} CAPTURED payment records. "
                    f"Customer was charged ₹{total_charged:.2f} in total — "
                    f"₹{total_charged - float(order.total_amount):.2f} overcharged. "
                    "Idempotency check failed in the payment processing layer."
                ),
                blast_radius_analysis={
                    "order_number": order.order_number,
                    "order_total": float(order.total_amount),
                    "captured_payment_count": len(captured),
                    "total_charged": total_charged,
                    "overcharge": round(total_charged - float(order.total_amount), 2),
                    "payment_refs": [p.transaction_reference for p in captured],
                },
                detected_at=_utc(),
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            incidents.append(incident)

        return incidents

    # ------------------------------------------------------------------ #
    #  Rule 6 — Invoice Amount Mismatch                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _scan_invoice_amount_mismatch(db: Session) -> List[Incident]:
        """
        RULE_INVOICE_AMOUNT_MISMATCH
        Invoice total_amount differs from order total_amount by more than 1%.
        """
        stmt = (
            select(Invoice)
            .where(Invoice.status.in_(["ISSUED", "DRAFT"]))
            .options(selectinload(Invoice.order))
        )
        invoices = list(db.scalars(stmt).all())
        incidents: List[Incident] = []

        for inv in invoices:
            if not inv.order:
                continue
            order_total = float(inv.order.total_amount)
            inv_total = float(inv.total_amount)
            if order_total == 0:
                continue
            diff_pct = abs(order_total - inv_total) / order_total
            if diff_pct <= 0.01:  # within 1% tolerance
                continue

            # Dedup
            existing = db.scalars(
                select(Incident)
                .where(
                    Incident.affected_order_id == inv.order_id,
                    Incident.detection_rule == "RULE_INVOICE_AMOUNT_MISMATCH",
                )
            ).first()
            if existing:
                continue

            total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0
            seq = total_incidents + 1
            incident_code = f"INC-2026-{seq:04d}"
            discrepancy = round(order_total - inv_total, 2)

            incident = Incident(
                id=str(uuid.uuid4()),
                incident_code=incident_code,
                title=f"Invoice Amount Mismatch — {inv.invoice_number}: ₹{inv_total} vs order ₹{order_total} (gap ₹{discrepancy})",
                severity="HIGH",
                status="DETECTED",
                detection_rule="RULE_INVOICE_AMOUNT_MISMATCH",
                affected_order_id=inv.order_id,
                root_cause_summary=(
                    f"Invoice {inv.invoice_number} shows ₹{inv_total:.2f} "
                    f"but order {inv.order.order_number} total is ₹{order_total:.2f}. "
                    f"Discrepancy of ₹{discrepancy:.2f} ({diff_pct*100:.1f}%). "
                    "Tax calculation error or discount application bug in invoice service."
                ),
                blast_radius_analysis={
                    "invoice_number": inv.invoice_number,
                    "invoice_total": inv_total,
                    "order_total": order_total,
                    "discrepancy": discrepancy,
                    "discrepancy_pct": round(diff_pct * 100, 2),
                    "order_number": inv.order.order_number if inv.order else None,
                },
                detected_at=_utc(),
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            incidents.append(incident)

        return incidents
