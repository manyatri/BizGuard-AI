"""
Bug Detection & Incident Management API
GET /api/v1/bugs/detect         — run invariant scan
GET /api/v1/bugs/incidents      — list all incidents
GET /api/v1/bugs/incidents/{id} — incident detail
GET /api/v1/bugs/incidents/{id}/timeline — workflow events
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.core.database import get_db
from app.services.invariant_detector import InvariantDetector
from app.models.workflow import WorkflowExecution, WorkflowEvent

router = APIRouter(prefix="/bugs", tags=["Bug Detection"])


def _incident_dict(inc) -> dict:
    return {
        "id": inc.id,
        "incident_code": inc.incident_code,
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "detection_rule": inc.detection_rule,
        "affected_order_id": inc.affected_order_id,
        "workflow_execution_id": inc.workflow_execution_id,
        "root_cause_summary": inc.root_cause_summary,
        "blast_radius_analysis": inc.blast_radius_analysis,
        "detected_at": inc.detected_at.isoformat() if inc.detected_at else None,
        "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
        "affected_order_number": inc.order.order_number if inc.order else None,
        "affected_customer": inc.order.customer_name if inc.order else None,
        "recovery_proposals_count": len(inc.recovery_proposals) if hasattr(inc, "recovery_proposals") else 0,
    }


@router.get("/detect")
async def detect_invariant_violations(db: Session = Depends(get_db)):
    """Run the full invariant scan and return all violations found."""
    incidents = InvariantDetector.run_full_scan(db)
    return {
        "scan_completed": True,
        "violations_found": len(incidents),
        "incidents": [_incident_dict(i) for i in incidents],
    }


@router.get("/incidents")
async def list_incidents(db: Session = Depends(get_db)):
    incidents = InvariantDetector.get_all_incidents(db)
    return {
        "total": len(incidents),
        "incidents": [_incident_dict(i) for i in incidents],
    }


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = InvariantDetector.get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    data = _incident_dict(incident)

    # Enrich with tasks and messages
    data["tasks"] = [
        {
            "id": t.id,
            "agent_role": t.agent_role,
            "status": t.status,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "output_artifacts": t.output_artifacts,
        }
        for t in (incident.tasks or [])
    ]
    data["messages"] = [
        {
            "id": m.id,
            "sender_agent": m.sender_agent,
            "channel_source": m.channel_source,
            "message_type": m.message_type,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in sorted(incident.messages or [], key=lambda x: x.created_at)
    ]
    data["recovery_proposals"] = [
        {
            "id": p.id,
            "proposal_code": p.proposal_code,
            "title": p.title,
            "status": p.status,
            "risk_level": p.risk_level,
        }
        for p in (incident.recovery_proposals or [])
    ]
    return data


@router.get("/incidents/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    incident = InvariantDetector.get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    events = []
    if incident.workflow_execution_id:
        wf = db.scalars(
            select(WorkflowExecution)
            .where(WorkflowExecution.id == incident.workflow_execution_id)
            .options(selectinload(WorkflowExecution.events))
        ).first()
        if wf:
            events = [
                {
                    "id": e.id,
                    "event_name": e.event_name,
                    "step_number": e.step_number,
                    "status": e.status,
                    "event_payload": e.event_payload,
                    "error_message": e.error_message,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in sorted(wf.events, key=lambda x: x.step_number)
            ]

    return {
        "incident_id": incident_id,
        "incident_code": incident.incident_code,
        "workflow_execution_id": incident.workflow_execution_id,
        "events": events,
    }
