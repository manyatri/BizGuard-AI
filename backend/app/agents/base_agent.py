"""
Base agent class — all BizGuard AI agents inherit from this.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.incidents import Incident, AgentTask, AgentMessage


def _utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class AgentOutput:
    incident_id: str
    agent_id: str
    agent_role: str
    task_performed: str
    findings: Dict[str, Any]
    content_markdown: str          # human-readable findings (markdown)
    recommended_next_action: str
    execution_status: str          # COMPLETED | FAILED | SKIPPED
    llm_generated: bool = False
    error: Optional[str] = None


class BaseAgent:
    """
    Abstract base for all BizGuard AI specialist agents.
    Subclasses override `run()`.
    """
    agent_id: str = "base-agent"
    agent_role: str = "BaseAgent"
    message_type: str = "ANALYSIS"

    def run(self, db: Session, incident: Incident, context: Dict[str, Any]) -> AgentOutput:
        raise NotImplementedError

    def _get_or_create_task(self, db: Session, incident_id: str, prompt_spec: str) -> AgentTask:
        """Creates an AgentTask record for this agent run."""
        task = AgentTask(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            agent_role=self.agent_role,
            prompt_spec=prompt_spec,
            status="RUNNING",
            started_at=_utc(),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def _complete_task(self, db: Session, task: AgentTask, output: AgentOutput):
        """Marks AgentTask as completed and writes an AgentMessage."""
        task.status = "COMPLETED" if output.execution_status == "COMPLETED" else "FAILED"
        task.completed_at = _utc()
        task.output_artifacts = output.findings

        msg = AgentMessage(
            id=str(uuid.uuid4()),
            incident_id=output.incident_id,
            sender_agent=self.agent_id,
            channel_source="BizGuard-AgentBus",
            message_type=self.message_type,
            content=output.content_markdown,
            metadata_json={
                "agent_role": self.agent_role,
                "task_id": task.id,
                "llm_generated": output.llm_generated,
                "recommended_next_action": output.recommended_next_action,
            },
            created_at=_utc(),
        )
        db.add(msg)
        db.commit()
