from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid

from app.modules.module5_hazard_simulation.schemas.enums import SimulationStatus, EngineType, HazardSeverity, ProvenanceType
from app.modules.module5_hazard_simulation.schemas.radiation import RadiationStepOutput, RadiationSimulationResult
from app.modules.module5_hazard_simulation.schemas.co2 import CO2StepOutput, CO2SimulationResult
from app.modules.module5_hazard_simulation.schemas.sleep import SleepStepOutput, SleepSimulationResult
from app.modules.module5_hazard_simulation.schemas.scenario import SimulationScenarioConfig

class SimulationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    timestamp_hour: float
    event_type: str  # e.g. "THRESHOLD_WARNING", "SCENARIO_PHASE", "SYSTEM_STATUS"
    engine: str
    severity: HazardSeverity
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CombinedStepReading(BaseModel):
    step_index: int
    simulation_time_hours: float
    mission_day: float
    radiation: Optional[RadiationStepOutput] = None
    co2: Optional[CO2StepOutput] = None
    sleep: Optional[SleepStepOutput] = None
    overall_hazard_level: HazardSeverity = HazardSeverity.NOMINAL
    active_events: List[SimulationEvent] = Field(default_factory=list)

class SimulationSessionCreate(BaseModel):
    scenario_id: Optional[str] = "NORMAL_MISSION"
    engine_type: EngineType = EngineType.COMBINED
    mission_duration_hours: Optional[float] = 168.0
    timestep_hours: Optional[float] = 1.0
    custom_scenario: Optional[SimulationScenarioConfig] = None

class SimulationSessionResponse(BaseModel):
    session_id: str
    scenario_id: str
    scenario_name: str
    engine_type: EngineType
    status: SimulationStatus
    current_time_hours: float
    total_duration_hours: float
    timestep_hours: float
    latest_reading: Optional[CombinedStepReading] = None
    events_count: int = 0
    created_at: datetime
    updated_at: datetime

class SimulationResultsResponse(BaseModel):
    session_id: str
    scenario_id: str
    engine_type: EngineType
    status: SimulationStatus
    total_steps: int
    mission_duration_hours: float
    radiation_summary: Optional[RadiationSimulationResult] = None
    co2_summary: Optional[CO2SimulationResult] = None
    sleep_summary: Optional[SleepSimulationResult] = None
    timeline: List[CombinedStepReading] = Field(default_factory=list)
    events: List[SimulationEvent] = Field(default_factory=list)
    provenance: ProvenanceType = ProvenanceType.SIMULATED

class Module4ExportPayload(BaseModel):
    source_session_id: str
    simulation_timestamp_hours: float
    observations: List[Dict[str, Any]]
    suggested_operational_state: Optional[str] = None
    provenance: str = "SIMULATED"

