"""
@developer-agent — proposes database recovery steps based on investigator findings.
Does NOT execute anything. Creates a RecoveryProposal pending human approval.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.incidents import Incident
from app.models.recovery import RecoveryProposal
from app.agents.base_agent import BaseAgent, AgentOutput, _utc
from app.agents.llm_provider import LLMProvider
from typing import Any, Dict


class DeveloperAgent(BaseAgent):
    agent_id = "@developer-agent"
    agent_role = "DeveloperAgent"
    message_type = "PROPOSAL_NOTICE"

    def run(self, db: Session, incident: Incident, context: Dict[str, Any]) -> AgentOutput:
        task = self._get_or_create_task(
            db, incident.id,
            f"Design a safe recovery proposal for incident {incident.incident_code}. "
            "Propose execution and rollback steps. Do NOT execute."
        )

        try:
            # Check if a proposal already exists for this incident
            existing_proposal = db.scalars(
                select(RecoveryProposal).where(RecoveryProposal.incident_id == incident.id)
            ).first()

            if existing_proposal:
                content = (
                    f"🛠️ **[@developer-agent] Recovery Proposal Already Exists**\n\n"
                    f"Proposal `{existing_proposal.id[:8]}...` already created for {incident.incident_code}.\n"
                    f"Status: `{existing_proposal.status}`\n\n"
                    "No new proposal created. Proceeding to @tester-agent for pre-checks."
                )
                output = AgentOutput(
                    incident_id=incident.id,
                    agent_id=self.agent_id,
                    agent_role=self.agent_role,
                    task_performed="proposal_check",
                    findings={"existing_proposal_id": existing_proposal.id, "status": existing_proposal.status},
                    content_markdown=content,
                    recommended_next_action="RUN_PRE_CHECKS",
                    execution_status="COMPLETED",
                )
                self._complete_task(db, task, output)
                return output

            system_prompt = (
                "You are @developer-agent for BizGuard AI. Based on incident investigation findings, "
                "design a safe, minimal, reversible database recovery plan. "
                "Output as numbered steps. Include rollback steps. Never say 'execute immediately'. "
                "Always note that human approval is required before execution."
            )
            user_message = (
                f"Incident: {incident.incident_code}\n"
                f"Title: {incident.title}\n"
                f"Detection Rule: {incident.detection_rule}\n"
                f"Root Cause: {incident.root_cause_summary}\n"
                f"Blast Radius: {incident.blast_radius_analysis}\n"
                f"Investigator Context: {context.get('investigator_findings', 'See root_cause_summary')}\n\n"
                "Design the recovery steps and rollback plan."
            )
            llm_response = LLMProvider.call(system_prompt, user_message, max_tokens=600)
            llm_generated = LLMProvider.is_real_llm_available()

            # Build execution steps based on the detection rule
            exec_steps, rollback_steps = self._build_steps(incident)

            proposal = RecoveryProposal(
                id=str(uuid.uuid4()),
                incident_id=incident.id,
                proposed_by="@developer-agent",
                title=f"Auto-Proposed Recovery — {incident.incident_code}",
                description=llm_response[:1000],
                execution_steps=exec_steps,
                rollback_steps=rollback_steps,
                risk_level="LOW",
                status="PENDING_REVIEW",
                created_at=_utc(),
            )
            db.add(proposal)
            incident.status = "PROPOSAL_READY"
            db.commit()
            db.refresh(proposal)

            content = (
                f"🛠️ **[@developer-agent] Recovery Proposal Created**\n\n"
                f"**Incident**: {incident.incident_code}\n"
                f"**Proposal ID**: `{proposal.id[:8]}...`\n"
                f"**Risk Level**: {proposal.risk_level}\n\n"
                f"**Proposed Steps**:\n{self._steps_to_md(exec_steps)}\n\n"
                f"**Rollback Steps**:\n{self._steps_to_md(rollback_steps)}\n\n"
                f"**AI Analysis**:\n{llm_response}\n\n"
                "⚠️ **Awaiting human approval before any execution.** "
                "Handing off to @tester-agent for pre-condition verification."
            )

            output = AgentOutput(
                incident_id=incident.id,
                agent_id=self.agent_id,
                agent_role=self.agent_role,
                task_performed="create_recovery_proposal",
                findings={
                    "proposal_id": proposal.id,
                    "execution_steps": exec_steps,
                    "rollback_steps": rollback_steps,
                    "llm_generated": llm_generated,
                },
                content_markdown=content,
                recommended_next_action="RUN_PRE_CHECKS",
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
                task_performed="create_recovery_proposal",
                findings={"error": str(e)},
                content_markdown=f"❌ **[@developer-agent] Proposal creation failed**: {e}",
                recommended_next_action="RETRY",
                execution_status="FAILED",
                error=str(e),
            )
            self._complete_task(db, task, output)
            return output

    def _build_steps(self, incident: Incident):
        rule = incident.detection_rule or ""
        br = incident.blast_radius_analysis or {}

        if "VARIANT_INVENTORY_MISMATCH" in rule or "COLOR_INVENTORY_MISMATCH" in rule:
            ordered_sku = br.get("ordered_variant_sku", "?")
            bad_sku = br.get("bad_sibling_sku", "?")
            exec_steps = [
                {"step": 1, "action": "VERIFY_STATE", "description": f"Confirm {ordered_sku} reserved=0 and {bad_sku} has unexpected reservation"},
                {"step": 2, "action": "RELEASE_WRONG_RESERVATION", "description": f"release_reservation(variant_sku='{bad_sku}', qty=1)"},
                {"step": 3, "action": "APPLY_CORRECT_RESERVATION", "description": f"reserve_stock(variant_sku='{ordered_sku}', qty=1)"},
                {"step": 4, "action": "VERIFY_ORDER_ITEM", "description": "Confirm order_items.variant_id still references correct variant"},
                {"step": 5, "action": "ADVANCE_ORDER_STATUS", "description": "Set order.status = INVOICED to resume fulfillment"},
                {"step": 6, "action": "POST_VERIFY", "description": "Confirm all inventory quantities are consistent"},
            ]
            rollback_steps = [
                {"step": 1, "action": "RELEASE_CORRECT_RESERVATION", "description": f"release_reservation(variant_sku='{ordered_sku}', qty=1)"},
                {"step": 2, "action": "RESTORE_WRONG_RESERVATION", "description": f"reserve_stock(variant_sku='{bad_sku}', qty=1)"},
                {"step": 3, "action": "REVERT_ORDER_STATUS", "description": "Set order.status = STALLED_INCONSISTENT"},
            ]
        elif "NEGATIVE_INVENTORY" in rule:
            sku = br.get("sku", "?")
            exec_steps = [
                {"step": 1, "action": "VERIFY_STATE", "description": f"Confirm {sku} quantity_reserved > quantity_on_hand"},
                {"step": 2, "action": "RESET_RESERVATION", "description": f"Set inventories.quantity_reserved = quantity_on_hand for {sku}"},
                {"step": 3, "action": "CREATE_AUDIT_LOG", "description": "Log correction with before/after values"},
            ]
            rollback_steps = [
                {"step": 1, "action": "RESTORE_RESERVED", "description": f"Restore original quantity_reserved for {sku}"},
            ]
        elif "SHIPPED_WITHOUT_PAYMENT" in rule:
            exec_steps = [
                {"step": 1, "action": "HALT_SHIPMENT", "description": "Flag order for manual review — do not proceed with delivery"},
                {"step": 2, "action": "CONTACT_CUSTOMER", "description": "Notify customer that payment is required"},
                {"step": 3, "action": "REVERT_ORDER_STATUS", "description": "Set order.status = PENDING_PAYMENT"},
            ]
            rollback_steps = [
                {"step": 1, "action": "RESTORE_SHIPPED_STATUS", "description": "Revert order to SHIPPED if payment verified"},
            ]
        elif "DUPLICATE_PAYMENT" in rule:
            exec_steps = [
                {"step": 1, "action": "IDENTIFY_DUPLICATE", "description": "Determine which payment is the duplicate (later transaction_reference)"},
                {"step": 2, "action": "INITIATE_REFUND", "description": "Issue refund for duplicate payment amount via payment gateway"},
                {"step": 3, "action": "UPDATE_PAYMENT_STATUS", "description": "Mark duplicate payment as REFUNDED"},
            ]
            rollback_steps = [
                {"step": 1, "action": "CANCEL_REFUND", "description": "Contact payment gateway to cancel refund if erroneously issued"},
            ]
        elif "INVOICE_AMOUNT_MISMATCH" in rule:
            exec_steps = [
                {"step": 1, "action": "VOID_INCORRECT_INVOICE", "description": "Set incorrect invoice status to VOIDED"},
                {"step": 2, "action": "REGENERATE_INVOICE", "description": "Generate new invoice with correct amount matching order total"},
                {"step": 3, "action": "NOTIFY_CUSTOMER", "description": "Send corrected invoice to customer email"},
            ]
            rollback_steps = [
                {"step": 1, "action": "RESTORE_ORIGINAL_INVOICE", "description": "Revert invoice to ISSUED status with original amount"},
            ]
        else:
            exec_steps = [
                {"step": 1, "action": "MANUAL_REVIEW", "description": "Review incident manually — no automated steps configured for this rule"},
            ]
            rollback_steps = []

        return exec_steps, rollback_steps

    def _steps_to_md(self, steps) -> str:
        if not steps:
            return "_(none)_"
        return "\n".join(f"{s['step']}. **{s['action']}** — {s['description']}" for s in steps)
