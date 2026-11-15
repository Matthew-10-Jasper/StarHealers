from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.radiation import RadiationInput
from app.schemas.co2 import CO2Input
from app.schemas.sleep import SleepInput

class SimulationScenarioConfig(BaseModel):
    scenario_id: str = Field(..., description="Unique scenario identifier (e.g. SOLAR_RADIATION_EVENT)")
    scenario_name: str = Field(..., description="Human-readable scenario title")
    description: str = Field(..., description="Scientific description of simulation parameters and conditions")
    radiation_params: RadiationInput = Field(default_factory=RadiationInput)
    co2_params: CO2Input = Field(default_factory=CO2Input)
    sleep_params: SleepInput = Field(default_factory=SleepInput)
    mission_duration_hours: float = Field(168.0, gt=0.0, le=8760.0)
    timestep_hours: float = Field(1.0, gt=0.0, le=24.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ScenarioCreateRequest(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    radiation_params: Optional[RadiationInput] = None
    co2_params: Optional[CO2Input] = None
    sleep_params: Optional[SleepInput] = None
    mission_duration_hours: Optional[float] = 168.0
    timestep_hours: Optional[float] = 1.0

