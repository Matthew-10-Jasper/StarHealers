from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import uuid
from app.modules.module4_mission_intelligence.schemas.enums import DataSource, QualityStatus

class EnvironmentalObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"OBS-{uuid.uuid4().hex[:10].upper()}")
    parameter: str = Field(..., description="Parameter name e.g. CABIN_PRESSURE, CO2, RADIATION, O2")
    value: Any = Field(..., description="Observed numeric or categorical value (canonical where converted)")
    unit: Optional[str] = Field(None, description="Physical unit, e.g. kPa, mmHg, mSv/day, %, g")
    canonical_value: Optional[Any] = Field(None, description="Scientifically converted canonical numeric value")
    canonical_unit: Optional[str] = Field(None, description="Standard canonical physical unit")
    raw_value: Optional[Any] = Field(None, description="Original raw telemetry value before conversion")
    raw_unit: Optional[str] = Field(None, description="Original raw telemetry unit before conversion")
    idempotency_key: Optional[str] = Field(None, description="Unique telemetry packet hash or transmission id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: DataSource = Field(default=DataSource.SIMULATED)
    quality_status: QualityStatus = Field(default=QualityStatus.UNVERIFIED)
    validation_status: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ObservationCreate(BaseModel):
    parameter: str
    value: Any
    unit: Optional[str] = None
    idempotency_key: Optional[str] = None
    timestamp: Optional[datetime] = None
    source: DataSource = DataSource.SIMULATED
    radiation_weighting_factor: Optional[float] = Field(
        None, description="Required for converting absorbed dose (Gy) to equivalent dose (Sv)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ObservationBatchCreate(BaseModel):
    observations: list[ObservationCreate]
