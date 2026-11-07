"""
@investigator-agent — performs root cause analysis using LLM or structured reasoning.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.incidents import Incident
from app.models.orders import Order, OrderItem, Payment
from app.models.catalog import ProductVariant, Inventory
from app.agents.base_agent import BaseAgent, AgentOutput, _utc
from app.agents.llm_provider import LLMProvider
from typing import Any, Dict


class InvestigatorAgent(BaseAgent):
    agent_id = "@investigator-agent"
    agent_role = "InvestigatorAgent"
    message_type = "EVIDENCE"

    def run(self, db: Session, incident: Incident, context: Dict[str, Any]) -> AgentOutput:
        task = self._get_or_create_task(
            db, incident.id,
            f"Investigate root cause of incident {incident.incident_code}. "
            "Collect DB evidence and produce a structured root-cause analysis."
        )

        try:
            evidence = self._collect_evidence(db, incident)

            system_prompt = (
                "You are @investigator-agent for BizGuard AI, an autonomous business reliability "
                "platform for a clothing e-commerce store. Your role is to analyze incident data "
                "and produce a precise, evidence-backed root cause analysis. "
                "Be technical but concise. Use markdown. Never fabricate data."
            )
            user_message = (
                f"Incident: {incident.incident_code}\n"
                f"Title: {incident.title}\n"
                f"Detection Rule: {incident.detection_rule}\n"
                f"Current Summary: {incident.root_cause_summary}\n\n"
                f"Database Evidence:\n{self._format_evidence(evidence)}\n\n"
                "Provide: 1) Root cause, 2) Evidence chain, 3) Blast radius, 4) Confidence score (0-1)."
            )

            llm_response = LLMProvider.call(system_prompt, user_message, max_tokens=800)
            llm_generated = LLMProvider.is_real_llm_available()

            # Update incident root_cause_summary
            incident.root_cause_summary = (
                incident.root_cause_summary or ""
            ) + f"\n\n**AI Analysis**:\n{llm_response[:500]}"
            db.commit()

            findings = {
                "evidence": evidence,
                "llm_generated": llm_generated,
                "analysis_length": len(llm_response),
            }

            content = (
                f"🔬 **[@investigator-agent] Root Cause Analysis — {incident.incident_code}**\n\n"
                f"**Rule**: `{incident.detection_rule}`\n\n"
                f"**Database Evidence**:\n{self._format_evidence(evidence)}\n\n"
                f"**AI Analysis**:\n{llm_response}"
            )

            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="root_cause_analysis",
                findings=findings,
                content_markdown=content,
                recommended_next_action="CREATE_RECOVERY_PROPOSAL",
                execution_status="COMPLETED",
                llm_generated=llm_generated,
            )
            self._complete_task(db, task, output)
            return output

        except Exception as e:
            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="root_cause_analysis",
                findings={"error": str(e)},
                content_markdown=f"❌ **[@investigator-agent] Investigation failed**: {e}",
                recommended_next_action="RETRY",
                execution_status="FAILED",
                error=str(e),
            )
            self._complete_task(db, task, output)
            return output

    def _collect_evidence(self, db: Session, incident: Incident) -> Dict[str, Any]:
        evidence: Dict[str, Any] = {
            "incident_code": incident.incident_code,
            "detection_rule": incident.detection_rule,
            "severity": incident.severity,
        }

        if incident.affected_order_id:
            order = db.scalars(
                select(Order)
                .where(Order.id == incident.affected_order_id)
                .options(
                    selectinload(Order.items).selectinload(OrderItem.variant)
                        .selectinload(ProductVariant.inventory),
                    selectinload(Order.payments),
                )
            ).first()
            if order:
                evidence["order"] = {
                    "order_number": order.order_number,
                    "status": order.status,
                    "total_amount": float(order.total_amount),
                    "customer": order.customer_name,
                    "payments": [{"status": p.status, "amount": float(p.amount)} for p in order.payments],
                    "items": [
                        {
                            "sku": item.variant.sku if item.variant else "unknown",
                            "ordered_size": item.ordered_size,
                            "ordered_color": item.ordered_color,
                            "quantity": item.quantity,
                            "inventory": {
                                "on_hand": item.variant.inventory.quantity_on_hand if item.variant and item.variant.inventory else "N/A",
                                "reserved": item.variant.inventory.quantity_reserved if item.variant and item.variant.inventory else "N/A",
                                "available": item.variant.inventory.quantity_available if item.variant and item.variant.inventory else "N/A",
                            } if item.variant else {},
                        }
                        for item in order.items
                    ],
                }

        if incident.blast_radius_analysis:
            evidence["blast_radius"] = incident.blast_radius_analysis

        return evidence

    def _format_evidence(self, evidence: Dict[str, Any]) -> str:
        lines = []
        if "order" in evidence:
            o = evidence["order"]
            lines.append(f"**Order**: {o.get('order_number')} | Status: `{o.get('status')}` | Total: ₹{o.get('total_amount')}")
            lines.append(f"**Customer**: {o.get('customer')}")
            for item in o.get("items", []):
                inv = item.get("inventory", {})
                lines.append(
                    f"  - SKU `{item['sku']}` | Size: {item['ordered_size']} | Color: {item['ordered_color']} | "
                    f"on_hand={inv.get('on_hand')} reserved={inv.get('reserved')} available={inv.get('available')}"
                )
            payments = o.get("payments", [])
            lines.append(f"**Payments**: {len(payments)} record(s) → {[p['status'] for p in payments]}")
        if "blast_radius" in evidence:
            br = evidence["blast_radius"]
            for k, v in br.items():
                lines.append(f"  `{k}`: {v}")
        return "\n".join(lines) if lines else "No structured evidence collected."
