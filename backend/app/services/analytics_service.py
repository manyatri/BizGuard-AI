"""
AnalyticsService — live metrics from the BizGuard database.
All queries use synchronous SQLAlchemy.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.models.catalog import Product, ProductVariant, Inventory
from app.models.orders import Order, Payment
from app.models.incidents import Incident
from app.models.recovery import RecoveryProposal
from app.models.workflow import WorkflowExecution


class AnalyticsService:

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        """Return live statistics from the database."""

        # Total active products
        total_products = db.scalar(
            select(func.count()).select_from(Product).where(Product.is_active == True)
        ) or 0

        # Total orders
        total_orders = db.scalar(select(func.count()).select_from(Order)) or 0

        # Orders by status
        status_rows = db.execute(
            select(Order.status, func.count(Order.id).label("cnt"))
            .group_by(Order.status)
        ).all()
        orders_by_status = {row.status: row.cnt for row in status_rows}

        # Total revenue (sum of CAPTURED payments)
        total_revenue = float(
            db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0.0))
                .where(Payment.status == "CAPTURED")
            ) or 0.0
        )

        # Incidents
        active_incidents = db.scalar(
            select(func.count()).select_from(Incident)
            .where(Incident.status.notin_(["CLOSED", "VERIFIED_RESOLVED"]))
        ) or 0

        resolved_incidents = db.scalar(
            select(func.count()).select_from(Incident)
            .where(Incident.status.in_(["CLOSED", "VERIFIED_RESOLVED"]))
        ) or 0

        # Avg order value
        avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

        # Low-stock variants
        low_stock_variants = db.scalar(
            select(func.count()).select_from(Inventory)
            .join(Inventory.variant)
            .where(
                (Inventory.quantity_on_hand - Inventory.quantity_reserved) <= Inventory.reorder_threshold,
                (Inventory.quantity_on_hand - Inventory.quantity_reserved) > 0,
            )
        ) or 0

        # Out of stock
        out_of_stock_variants = db.scalar(
            select(func.count()).select_from(Inventory)
            .where(
                (Inventory.quantity_on_hand - Inventory.quantity_reserved) <= 0
            )
        ) or 0

        # Pending approvals
        pending_approvals = db.scalar(
            select(func.count()).select_from(RecoveryProposal)
            .where(RecoveryProposal.status.in_(["READY_FOR_REVIEW", "APPROVED"]),
                   RecoveryProposal.executed_at.is_(None))
        ) or 0

        # MTTD (mean time to detect) in minutes
        # = avg(incident.detected_at - order.created_at) for resolved incidents
        resolved_with_order = db.execute(
            select(Incident.detected_at, Order.created_at)
            .join(Order, Order.id == Incident.affected_order_id)
            .where(Incident.status.in_(["VERIFIED_RESOLVED", "CLOSED"]),
                   Incident.affected_order_id.isnot(None))
        ).all()

        mttd_minutes: Optional[float] = None
        if resolved_with_order:
            diffs = []
            for row in resolved_with_order:
                if row.detected_at and row.created_at:
                    d = (row.detected_at - row.created_at).total_seconds() / 60.0
                    diffs.append(d)
            if diffs:
                mttd_minutes = round(sum(diffs) / len(diffs), 2)

        # MTTR (mean time to resolve) in minutes
        # = avg(incident.resolved_at - incident.detected_at) for resolved incidents
        resolved_incidents_rows = db.execute(
            select(Incident.detected_at, Incident.resolved_at)
            .where(Incident.status.in_(["VERIFIED_RESOLVED", "CLOSED"]),
                   Incident.resolved_at.isnot(None))
        ).all()

        mttr_minutes: Optional[float] = None
        if resolved_incidents_rows:
            diffs = []
            for row in resolved_incidents_rows:
                if row.detected_at and row.resolved_at:
                    d = (row.resolved_at - row.detected_at).total_seconds() / 60.0
                    diffs.append(d)
            if diffs:
                mttr_minutes = round(sum(diffs) / len(diffs), 2)

        # Workflow success rate
        total_wf = db.scalar(select(func.count()).select_from(WorkflowExecution)) or 0
        completed_wf = db.scalar(
            select(func.count()).select_from(WorkflowExecution)
            .where(WorkflowExecution.status == "COMPLETED")
        ) or 0
        workflow_success_rate = (
            round((completed_wf / total_wf) * 100, 1) if total_wf > 0 else 0.0
        )

        return {
            "total_products": total_products,
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "total_revenue": total_revenue,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "avg_order_value": avg_order_value,
            "low_stock_variants": low_stock_variants,
            "out_of_stock_variants": out_of_stock_variants,
            "pending_approvals": pending_approvals,
            "mttd_minutes": mttd_minutes,
            "mttr_minutes": mttr_minutes,
            "workflow_success_rate": workflow_success_rate,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_incident_timeline(db: Session, days: int = 30) -> List[dict]:
        """Return incidents grouped by day for the past N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        incidents = db.execute(
            select(Incident.detected_at, Incident.severity, Incident.status)
            .where(Incident.detected_at >= cutoff)
            .order_by(Incident.detected_at.asc())
        ).all()

        from collections import defaultdict
        grouped: dict = defaultdict(list)
        for row in incidents:
            day_key = row.detected_at.strftime("%Y-%m-%d") if row.detected_at else "unknown"
            grouped[day_key].append({"severity": row.severity, "status": row.status})

        timeline = [
            {"date": day, "incidents": items, "count": len(items)}
            for day, items in sorted(grouped.items())
        ]
        return timeline

    @staticmethod
    def get_inventory_health(db: Session) -> List[dict]:
        """Return all variants with their inventory health status."""
        rows = db.execute(
            select(
                ProductVariant.id,
                ProductVariant.sku,
                ProductVariant.size,
                ProductVariant.color,
                Inventory.quantity_on_hand,
                Inventory.quantity_reserved,
                Inventory.reorder_threshold,
                Inventory.warehouse_bin,
            )
            .join(Inventory, Inventory.variant_id == ProductVariant.id)
        ).all()

        result = []
        for row in rows:
            available = max(0, row.quantity_on_hand - row.quantity_reserved)
            if available == 0:
                health = "OUT_OF_STOCK"
            elif available <= row.reorder_threshold:
                health = "LOW_STOCK"
            else:
                health = "HEALTHY"

            result.append({
                "variant_id": row.id,
                "sku": row.sku,
                "size": row.size,
                "color": row.color,
                "quantity_on_hand": row.quantity_on_hand,
                "quantity_reserved": row.quantity_reserved,
                "quantity_available": available,
                "reorder_threshold": row.reorder_threshold,
                "warehouse_bin": row.warehouse_bin,
                "health_status": health,
            })
        return result

    @staticmethod
    def get_workflow_stats(db: Session) -> dict:
        """Workflow execution statistics."""
        status_rows = db.execute(
            select(WorkflowExecution.status, func.count(WorkflowExecution.id).label("cnt"))
            .group_by(WorkflowExecution.status)
        ).all()
        by_status = {row.status: row.cnt for row in status_rows}

        total = sum(by_status.values())
        completed = by_status.get("COMPLETED", 0)
        success_rate = round((completed / total) * 100, 1) if total > 0 else 0.0

        # Avg duration for completed workflows (seconds)
        completed_rows = db.execute(
            select(WorkflowExecution.started_at, WorkflowExecution.completed_at)
            .where(
                WorkflowExecution.status == "COMPLETED",
                WorkflowExecution.completed_at.isnot(None),
            )
        ).all()

        avg_duration_seconds: Optional[float] = None
        if completed_rows:
            durations = [
                (row.completed_at - row.started_at).total_seconds()
                for row in completed_rows
                if row.completed_at and row.started_at
            ]
            if durations:
                avg_duration_seconds = round(sum(durations) / len(durations), 2)

        return {
            "total_executions": total,
            "by_status": by_status,
            "success_rate_percent": success_rate,
            "avg_duration_seconds": avg_duration_seconds,
        }
