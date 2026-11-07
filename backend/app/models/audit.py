import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Any
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. inventories, orders, invoices
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False) # INVENTORY_COMPENSATION, INVOICE_VOIDED, STATUS_RESUMED
    actor_type: Mapped[str] = mapped_column(String(50), default="SYSTEM_RECOVERY_ENGINE") # SYSTEM_RECOVERY_ENGINE, ADMIN_USER
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    before_state: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    after_state: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
