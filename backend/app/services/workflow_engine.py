import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional, List, Any
from app.models.workflow import WorkflowExecution, WorkflowEvent

class WorkflowEngine:
    @staticmethod
    def create_execution(
        db: Session, 
        correlation_id: str, 
        order_id: Optional[str] = None,
        workflow_name: str = "OrderFulfillmentSaga",
        initial_context: Optional[dict] = None
    ) -> WorkflowExecution:
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_name=workflow_name,
            correlation_id=correlation_id,
            order_id=order_id,
            current_step="1_ORDER_PLACED",
            status="RUNNING",
            context_payload=initial_context or {},
            started_at=datetime.now(timezone.utc)
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    @staticmethod
    def log_event(
        db: Session,
        execution_id: str,
        event_name: str,
        step_number: int,
        status: str = "SUCCESS",
        payload: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> WorkflowEvent:
        event = WorkflowEvent(
            id=str(uuid.uuid4()),
            workflow_execution_id=execution_id,
            event_name=event_name,
            step_number=step_number,
            status=status,
            event_payload=payload or {},
            error_message=error_message,
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def transition_step(
        db: Session,
        execution_id: str,
        new_step: str,
        status: str = "RUNNING"
    ) -> Optional[WorkflowExecution]:
        execution = db.scalars(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        ).first()
        if execution:
            execution.current_step = new_step
            execution.status = status
            if status in ["COMPLETED", "FAILED", "COMPENSATED"]:
                execution.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(execution)
        return execution

    @staticmethod
    def get_executions(db: Session) -> List[WorkflowExecution]:
        stmt = select(WorkflowExecution).options(selectinload(WorkflowExecution.events)).order_by(WorkflowExecution.started_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_execution_by_id(db: Session, execution_id: str) -> Optional[WorkflowExecution]:
        stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id).options(selectinload(WorkflowExecution.events))
        return db.scalars(stmt).first()
