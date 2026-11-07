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

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True) # e.g. INC-2026-081
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="CRITICAL", nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    status: Mapped[str] = mapped_column(
        String(50), 
        default="DETECTED", 
        nullable=False, 
        index=True
    ) # DETECTED, INVESTIGATING, PROPOSAL_READY, AWAITING_APPROVAL, EXECUTING_FIX, VERIFIED_RESOLVED, CLOSED
    detection_rule: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. RULE_VARIANT_INVENTORY_MISMATCH
    affected_order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    workflow_execution_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("workflow_executions.id"), nullable=True)
    root_cause_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blast_radius_analysis: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="incidents")
    workflow_execution: Mapped[Optional["WorkflowExecution"]] = relationship("WorkflowExecution", back_populates="incidents")
    tasks: Mapped[List["AgentTask"]] = relationship("AgentTask", back_populates="incident", cascade="all, delete-orphan")
    messages: Mapped[List["AgentMessage"]] = relationship("AgentMessage", back_populates="incident", cascade="all, delete-orphan")
    recovery_proposals: Mapped[List["RecoveryProposal"]] = relationship("RecoveryProposal", back_populates="incident", cascade="all, delete-orphan")
    approvals: Mapped[List["Approval"]] = relationship("Approval", back_populates="incident")

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False)
    agent_role: Mapped[str] = mapped_column(String(100), nullable=False) # TriageSpecialist, InventoryForensics, BillingAuditor, RecoveryPlanner
    prompt_spec: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ASSIGNED") # ASSIGNED, IN_PROGRESS, COMPLETED, FAILED
    output_artifacts: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="tasks")

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False)
    sender_agent: Mapped[str] = mapped_column(String(100), nullable=False) # Agent-Triage, Agent-Inventory, Operator
    channel_source: Mapped[str] = mapped_column(String(50), default="Switch-Bus") # Switch-Bus, Mattermost, WarRoom-UI
    message_type: Mapped[str] = mapped_column(String(50), default="HYPOTHESIS") # HYPOTHESIS, EVIDENCE, TEST_RESULT, PROPOSAL_NOTICE, HUMAN_INTERVENTION
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="messages")
