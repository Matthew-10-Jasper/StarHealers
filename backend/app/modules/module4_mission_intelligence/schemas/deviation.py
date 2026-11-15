from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import uuid
from app.modules.module4_mission_intelligence.schemas.enums import DeviationSeverity, DataSource

class MissionDeviation(BaseModel):
    deviation_id: str = Field(default_factory=lambda: f"DEV-{uuid.uuid4().hex[:8].upper()}")
    deviation_name: str
    category: str
    expected_condition: str
    actual_condition: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    severity: DeviationSeverity
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: DataSource = DataSource.SIMULATED
    confirmation_status: str = Field(default="CONFIRMED", description="UNCONFIRMED, CONFIRMED, RESOLVED")
    resolved: bool = Field(default=False)
    resolution_notes: Optional[str] = None

