"""
WebSocket endpoints for real-time workflow and incident monitoring.
WS /ws/workflow/{execution_id} — streams workflow events
WS /ws/incidents/live          — streams new incident notifications
"""
import asyncio
import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.workflow import WorkflowExecution, WorkflowEvent
from app.models.incidents import Incident

router = APIRouter(tags=["WebSocket"])


def _serialize_event(e: WorkflowEvent) -> dict:
    return {
        "id": e.id,
        "event_name": e.event_name,
        "step_number": e.step_number,
        "status": e.status,
        "event_payload": e.event_payload,
        "error_message": e.error_message,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def _serialize_incident(i: Incident) -> dict:
    return {
        "id": i.id,
        "incident_code": i.incident_code,
        "title": i.title,
        "severity": i.severity,
        "status": i.status,
        "detected_at": i.detected_at.isoformat() if i.detected_at else None,
    }


@router.websocket("/ws/workflow/{execution_id}")
async def workflow_ws(websocket: WebSocket, execution_id: str):
    """
    Streams workflow events for a specific execution.
    Sends history on connect, then polls for new events every 2 seconds.
    """
    await websocket.accept()
    db: Session = SessionLocal()
    last_event_id: str | None = None
    ping_counter = 0

    try:
        # Send history on connect
        execution = db.scalars(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        ).first()

        if not execution:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Workflow execution {execution_id} not found",
            }))
            await websocket.close()
            return

        events = db.scalars(
            select(WorkflowEvent)
            .where(WorkflowEvent.workflow_execution_id == execution_id)
            .order_by(WorkflowEvent.step_number.asc())
        ).all()

        await websocket.send_text(json.dumps({
            "type": "history",
            "execution_id": execution_id,
            "execution_status": execution.status,
            "current_step": execution.current_step,
            "events": [_serialize_event(e) for e in events],
        }))

        if events:
            last_event_id = events[-1].id

        # Poll for new events every 2 seconds
        while True:
            await asyncio.sleep(2)
            ping_counter += 1

            # Refresh execution status
            db.expire(execution)
            new_events_query = select(WorkflowEvent).where(
                WorkflowEvent.workflow_execution_id == execution_id
            )
            if last_event_id:
                # Get events newer than the last seen one
                # We use step_number ordering and fetch all, skip known ones
                all_events = db.scalars(
                    new_events_query.order_by(WorkflowEvent.step_number.asc())
                ).all()
                known_ids = {last_event_id}
                found_last = False
                new_events = []
                for ev in all_events:
                    if ev.id == last_event_id:
                        found_last = True
                        continue
                    if found_last:
                        new_events.append(ev)
            else:
                new_events = []

            if new_events:
                for ev in new_events:
                    await websocket.send_text(json.dumps({
                        "type": "new_event",
                        "event": _serialize_event(ev),
                        "execution_status": execution.status,
                    }))
                last_event_id = new_events[-1].id

            # Send ping every 10s (5 cycles × 2s)
            if ping_counter % 5 == 0:
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "execution_status": execution.status,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
    finally:
        db.close()


@router.websocket("/ws/incidents/live")
async def incidents_live_ws(websocket: WebSocket):
    """
    Streams new incident notifications.
    Sends count on connect, then notifies when new incidents are detected.
    """
    await websocket.accept()
    db: Session = SessionLocal()
    known_incident_ids: set = set()

    try:
        # Initial state
        incidents = db.scalars(select(Incident).order_by(Incident.detected_at.desc())).all()
        known_incident_ids = {i.id for i in incidents}

        await websocket.send_text(json.dumps({
            "type": "initial",
            "active_incidents": sum(1 for i in incidents if i.status not in ("CLOSED", "VERIFIED_RESOLVED")),
            "total_incidents": len(incidents),
            "recent": [_serialize_incident(i) for i in incidents[:5]],
        }))

        while True:
            await asyncio.sleep(3)

            all_incidents = db.scalars(
                select(Incident).order_by(Incident.detected_at.desc())
            ).all()

            new_ones = [i for i in all_incidents if i.id not in known_incident_ids]
            if new_ones:
                for inc in new_ones:
                    await websocket.send_text(json.dumps({
                        "type": "new_incident",
                        "incident": _serialize_incident(inc),
                    }))
                known_incident_ids.update(i.id for i in new_ones)

            # Send periodic stats update
            active = sum(1 for i in all_incidents if i.status not in ("CLOSED", "VERIFIED_RESOLVED"))
            await websocket.send_text(json.dumps({
                "type": "stats",
                "active_incidents": active,
                "total_incidents": len(all_incidents),
            }))

    except WebSocketDisconnect:
        pass
    finally:
        db.close()
