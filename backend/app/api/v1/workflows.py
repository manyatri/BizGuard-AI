from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["Workflow Sagas"])

@router.get("")
async def list_workflows(db: Session = Depends(get_db)):
    executions = WorkflowEngine.get_executions(db)
    return [
        {
            "id": ex.id,
            "workflow_name": ex.workflow_name,
            "correlation_id": ex.correlation_id,
            "order_id": ex.order_id,
            "current_step": ex.current_step,
            "status": ex.status,
            "started_at": ex.started_at,
            "completed_at": ex.completed_at,
            "events_count": len(ex.events),
            "events": [
                {
                    "id": ev.id,
                    "event_name": ev.event_name,
                    "step_number": ev.step_number,
                    "status": ev.status,
                    "event_payload": ev.event_payload,
                    "error_message": ev.error_message,
                    "created_at": ev.created_at
                }
                for ev in ex.events
            ]
        }
        for ex in executions
    ]

@router.get("/{execution_id}")
async def get_workflow(execution_id: str, db: Session = Depends(get_db)):
    ex = WorkflowEngine.get_execution_by_id(db, execution_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    return {
        "id": ex.id,
        "workflow_name": ex.workflow_name,
        "correlation_id": ex.correlation_id,
        "order_id": ex.order_id,
        "current_step": ex.current_step,
        "status": ex.status,
        "started_at": ex.started_at,
        "completed_at": ex.completed_at,
        "events": [
            {
                "id": ev.id,
                "event_name": ev.event_name,
                "step_number": ev.step_number,
                "status": ev.status,
                "event_payload": ev.event_payload,
                "error_message": ev.error_message,
                "created_at": ev.created_at
            }
            for ev in ex.events
        ]
    }
