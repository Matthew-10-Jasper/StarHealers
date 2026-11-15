from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.modules.module5_hazard_simulation.schemas.enums import HazardSeverity, ProvenanceType

class CO2Input(BaseModel):
    cabin_volume_m3: float = Field(150.0, gt=1.0, le=5000.0, description="Total pressurized habitable cabin volume in m^3")
    cabin_pressure_kpa: float = Field(101.3, gt=20.0, le=120.0, description="Ambient cabin pressure in kPa")
    initial_co2_mmhg: float = Field(1.0, ge=0.0, le=50.0, description="Initial CO2 partial pressure in mmHg")
    crew_count: int = Field(4, ge=1, le=20, description="Number of astronauts occupying the cabin")
    co2_generation_rate_per_crew_l_h: float = Field(18.0, gt=0.0, le=100.0, description="CO2 generation rate per person in Liters/hour at STP")
    nominal_scrubber_capacity_l_h: float = Field(80.0, gt=0.0, le=1000.0, description="Maximum nominal CO2 scrubber removal capacity in Liters/hour")
    baseline_removal_efficiency: float = Field(1.0, ge=0.0, le=1.0, description="Baseline operational efficiency of CO2 scrubber [0.0 - 1.0]")
    mission_duration_hours: float = Field(168.0, gt=0.0, le=8760.0, description="Total simulation duration in hours")
    timestep_hours: float = Field(1.0, gt=0.0, le=24.0, description="Simulation timestep in hours")
    
    # Scrubber failure scenario
    failure_active: bool = Field(False, description="Whether a scrubber degradation/failure scenario is simulated")
    failure_start_hour: float = Field(24.0, ge=0.0, description="Hour when scrubber failure begins")
    failure_duration_hours: float = Field(48.0, gt=0.0, description="Duration of scrubber failure in hours")
    failure_removal_efficiency: float = Field(0.15, ge=0.0, le=1.0, description="Degraded scrubber efficiency during failure [0.0 - 1.0]")

class CO2StepOutput(BaseModel):
    step_index: int
    simulation_time_hours: float
    mission_day: float
    co2_partial_pressure_mmhg: float
    co2_ppm: float
    generation_rate_l_h: float
    removal_rate_l_h: float
    scrubber_efficiency: float
    failure_active: bool
    severity: HazardSeverity
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CO2SimulationResult(BaseModel):
    engine: str = "CO2"
    scenario_id: Optional[str] = None
    parameters: CO2Input
    timesteps: List[CO2StepOutput]
    peak_co2_mmhg: float
    peak_co2_ppm: float
    final_co2_mmhg: float
    time_above_warning_hours: float
    time_above_critical_hours: float
    provenance: ProvenanceType = ProvenanceType.SIMULATED
    model_assumptions: str = (
        "Well-mixed single-compartment mass balance dC/dt = (G - R) / V. "
        "Gas converted between STP volume (L/h) and partial pressure (mmHg) via ideal gas law at 21 deg C."
    )

