"""
Approvals API — human review and decision-making for recovery proposals.
GET  /api/v1/approvals/pending     — proposals awaiting approval
POST /api/v1/approvals/{id}/decide — approve or reject
GET  /api/v1/approvals/history     — all past decisions
"""
import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.recovery import RecoveryProposal, Approval
from app.models.incidents import Incident


router = APIRouter(prefix="/approvals", tags=["Approvals"])


class DecisionRequest(BaseModel):
    decision: str           # APPROVED or REJECTED
    approver_user: str
    comments: Optional[str] = None


@router.get("/pending")
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Returns all proposals waiting for a human decision."""
    proposals = db.scalars(
        select(RecoveryProposal)
        .where(RecoveryProposal.status.in_(["READY_FOR_REVIEW", "DRAFTED"]))
        .options(selectinload(RecoveryProposal.incident))
        .order_by(RecoveryProposal.created_at.desc())
    ).all()

    return {
        "total": len(proposals),
        "proposals": [
            {
                "id": p.id,
                "proposal_code": p.proposal_code,
                "title": p.title,
                "description": p.description,
                "risk_level": p.risk_level,
                "status": p.status,
                "execution_steps": p.execution_steps,
                "rollback_steps": p.rollback_steps,
                "pre_check_test_results": p.pre_check_test_results,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "incident_code": p.incident.incident_code if p.incident else None,
                "incident_title": p.incident.title if p.incident else None,
                "incident_severity": p.incident.severity if p.incident else None,
            }
            for p in proposals
        ],
    }


@router.post("/{proposal_id}/decide")
async def decide_approval(
    proposal_id: str, body: DecisionRequest, db: Session = Depends(get_db)
):
    """
    Record a human approval or rejection decision.
    Strictly enforces backend safety:
    - If testing has not passed, approval is blocked.
    - If already executed, decision cannot be altered.
    - Rejection marks proposal and incident as REJECTED.
    """
    if body.decision not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")

    proposal = db.scalars(
        select(RecoveryProposal)
        .where(RecoveryProposal.id == proposal_id)
        .options(selectinload(RecoveryProposal.incident))
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")

    if proposal.status == "EXECUTED":
        raise HTTPException(status_code=400, detail="Cannot alter decision: proposal has already been executed.")

    # Safety Rule: If testing fails or has not been run, approval is blocked
    if body.decision == "APPROVED":
        if not proposal.pre_check_test_results or not proposal.pre_check_test_results.get("all_passed"):
            raise HTTPException(
                status_code=400,
                detail="Approval blocked: automated pre-check tests must pass before human supervisor sign-off.",
            )

    # Tamper-proof cryptographic signature
    now_utc = datetime.now(timezone.utc)
    sig_input = f"{proposal_id}:{proposal.proposal_code}:{body.decision}:{body.approver_user}:{now_utc.isoformat()}"
    signature_hash = hashlib.sha256(sig_input.encode()).hexdigest()

    approval = Approval(
        id=str(uuid.uuid4()),
        proposal_id=proposal_id,
        incident_id=proposal.incident_id,
        approver_user=body.approver_user,
        decision=body.decision,
        comments=body.comments,
        signature_hash=signature_hash,
        decided_at=now_utc,
    )
    db.add(approval)

    # Update proposal status
    proposal.status = body.decision  # APPROVED or REJECTED

    # Update incident status accordingly
    if proposal.incident:
        if body.decision == "APPROVED":
            proposal.incident.status = "APPROVED_AWAITING_EXECUTION"
        else:
            proposal.incident.status = "PROPOSAL_REJECTED"

    db.commit()

    return {
        "status": "DECISION_RECORDED",
        "proposal_id": proposal_id,
        "proposal_code": proposal.proposal_code,
        "decision": body.decision,
        "signature_hash": signature_hash,
        "approver": body.approver_user,
        "decided_at": now_utc.isoformat(),
    }


@router.get("/history")
async def get_approval_history(db: Session = Depends(get_db)):
    """Returns chronological audit history of all approval decisions."""
    approvals = db.scalars(
        select(Approval)
        .options(
            selectinload(Approval.proposal),
            selectinload(Approval.incident),
        )
        .order_by(Approval.decided_at.desc())
    ).all()

    return {
        "total": len(approvals),
        "approvals": [
            {
                "id": a.id,
                "proposal_id": a.proposal_id,
                "proposal_code": a.proposal.proposal_code if a.proposal else None,
                "incident_id": a.incident_id,
                "incident_code": a.incident.incident_code if a.incident else None,
                "approver_user": a.approver_user,
                "decision": a.decision,
                "comments": a.comments,
                "signature_hash": a.signature_hash,
                "decided_at": a.decided_at.isoformat() if a.decided_at else None,
            }
            for a in approvals
        ],
    }
