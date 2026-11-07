from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ApprovalRead(BaseModel):
    id: str
    proposal_id: str
    incident_id: str
    approver_user: str
    decision: str
    comments: Optional[str] = None
    signature_hash: Optional[str] = None
    decided_at: datetime

    class Config:
        from_attributes = True

class ApprovalDecisionCreate(BaseModel):
    approver_user: str
    decision: str # APPROVED, REJECTED
    comments: Optional[str] = None

class RecoveryProposalRead(BaseModel):
    id: str
    incident_id: str
    proposal_code: str
    title: str
    description: Optional[str] = None
    risk_level: str
    pre_check_test_results: Optional[Any] = None
    execution_steps: Optional[Any] = None
    rollback_steps: Optional[Any] = None
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    approvals: List[ApprovalRead] = []

    class Config:
        from_attributes = True
