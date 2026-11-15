from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text
)
from app.modules.module4_mission_intelligence.database.session import Base

class MissionStateEntity(Base):
    __tablename__ = "mission_state"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    context_id = Column(String(64), nullable=False, index=True)
    context_version = Column(Integer, nullable=False, default=1)
    planned_profile_id = Column(String(64), nullable=False)
    actual_mission_phase = Column(String(128), nullable=False)
    operational_state = Column(String(32), nullable=False, default="NOMINAL")
    gravity_environment = Column(String(64), nullable=False)
    gravity_value_g = Column(Float, nullable=False, default=0.0001)
    
    # Serialized JSON structures
    communication_json = Column(Text, nullable=False, default="{}")
    environment_json = Column(Text, nullable=False, default="{}")
    data_quality_json = Column(Text, nullable=False, default="{}")
    planned_context_json = Column(Text, nullable=False, default="{}")
    
    data_source = Column(String(32), nullable=False, default="SIMULATED")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class EnvironmentalObservationEntity(Base):
    __tablename__ = "environmental_observations"

    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(String(64), unique=True, nullable=False, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    parameter = Column(String(64), nullable=False, index=True)
    value_raw = Column(Text, nullable=False)
    unit = Column(String(32), nullable=True)
    canonical_value = Column(Float, nullable=True)
    canonical_unit = Column(String(32), nullable=True)
    idempotency_key = Column(String(64), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    source = Column(String(32), nullable=False, default="SIMULATED")
    quality_status = Column(String(32), nullable=False, default="UNVERIFIED")
    validation_status = Column(Boolean, nullable=False, default=False)
    metadata_json = Column(Text, nullable=False, default="{}")

class MissionDeviationEntity(Base):
    __tablename__ = "mission_deviations"

    id = Column(Integer, primary_key=True, index=True)
    deviation_id = Column(String(64), unique=True, nullable=False, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    deviation_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    expected_condition = Column(String(256), nullable=False)
    actual_condition = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False) # INFO, WARNING, CRITICAL, UNKNOWN
    evidence_json = Column(Text, nullable=False, default="{}")
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    source = Column(String(32), nullable=False, default="SIMULATED")
    confirmation_status = Column(String(32), nullable=False, default="CONFIRMED")
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_notes = Column(Text, nullable=True)

class StateTransitionEntity(Base):
    __tablename__ = "state_transitions"

    id = Column(Integer, primary_key=True, index=True)
    transition_id = Column(String(64), unique=True, nullable=False, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    from_state = Column(String(32), nullable=False)
    to_state = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False, default="{}")
    operator_id = Column(String(64), nullable=False, default="MISSION_CONTROLLER")
    is_valid = Column(Boolean, nullable=False, default=True)
    context_version = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class AuditLogEntity(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False, default="{}")
    operator_id = Column(String(64), nullable=False, default="SYSTEM")
    context_version = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class QueuedReportEntity(Base):
    __tablename__ = "queued_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(64), unique=True, nullable=False, index=True)
    mission_id = Column(String(64), nullable=False, index=True)
    report_type = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=False)
    delivery_status = Column(String(32), nullable=False, default="LOCALLY_GENERATED")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    transmitted_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledgement_id = Column(String(64), nullable=True)

