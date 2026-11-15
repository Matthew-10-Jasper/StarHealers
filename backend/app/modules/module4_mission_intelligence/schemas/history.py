from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import uuid
from app.modules.module4_mission_intelligence.schemas.enums import OperationalState, ReportDeliveryStatus

class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"AUD-{uuid.uuid4().hex[:8].upper()}")
    event_type: str
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    operator_id: str = "SYSTEM"
    context_version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StateTransitionRecord(BaseModel):
    transition_id: str = Field(default_factory=lambda: f"TRN-{uuid.uuid4().hex[:8].upper()}")
    from_state: OperationalState
    to_state: OperationalState
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    operator_id: str = "MISSION_CONTROLLER"
    is_valid: bool = True
    context_version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QueuedReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:8].upper()}")
    report_type: str
    payload: Dict[str, Any]
    delivery_status: ReportDeliveryStatus = ReportDeliveryStatus.LOCALLY_GENERATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transmitted_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledgement_id: Optional[str] = None

