from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AgentMessageRead(BaseModel):
    id: str
    incident_id: str
    sender_agent: str
    channel_source: str
    message_type: str
    content: str
    metadata_json: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AgentMessageCreate(BaseModel):
    sender_agent: str = "Operator"
    channel_source: str = "WarRoom-UI"
    message_type: str = "HUMAN_INTERVENTION"
    content: str
    metadata_json: Optional[dict] = None

class IncidentRead(BaseModel):
    id: str
    incident_code: str
    title: str
    severity: str
    status: str
    detection_rule: str
    affected_order_id: Optional[str] = None
    workflow_execution_id: Optional[str] = None
    root_cause_summary: Optional[str] = None
    blast_radius_analysis: Optional[Any] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    messages: List[AgentMessageRead] = []

    class Config:
        from_attributes = True
