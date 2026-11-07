import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Any
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_name: Mapped[str] = mapped_column(String(100), default="OrderFulfillmentSaga", nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. order_id or order_number
    order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    current_step: Mapped[str] = mapped_column(String(100), default="ORDER_INITIALIZED", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), 
        default="RUNNING", 
        nullable=False, 
        index=True
    ) # RUNNING, COMPLETED, FAILED, STALLED_INCONSISTENT, COMPENSATED
    context_payload: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="workflow_executions")
    events: Mapped[List["WorkflowEvent"]] = relationship("WorkflowEvent", back_populates="execution", cascade="all, delete-orphan")
    incidents: Mapped[List["Incident"]] = relationship("Incident", back_populates="workflow_execution")

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_execution_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_executions.id"), nullable=False)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False) # ORDER_CREATED, PAYMENT_PROCESSED, INVENTORY_RESERVED, INVOICE_GENERATED
    step_number: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS") # SUCCESS, FAILED, INVARIANT_BREACH
    event_payload: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    execution: Mapped["WorkflowExecution"] = relationship("WorkflowExecution", back_populates="events")
