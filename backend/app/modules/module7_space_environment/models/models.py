from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.modules.module7_space_environment.database.session import Base

class HazardAlertModel(Base):
    __tablename__ = "hazard_alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    hazard_type = Column(String(32), index=True, nullable=False)  # RADIATION, CO2, CABIN_PRESSURE, COMPOSITE
    severity = Column(String(16), index=True, nullable=False)     # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    source_module = Column(String(32), default="MODULE_7", nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String(64), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class EnvironmentalSnapshotModel(Base):
    __tablename__ = "environmental_snapshots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    snapshot_id = Column(String(64), unique=True, index=True, nullable=False)
    cumulative_dose_msv = Column(Float, nullable=False)
    radiation_rate_msv_h = Column(Float, nullable=False)
    co2_percent = Column(Float, nullable=False)
    co2_mmhg = Column(Float, nullable=False)
    cabin_pressure_kpa = Column(Float, nullable=True)
    composite_risk_score = Column(Float, nullable=False)
    risk_status = Column(String(32), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

