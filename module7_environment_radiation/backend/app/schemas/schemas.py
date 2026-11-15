from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RadiationSeriesPoint(BaseModel):
    hour: float
    gcr_dose_msv: float
    spe_dose_msv: float
    total_cumulative_msv: float
    dose_rate_msv_h: float

class RadiationOverviewResponse(BaseModel):
    cumulative_dose_msv: float
    current_dose_rate_msv_h: float
    gcr_component_msv: float
    spe_component_msv: float
    career_limit_pct: float
    thirty_day_limit_pct: float
    active_spe_event: bool
    shielding_material: str = "ALUMINUM"
    shielding_thickness_g_cm2: float = 10.0
    time_series: List[RadiationSeriesPoint] = Field(default_factory=list)
    provenance: str = "SIMULATED_MODULE5_ENGINE"

class CO2SeriesPoint(BaseModel):
    hour: float
    co2_percent: float
    ppco2_mmhg: float
    scrubber_efficiency_pct: float

class CO2OverviewResponse(BaseModel):
    current_co2_pct: float
    ppco2_mmhg: float
    status: str  # "NOMINAL", "ELEVATED", "CRITICAL"
    scrubber_efficiency_pct: float
    accumulated_exposure_hours: float
    time_series: List[CO2SeriesPoint] = Field(default_factory=list)
    provenance: str = "SIMULATED_MODULE5_ENGINE"

class CabinTelemetryResponse(BaseModel):
    cabin_pressure_kpa: Optional[float] = None
    cabin_pressure_status: str = "DATA_UNAVAILABLE"
    o2_percentage: Optional[float] = None
    o2_status: str = "DATA_UNAVAILABLE"
    temperature_c: Optional[float] = None
    temperature_status: str = "DATA_UNAVAILABLE"
    humidity_pct: Optional[float] = None
    humidity_status: str = "DATA_UNAVAILABLE"
    mission_id: str = "ARES_VOYAGER_MARS"
    operational_state: str = "NOMINAL"
    telemetry_freshness: str = "FRESH"
    completeness: str = "PARTIAL"

class HazardAlertResponse(BaseModel):
    alert_id: str
    hazard_type: str
    severity: str
    message: str
    source_module: str
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: str
    notes: Optional[str] = None

class CompositeRiskResponse(BaseModel):
    overall_risk_index: float  # 0 to 100
    operational_risk_level: str  # "NOMINAL", "MONITORING_REQUIRED", "CONTINGENCY", "EMERGENCY"
    radiation_risk_score: float
    co2_risk_score: float
    cabin_risk_score: float
    active_hazards_count: int
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

