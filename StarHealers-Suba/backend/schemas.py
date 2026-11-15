"""
StarHealers - Pydantic Request & Response Validation Schemas
Ensures strict type validation, allowed enums, unit consistency, and structured error responses.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


# ==========================================
# MISSION SCHEMAS
# ==========================================

class MissionEnvironment(BaseModel):
    cabinCo2: float = Field(..., description="Cabin CO2 percentage (e.g. 0.42%)")
    cabinO2: float = Field(..., description="Cabin O2 percentage (e.g. 20.9%)")
    cabinPressure: float = Field(..., description="Cabin pressure in kPa (e.g. 101.3)")
    ambientTemp: float = Field(..., description="Ambient temperature in Celsius")
    radiationDoseRate: float = Field(..., description="Radiation in mSv/day")
    gravityG: float = Field(..., description="Gravity g-force (0.00 for microgravity)")


class MissionResponse(BaseModel):
    id: str = Field(..., alias="mission_id")
    name: str
    target: str
    phase: str
    commsDelaySec: float
    environment: MissionEnvironment
    status: str

    class Config:
        populate_by_name = True


# ==========================================
# ASTRONAUT SCHEMAS
# ==========================================

class AstronautBaseline(BaseModel):
    restingHr: float
    hrv: float
    bpSystolic: float
    bpDiastolic: float
    spo2: float
    temp: float
    glucose: float
    hydration: float
    stress: float


class AstronautResponse(BaseModel):
    id: str = Field(..., alias="astronaut_id")
    missionId: str = Field(..., alias="mission_id")
    name: str
    role: str
    age: int
    bloodType: str = Field(..., alias="blood_type")
    heightCm: float = Field(..., alias="height_cm")
    weightKg: float = Field(..., alias="weight_kg")
    avatar: Optional[str] = Field(None, alias="avatar_url")
    status: str
    statusReason: Optional[str] = Field(None, alias="status_reason")
    baseline: AstronautBaseline
    bodyRegionStatus: Optional[Dict[str, str]] = None

    class Config:
        populate_by_name = True


# ==========================================
# HEALTH READING SCHEMAS (Module 1 Core Vitals)
# ==========================================

VALID_METRICS = {
    "heartRate", "hrv", "bloodPressure", "spo2",
    "temperature", "glucose", "sleep", "hydration", "stress"
}

VALID_SOURCES = {
    "SIMULATED", "RESEARCH DATASET", "CONNECTED SENSOR", "MANUAL INPUT"
}

VALID_SEVERITIES = {"NORMAL", "WARNING", "CRITICAL", "NO_DATA"}


class HealthReadingCreate(BaseModel):
    reading_id: Optional[str] = None
    metric_name: str
    value: Optional[float] = None
    secondary_value: Optional[float] = None
    unit: str
    source: str = "SIMULATED"
    quality_status: str = "GOOD"
    severity: str = "NORMAL"
    timestamp: Optional[str] = None

    @field_validator("metric_name")
    def validate_metric(cls, v):
        if v not in VALID_METRICS:
            raise ValueError(f"Invalid metric_name '{v}'. Supported: {sorted(list(VALID_METRICS))}")
        return v

    @field_validator("source")
    def validate_source(cls, v):
        if v.upper() not in VALID_SOURCES:
            raise ValueError(f"Invalid data source '{v}'. Must be one of: {sorted(list(VALID_SOURCES))}")
        return v.upper()

    @field_validator("severity")
    def validate_severity(cls, v):
        if v.upper() not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{v}'. Must be one of: {sorted(list(VALID_SEVERITIES))}")
        return v.upper()


class MetricReadingItem(BaseModel):
    value: Optional[float] = None
    secondaryValue: Optional[float] = None
    unit: str
    source: str
    quality: str
    severity: str
    status: str
    timestamp: str


class HistoricalDataPoint(BaseModel):
    time: str
    heartRate: Optional[float] = None
    hrv: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    stress: Optional[float] = None
    source: str = "SIMULATED"
    recorded_at: Optional[str] = None


# ==========================================
# BODY MAP SCHEMAS (Module 2)
# ==========================================

class BodyRegionDetailResponse(BaseModel):
    regionId: str
    label: str
    status: str
    subsystems: List[str]
    associatedMetrics: List[str]
    currentReadings: Dict[str, Any]
    activeAlerts: List[Dict[str, Any]]
    description: str
    disclaimer: str


# ==========================================
# TRIAGE SCHEMAS (Module 3 Rule-Based Engine)
# ==========================================

class ContributingMeasurement(BaseModel):
    name: str
    value: str
    threshold: str
    unit: str
    status: str


class TriageAlertResponse(BaseModel):
    id: str = Field(..., alias="alert_id")
    astronautId: str = Field(..., alias="astronaut_id")
    ruleId: str = Field(..., alias="rule_id")
    title: str
    severity: str
    status: str
    triggerReason: str = Field(..., alias="trigger_reason")
    explanation: str
    contributingMeasurements: List[ContributingMeasurement] = Field(..., alias="contributing_measurements")
    escalationSteps: List[str] = Field(..., alias="escalation_steps")
    timestamp: str
    acknowledgedBy: Optional[str] = Field(None, alias="acknowledged_by")
    resolvedAt: Optional[str] = Field(None, alias="resolved_at")

    class Config:
        populate_by_name = True


class AlertResolutionRequest(BaseModel):
    user_id: str = Field(default="USR-MED-01")
    notes: Optional[str] = None


class TriageEvaluateRequest(BaseModel):
    astronaut_id: str
    heartRate: Optional[float] = None
    hrv: Optional[float] = None
    spo2: Optional[float] = None
    sleep: Optional[float] = None
    stress: Optional[float] = None
    temperature: Optional[float] = None
    hydration: Optional[float] = None


class TriageEvaluateResponse(BaseModel):
    astronautId: str
    evaluatedRulesCount: int
    severity: str
    isAlertTriggered: bool
    triggeredAlerts: List[Dict[str, Any]]
    explanation: str
