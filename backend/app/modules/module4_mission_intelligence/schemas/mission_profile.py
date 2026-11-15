from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.modules.module4_mission_intelligence.schemas.enums import GravityEnvironment, DataSource

class CommunicationCharacteristics(BaseModel):
    link_type: str = Field(..., description="Link type, e.g. TDRSS or DSN")
    expected_delay_seconds: float = Field(ge=0.0, description="One-way light-time delay in seconds")
    bandwidth_mbps: float = Field(gt=0.0, description="Available bandwidth in megabits per second")
    reachability: str = Field(..., description="Reachability mode")

class ParameterBound(BaseModel):
    min: float
    max: float
    target: float

class MissionProfile(BaseModel):
    mission_id: str = Field(..., description="Unique identifier for the mission profile")
    mission_name: str = Field(..., description="Human-readable title")
    destination: str = Field(..., description="Primary destination, e.g. LOW_EARTH_ORBIT, MOON, MARS")
    mission_phase: str = Field(..., description="Planned phase of operation")
    gravity_environment: GravityEnvironment = Field(..., description="Gravity classification")
    gravity_value_g: float = Field(ge=0.0, description="Effective gravitational acceleration in g (Earth=1.0)")
    habitat_type: str = Field(..., description="Pressurized habitat structure classification")
    expected_duration_days: Optional[int] = Field(None, ge=1, description="Planned mission duration in days")
    communication_characteristics: CommunicationCharacteristics
    environmental_monitoring_categories: List[str] = Field(default_factory=list)
    nominal_bounds: Dict[str, ParameterBound] = Field(default_factory=dict)
    configuration_version: str = Field(default="1.0.0")
    data_source: DataSource = Field(default=DataSource.SIMULATED)

class MissionSelectRequest(BaseModel):
    mission_id: str
    operator_id: Optional[str] = "MISSION_CONTROLLER_AUTO"
    preserve_previous_observations: bool = True

