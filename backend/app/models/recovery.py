import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Any
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class RecoveryProposal(Base):
    __tablename__ = "recovery_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False)
    proposal_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True) # e.g. REC-2026-0042
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    pre_check_test_results: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    execution_steps: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True) # Array of atomic action instructions
    rollback_steps: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True) # Array of compensating reversal steps
    status: Mapped[str] = mapped_column(
        String(50), 
        default="DRAFTED", 
        nullable=False, 
        index=True
    ) # DRAFTED, READY_FOR_REVIEW, APPROVED, REJECTED, EXECUTED, FAILED_ROLLBACK
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="recovery_proposals")
    approvals: Mapped[List["Approval"]] = relationship("Approval", back_populates="proposal", cascade="all, delete-orphan")

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("recovery_proposals.id"), nullable=False)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False)
    approver_user: Mapped[str] = mapped_column(String(150), nullable=False) # e.g. operator-1@fashionops.com
    decision: Mapped[str] = mapped_column(String(20), nullable=False) # APPROVED, REJECTED
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # Tamper-proof digest
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    proposal: Mapped["RecoveryProposal"] = relationship("RecoveryProposal", back_populates="approvals")
    incident: Mapped["Incident"] = relationship("Incident", back_populates="approvals")
