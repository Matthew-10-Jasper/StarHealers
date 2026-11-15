from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.modules.module5_hazard_simulation.schemas.enums import HazardSeverity, ProvenanceType, RadiationEnvironment

class RadiationInput(BaseModel):
    initial_dose_rate_msv_day: float = Field(1.8, ge=0.0, le=500.0, description="Baseline ambient GCR radiation dose rate in mSv/day")
    mission_duration_hours: float = Field(168.0, gt=0.0, le=8760.0, description="Total simulation duration in hours")
    timestep_hours: float = Field(1.0, gt=0.0, le=24.0, description="Discrete simulation step size in hours")
    shielding_factor: float = Field(0.20, ge=0.0, le=0.99, description="Vehicle/shelter radiation shielding attenuation fraction [0=none, 0.99=maximum]")
    environment: RadiationEnvironment = Field(RadiationEnvironment.GCR_DEEP_SPACE, description="Radiation environment classification")
    
    # Radiation event profile (SPE - Solar Particle Event)
    spe_active: bool = Field(False, description="Whether a solar particle event is simulated")
    spe_start_hour: float = Field(24.0, ge=0.0, description="Hour when SPE starts")
    spe_duration_hours: float = Field(48.0, gt=0.0, description="Duration of SPE in hours")
    spe_peak_intensity_msv_day: float = Field(25.0, ge=0.0, le=5000.0, description="Peak additional dose rate during SPE in mSv/day")
    spe_profile_type: str = Field("LOGNORMAL", description="Shape of event profile: LOGNORMAL, WEIBULL, or STEP")

class RadiationStepOutput(BaseModel):
    step_index: int
    simulation_time_hours: float
    mission_day: float
    incident_dose_rate_msv_day: float
    absorbed_dose_rate_msv_day: float
    cumulative_dose_msv: float
    shielding_factor: float
    spe_active: bool
    severity: HazardSeverity
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RadiationSimulationResult(BaseModel):
    engine: str = "RADIATION"
    scenario_id: Optional[str] = None
    parameters: RadiationInput
    timesteps: List[RadiationStepOutput]
    final_cumulative_dose_msv: float
    max_dose_rate_msv_day: float
    time_above_warning_hours: float
    time_above_critical_hours: float
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    model_assumptions: str = (
        "Linear exponential attenuation for shielding. GCR modeled as constant background; "
        "SPE modeled as parameterized intensity curve. Doses are effective dose equivalent in mSv."
    )

