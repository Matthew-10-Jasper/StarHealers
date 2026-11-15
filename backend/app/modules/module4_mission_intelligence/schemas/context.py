from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
from app.modules.module4_mission_intelligence.schemas.enums import OperationalState, DataSource, CommStatus, QualityStatus, GravityEnvironment
from app.modules.module4_mission_intelligence.schemas.deviation import MissionDeviation

class PlannedMissionContext(BaseModel):
    profile_id: str
    mission_name: str
    destination: str
    planned_phase: str
    gravity_environment: GravityEnvironment
    gravity_value_g: float
    expected_delay_seconds: float
    expected_duration_days: Optional[int] = None
    habitat_type: str

class CommunicationContext(BaseModel):
    status: CommStatus = CommStatus.NOMINAL
    expected_delay_seconds: float = 1.2
    bandwidth_mbps: float = 50.0
    earth_reachable: bool = True
    queued_reports_count: int = 0
    last_contact_timestamp: Optional[datetime] = None
    last_acknowledged_timestamp: Optional[datetime] = None

class EnvironmentStatus(BaseModel):
    radiation_status: str = "UNKNOWN"
    cabin_pressure_status: str = "UNKNOWN"
    co2_status: str = "UNKNOWN"
    life_support_status: str = "UNKNOWN"
    habitat_status: str = "UNKNOWN"
    observed_parameters: Dict[str, Any] = Field(default_factory=dict)
    parameter_timestamps: Dict[str, datetime] = Field(default_factory=dict)

class DataQualityContext(BaseModel):
    overall_status: QualityStatus = QualityStatus.UNKNOWN
    validation_quality: QualityStatus = QualityStatus.UNKNOWN
    telemetry_completeness: str = "NONE"
    telemetry_freshness: str = "UNKNOWN"
    unknown_parameters: List[str] = Field(default_factory=list)
    stale_parameters: List[str] = Field(default_factory=list)
    contradictory_parameters: List[str] = Field(default_factory=list)
    last_telemetry_timestamp: Optional[datetime] = None

class ActualMissionContext(BaseModel):
    actual_mission_phase: str
    gravity_environment: GravityEnvironment
    gravity_value_g: float
    habitat_status: str = "NOMINAL"
    life_support_status: str = "NOMINAL"
    mission_elapsed_seconds: float = 0.0
    communication: CommunicationContext = Field(default_factory=CommunicationContext)
    environment: EnvironmentStatus = Field(default_factory=EnvironmentStatus)
    data_quality: DataQualityContext = Field(default_factory=DataQualityContext)

class MissionContextResponse(BaseModel):
    context_id: str = Field(default_factory=lambda: f"CTX-{uuid.uuid4().hex[:8].upper()}")
    context_version: int = 1
    mission_id: str
    planned_profile: str
    actual_mission_phase: str
    operational_state: OperationalState = OperationalState.NOMINAL
    gravity_environment: GravityEnvironment
    gravity_value_g: float = 0.0001
    communication: CommunicationContext
    environment: EnvironmentStatus
    data_quality: DataQualityContext
    active_deviations: List[MissionDeviation] = Field(default_factory=list)
    data_source: DataSource = DataSource.SIMULATED
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContextTransitionRequest(BaseModel):
    target_state: OperationalState
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    operator_id: Optional[str] = "MISSION_CONTROLLER"

class ContextUpdateRequest(BaseModel):
    actual_mission_phase: Optional[str] = None
    gravity_environment: Optional[GravityEnvironment] = None
    gravity_value_g: Optional[float] = None
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    operator_id: Optional[str] = "MISSION_CONTROLLER"

