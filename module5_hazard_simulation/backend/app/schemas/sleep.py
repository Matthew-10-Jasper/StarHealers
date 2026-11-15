from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.schemas.enums import HazardSeverity, ProvenanceType

class SleepInput(BaseModel):
    baseline_sleep_hours: float = Field(8.0, ge=4.0, le=12.0, description="Nominal daily sleep requirement in hours")
    initial_sleep_debt_hours: float = Field(0.0, ge=0.0, le=40.0, description="Pre-existing cumulative sleep deficit in hours")
    nominal_sleep_hours: float = Field(7.5, ge=2.0, le=12.0, description="Standard scheduled sleep per mission day in hours")
    recovery_efficiency: float = Field(0.75, ge=0.1, le=1.0, description="Fraction of surplus sleep converted into debt reduction")
    mission_days: int = Field(14, ge=1, le=365, description="Total simulation duration in mission days")
    
    # Sleep disruption scenario
    disruption_active: bool = Field(False, description="Whether acute sleep disruption is active")
    disruption_start_day: int = Field(3, ge=1, description="Mission day when disruption begins")
    disruption_duration_days: int = Field(4, ge=1, description="Number of consecutive disrupted days")
    disrupted_sleep_hours: float = Field(4.0, ge=0.0, le=12.0, description="Sleep duration during disrupted days in hours")
    
    # Explicit daily schedule override if specified
    custom_daily_schedule: Optional[List[float]] = Field(None, description="Explicit array of daily sleep hours")

class SleepStepOutput(BaseModel):
    step_index: int
    mission_day: int
    required_sleep_hours: float
    actual_sleep_hours: float
    daily_deficit_hours: float
    daily_recovery_hours: float
    cumulative_debt_hours: float
    disruption_active: bool
    severity: HazardSeverity
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SleepSimulationResult(BaseModel):
    engine: str = "SLEEP"
    scenario_id: Optional[str] = None
    parameters: SleepInput
    timesteps: List[SleepStepOutput]
    peak_sleep_debt_hours: float
    final_sleep_debt_hours: float
    total_deficit_accumulated_hours: float
    total_recovery_hours: float
    days_above_warning: int
    days_above_critical: int
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    model_assumptions: str = (
        "Linear deficit accumulation with sub-unity recovery efficiency (0.75). "
        "Non-clinical mathematical heuristic; does not diagnose cognitive impairment."
    )

