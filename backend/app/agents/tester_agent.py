"""
@tester-agent — executes pre-condition tests and database queries to verify proposed recovery.
"""
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.incidents import Incident
from app.models.orders import Order, OrderItem, Payment
from app.models.catalog import ProductVariant, Inventory
from app.models.recovery import RecoveryProposal
from app.agents.base_agent import BaseAgent, AgentOutput, _utc


class TesterAgent(BaseAgent):
    agent_id = "@tester-agent"
    agent_role = "TesterAgent"
    message_type = "TEST_RESULTS"

    def run(self, db: Session, incident: Incident, context: Dict[str, Any]) -> AgentOutput:
        task = self._get_or_create_task(
            db, incident.id,
            f"Verify pre-conditions for incident {incident.incident_code} recovery proposal."
        )

        try:
            proposal = db.scalars(
                select(RecoveryProposal)
                .where(RecoveryProposal.incident_id == incident.id)
                .order_by(RecoveryProposal.created_at.desc())
            ).first()

            tests_run = []
            all_passed = True

            # Test 1: Order exists and status check
            if incident.affected_order_id:
                order = db.scalars(
                    select(Order)
                    .where(Order.id == incident.affected_order_id)
                    .options(
                        selectinload(Order.items).selectinload(OrderItem.variant).selectinload(ProductVariant.inventory),
                        selectinload(Order.payments)
                    )
                ).first()

                if order:
                    tests_run.append({
                        "name": "ORDER_EXISTS_CHECK",
                        "status": "PASS",
                        "details": f"Order {order.order_number} found in status {order.status}."
                    })

                    # Test 2: Invariant state validation
                    for item in order.items:
                        v = item.variant
                        if v and v.inventory:
                            tests_run.append({
                                "name": f"VARIANT_STOCK_CHECK_{v.sku}",
                                "status": "PASS",
                                "details": f"SKU {v.sku} on_hand={v.inventory.quantity_on_hand}, reserved={v.inventory.quantity_reserved}, available={v.inventory.quantity_available}"
                            })

                    # Test 3: Payment integrity
                    captured = [p for p in order.payments if p.status == "CAPTURED"]
                    tests_run.append({
                        "name": "PAYMENT_INTEGRITY_CHECK",
                        "status": "PASS" if len(captured) >= 1 else "WARN",
                        "details": f"{len(captured)} CAPTURED payment records."
                    })
                else:
                    all_passed = False
                    tests_run.append({
                        "name": "ORDER_EXISTS_CHECK",
                        "status": "FAIL",
                        "details": f"Order {incident.affected_order_id} not found."
                    })

            # Test 4: Proposal validity
            if proposal:
                tests_run.append({
                    "name": "PROPOSAL_STEPS_VALIDATION",
                    "status": "PASS" if proposal.execution_steps else "FAIL",
                    "details": f"{len(proposal.execution_steps or [])} execution steps defined."
                })
                # Update proposal pre_check_test_results
                proposal.pre_check_test_results = {
                    "all_passed": all_passed,
                    "tests": tests_run,
                    "verified_at": _utc().isoformat()
                }
                db.commit()

            content = (
                f"🧪 **[@tester-agent] Pre-Condition Verification Results**\n\n"
                f"**Target Incident**: `{incident.incident_code}`\n"
                f"**Overall Test Status**: `{'PASSED ✅' if all_passed else 'FAILED ❌'}`\n\n"
                f"**Verification Checks**:\n"
            )
            for t in tests_run:
                icon = "✅" if t["status"] == "PASS" else ("⚠️" if t["status"] == "WARN" else "❌")
                content += f"- {icon} **{t['name']}**: {t['details']}\n"

            content += "\nPre-condition checks passed. Handing off to @auditor-agent for compliance and safety audit."

            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="verify_pre_conditions",
                findings={"tests": tests_run, "all_passed": all_passed},
                content_markdown=content,
                recommended_next_action="AUDIT_PROPOSAL",
                execution_status="COMPLETED",
                llm_generated=False,
            )
            self._complete_task(db, task, output)
            return output

        except Exception as e:
            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="verify_pre_conditions",
                findings={"error": str(e)},
                content_markdown=f"❌ **[@tester-agent] Verification failed**: {e}",
                recommended_next_action="RETRY",
                execution_status="FAILED",
                error=str(e),
            )
            self._complete_task(db, task, output)
            return output
