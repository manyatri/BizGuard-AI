"""
Recovery Engine API
POST /api/v1/recovery/proposals              — create proposal
GET  /api/v1/recovery/proposals              — list proposals
GET  /api/v1/recovery/proposals/{id}         — proposal detail
POST /api/v1/recovery/proposals/{id}/pre-check — run pre-checks
POST /api/v1/recovery/execute/{id}           — execute if APPROVED
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/recovery", tags=["Recovery"])


class CreateProposalRequest(BaseModel):
    incident_id: str


class ExecuteRequest(BaseModel):
    approver: str


def _proposal_dict(p) -> dict:
    return {
        "id": p.id,
        "incident_id": p.incident_id,
        "proposal_code": p.proposal_code,
        "title": p.title,
        "description": p.description,
        "risk_level": p.risk_level,
        "status": p.status,
        "execution_steps": p.execution_steps,
        "rollback_steps": p.rollback_steps,
        "pre_check_test_results": p.pre_check_test_results,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "executed_at": p.executed_at.isoformat() if p.executed_at else None,
        "incident_code": p.incident.incident_code if p.incident else None,
        "incident_title": p.incident.title if p.incident else None,
        "incident_severity": p.incident.severity if p.incident else None,
    }


@router.post("/proposals")
async def create_proposal(body: CreateProposalRequest, db: Session = Depends(get_db)):
    try:
        proposal = RecoveryService.create_proposal(db, body.incident_id)
        return _proposal_dict(proposal)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/proposals")
async def list_proposals(db: Session = Depends(get_db)):
    proposals = RecoveryService.get_all_proposals(db)
    return {"total": len(proposals), "proposals": [_proposal_dict(p) for p in proposals]}


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = RecoveryService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
    data = _proposal_dict(proposal)
    data["approvals"] = [
        {
            "id": a.id,
            "approver_user": a.approver_user,
            "decision": a.decision,
            "comments": a.comments,
            "decided_at": a.decided_at.isoformat() if a.decided_at else None,
        }
        for a in (proposal.approvals or [])
    ]
    return data


@router.post("/proposals/{proposal_id}/pre-check")
async def run_pre_checks(proposal_id: str, db: Session = Depends(get_db)):
    try:
        return RecoveryService.run_pre_checks(db, proposal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/execute/{proposal_id}")
async def execute_proposal(proposal_id: str, body: ExecuteRequest, db: Session = Depends(get_db)):
    try:
        return RecoveryService.execute_approved_proposal(db, proposal_id, body.approver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
