from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class AstronautSchema(BaseModel):
    astronaut_id: str
    name: str
    role: str
    callsign: Optional[str] = None
    baseline_sleep_hours: float = 8.0
    baseline_hrv_rmssd: float = 52.0

class SleepStatusResponse(BaseModel):
    astronaut_id: str
    total_sleep_hours_last_24h: float
    recommended_sleep_hours: float = 8.0
    daily_deficit_hours: float
    cumulative_sleep_debt_hours: float
    sleep_debt_trend: str  # "STABLE", "ACCUMULATING", "RECOVERING"
    sleep_disruption_active: bool
    data_source: str = "SIMULATED_MODULE5"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CircadianPhasePoint(BaseModel):
    hour: float
    alertness_score: float  # 0 to 100
    biological_phase: str   # "SLEEP_GATE", "MAINTENANCE_ZONE", "CIRCADIAN_TROUGH", "PEAK_ALERTNESS"

class CircadianRhythmResponse(BaseModel):
    astronaut_id: str
    mission_elapsed_hours: float
    mission_day: int
    local_mission_hour: float  # 0.0 to 24.0
    current_phase: str
    circadian_alignment_index: float  # 0.0 (misaligned) to 1.0 (optimal)
    alertness_estimate: float  # 0 to 100
    potential_disruption: bool
    disruption_notes: Optional[str] = None
    alertness_curve_24h: List[CircadianPhasePoint] = Field(default_factory=list)
    model_provenance: str = "ESTIMATED_TWO_PROCESS_CIRCADIAN_MODEL"

class FatigueAssessmentResponse(BaseModel):
    astronaut_id: str
    fatigue_level: str  # "NORMAL", "ELEVATED", "HIGH", "UNRELIABLE"
    fatigue_score: float  # 0 to 100
    heart_rate_bpm: Optional[float] = None
    hrv_rmssd_ms: Optional[float] = None
    sleep_deficit_hours: float
    cumulative_debt_hours: float
    stress_index: Optional[float] = None
    reliable_data: bool = True
    assessment_notes: str
    calculation_breakdown: Dict[str, Any] = Field(default_factory=dict)

class StressTrendPoint(BaseModel):
    timestamp_hour: float
    stress_score: float  # 0 to 100
    sleep_debt_hours: float
    hrv_rmssd: Optional[float] = None

class StressMonitoringResponse(BaseModel):
    astronaut_id: str
    current_stress_score: Optional[float] = None  # None indicates NO DATA
    stress_level: str  # "LOW", "MODERATE", "HIGH", "NO_DATA"
    historical_trend: List[StressTrendPoint] = Field(default_factory=list)
    sleep_debt_stress_correlation: Optional[float] = 0.72
    hrv_fatigue_correlation: Optional[float] = -0.68
    data_available: bool = True

class CognitiveReadinessResponse(BaseModel):
    astronaut_id: str
    overall_readiness_score: float  # 0 to 100
    rating: str  # "OPTIMAL_PERFORMANCE", "QUALIFIED_MONITORED", "DEGRADED_RESTRICTED", "IMPAIRED"
    sleep_component: float       # 0 to 100
    circadian_component: float   # 0 to 100
    fatigue_component: float     # 0 to 100
    stress_component: float      # 0 to 100
    pvt_component: float         # 0 to 100
    factor_weights: Dict[str, float]
    data_completeness: float     # 0.0 to 1.0
    explanation: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    non_clinical_disclaimer: str = (
        "Non-clinical decision-support metric based on mathematical fatigue heuristics. "
        "Not a diagnostic determination of medical fitness for flight duty."
    )

class PVTTrialCreate(BaseModel):
    trial_number: int
    stimulus_delay_ms: float
    reaction_time_ms: float

class PVTSessionSubmitRequest(BaseModel):
    astronaut_id: str
    trials: List[PVTTrialCreate]

class PVTTrialResponse(BaseModel):
    trial_number: int
    stimulus_delay_ms: float
    reaction_time_ms: float
    is_lapse: bool
    is_false_start: bool

class PVTSessionResponse(BaseModel):
    session_id: str
    astronaut_id: str
    trials_count: int
    avg_reaction_time_ms: float
    median_reaction_time_ms: float
    lapses_count: int
    false_starts_count: int
    slowest_reaction_ms: float
    fastest_reaction_ms: float
    performance_rating: str
    completed_at: datetime
    trials: List[PVTTrialResponse] = Field(default_factory=list)

class PVTHistoryResponse(BaseModel):
    astronaut_id: str
    total_sessions_completed: int
    historical_avg_reaction_time_ms: float
    sessions: List[PVTSessionResponse] = Field(default_factory=list)

