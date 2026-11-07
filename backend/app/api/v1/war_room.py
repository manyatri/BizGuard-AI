"""
AI War Room API — multi-agent investigation coordination.
GET  /api/v1/war-room/incidents/{id}/messages    — agent message feed
POST /api/v1/war-room/incidents/{id}/investigate — trigger investigation
GET  /api/v1/war-room/incidents/{id}/tasks       — agent task records
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.incidents import Incident, AgentTask, AgentMessage
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/war-room", tags=["AI War Room"])


@router.get("/incidents/{incident_id}/messages")
async def get_war_room_messages(incident_id: str, db: Session = Depends(get_db)):
    """Returns all agent messages for the incident."""
    incident = db.scalars(select(Incident).where(Incident.id == incident_id)).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    messages = db.scalars(
        select(AgentMessage)
        .where(AgentMessage.incident_id == incident_id)
        .order_by(AgentMessage.created_at.asc())
    ).all()

    return {
        "incident_id": incident_id,
        "incident_code": incident.incident_code,
        "total_messages": len(messages),
        "messages": [
            {
                "id": m.id,
                "sender_agent": m.sender_agent,
                "channel_source": m.channel_source,
                "message_type": m.message_type,
                "content": m.content,
                "metadata_json": m.metadata_json,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.post("/incidents/{incident_id}/investigate")
async def trigger_investigation(incident_id: str, db: Session = Depends(get_db)):
    """
    Triggers multi-agent investigation for the incident using the 5 specialized AI agents:
    @monitor-agent, @investigator-agent, @developer-agent, @tester-agent, @auditor-agent.
    """
    incident = db.scalars(select(Incident).where(Incident.id == incident_id)).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident.status = "INVESTIGATING"
    db.commit()

    # Run full multi-agent pipeline
    outputs = AgentOrchestrator.run_incident_war_room(db, incident)

    messages = db.scalars(
        select(AgentMessage)
        .where(AgentMessage.incident_id == incident_id)
        .order_by(AgentMessage.created_at.asc())
    ).all()

    tasks = db.scalars(
        select(AgentTask)
        .where(AgentTask.incident_id == incident_id)
    ).all()

    return {
        "incident_id": incident_id,
        "incident_code": incident.incident_code,
        "status": "investigation_complete",
        "tasks_created": len(tasks),
        "messages": [
            {
                "id": m.id,
                "sender_agent": m.sender_agent,
                "message_type": m.message_type,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }


@router.get("/incidents/{incident_id}/tasks")
async def get_agent_tasks(incident_id: str, db: Session = Depends(get_db)):
    """Returns all agent task records for the incident."""
    incident = db.scalars(select(Incident).where(Incident.id == incident_id)).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    tasks = db.scalars(
        select(AgentTask)
        .where(AgentTask.incident_id == incident_id)
        .order_by(AgentTask.started_at.asc())
    ).all()

    return {
        "incident_id": incident_id,
        "tasks": [
            {
                "id": t.id,
                "agent_role": t.agent_role,
                "status": t.status,
                "prompt_spec": t.prompt_spec,
                "output_artifacts": t.output_artifacts,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ],
    }
