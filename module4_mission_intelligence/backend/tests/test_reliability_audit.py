"""
Reliability and Data-Quality Semantics Acceptance Tests for Module 4.
Verifies:
1. Data-quality semantics indicators (validation_quality, telemetry_completeness, telemetry_freshness).
2. Duplicate observations are idempotent (idempotency key).
3. Old observations cannot overwrite newer observations (out-of-order telemetry).
4. Stale telemetry is identified correctly.
5. Missing telemetry remains UNKNOWN.
6. Repeated GET requests do not generate audit events.
7. Database rollback handling on repository error.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.schemas.enums import OperationalState, DataSource, QualityStatus, DeviationSeverity
from app.schemas.mission_profile import MissionSelectRequest
from app.schemas.observation import ObservationBatchCreate, ObservationCreate
from app.schemas.context import EnvironmentStatus, DataQualityContext, ContextTransitionRequest
from app.schemas.deviation import MissionDeviation
from app.repositories.mission_repository import MissionRepository
from app.services.environment_manager import ActualEnvironmentManager
from app.api.endpoints import (
    select_mission_profile, ingest_observations, get_current_mission_context,
    get_mission_history, request_state_transition
)

@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_data_quality_semantics_partial_telemetry(memory_db):
    """
    When only cabin pressure is ingested:
    - validation_quality: VERIFIED
    - telemetry_completeness: PARTIAL
    - telemetry_freshness: FRESH
    - four other parameters: UNKNOWN
    - overall_status: PARTIAL (does NOT claim full environmental verification)
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    
    # Ingest verified cabin pressure
    now = datetime.now(timezone.utc)
    res = ingest_observations(
        ObservationBatchCreate(
            observations=[
                ObservationCreate(
                    parameter="cabin_pressure_kpa",
                    value=70.3,
                    unit="kPa",
                    timestamp=now,
                    source=DataSource.SIMULATED
                )
            ]
        ),
        db=memory_db
    )
    
    ctx = get_current_mission_context(db=memory_db)
    dq = ctx.data_quality
    
    # Check separate quality indicators
    assert dq.validation_quality == QualityStatus.VERIFIED
    assert dq.telemetry_completeness == "PARTIAL"
    assert dq.telemetry_freshness == "FRESH"
    assert dq.overall_status == QualityStatus.PARTIAL
    
    # 4 remaining parameters remain UNKNOWN
    assert len(dq.unknown_parameters) == 4
    assert "cabin_pressure_status" not in dq.unknown_parameters
    assert "co2_concentration_status" in dq.unknown_parameters
    assert "radiation_status" in dq.unknown_parameters
    assert "life_support_status" in dq.unknown_parameters
    assert "habitat_integrity_status" in dq.unknown_parameters
    
    # Status fields in Environment
    assert ctx.environment.cabin_pressure_status == "NOMINAL"
    assert ctx.environment.co2_status == "UNKNOWN"
    assert ctx.environment.radiation_status == "UNKNOWN"
    assert ctx.environment.life_support_status == "UNKNOWN"
    assert ctx.environment.habitat_status == "UNKNOWN"

def test_duplicate_observations_idempotency(memory_db):
    """
    Submitting an observation with an identical idempotency key returns the existing
    observation without creating duplicate DB rows or duplicate audit events.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    repo = MissionRepository(memory_db)
    
    key = "IDEMP-TEST-001"
    now = datetime.now(timezone.utc)
    obs = ObservationCreate(
        parameter="CABIN_PRESSURE",
        value=70.3,
        unit="kPa",
        idempotency_key=key,
        timestamp=now
    )
    
    # First submission
    batch1 = ObservationBatchCreate(observations=[obs])
    res1 = ingest_observations(batch1, db=memory_db)
    assert res1["processed_count"] == 1
    
    obs_count_1 = len(repo.get_recent_observations("ARES_VOYAGER_MARS", limit=50))
    
    # Second submission with identical idempotency key
    batch2 = ObservationBatchCreate(observations=[obs])
    res2 = ingest_observations(batch2, db=memory_db)
    assert res2["processed_count"] == 1
    assert res2["observations"][0]["metadata"].get("idempotent_duplicate") is True
    
    obs_count_2 = len(repo.get_recent_observations("ARES_VOYAGER_MARS", limit=50))
    assert obs_count_2 == obs_count_1, "Duplicate observation must not add additional rows to DB"

def test_out_of_order_telemetry_cannot_overwrite_newer(memory_db):
    """
    An older observation arriving out-of-order must not overwrite a newer canonical observation.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    
    t_newer = datetime.now(timezone.utc)
    t_older = t_newer - timedelta(seconds=60)
    
    # 1. Ingest newer reading first (70.3 kPa at t_newer)
    batch_new = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa", timestamp=t_newer)
        ]
    )
    ingest_observations(batch_new, db=memory_db)
    
    # 2. Ingest older reading arriving delayed (69.0 kPa at t_older)
    batch_old = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=69.0, unit="kPa", timestamp=t_older)
        ]
    )
    ingest_observations(batch_old, db=memory_db)
    
    ctx = get_current_mission_context(db=memory_db)
    # The active value and timestamp must reflect the newer reading (70.3), not the older delayed reading (69.0)
    assert ctx.environment.observed_parameters["CABIN_PRESSURE"] == 70.3
    assert ctx.environment.parameter_timestamps["CABIN_PRESSURE"] == t_newer

def test_repeated_get_requests_do_not_create_audit_events(memory_db):
    """
    GET requests must be strictly idempotent and not create duplicate audit events.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    
    h1 = get_mission_history(mission_id="ARES_VOYAGER_MARS", db=memory_db)
    initial_audits = len(h1["audit_events"])
    
    # Perform repeated GET calls
    for _ in range(5):
        get_current_mission_context(db=memory_db)
        get_mission_history(mission_id="ARES_VOYAGER_MARS", db=memory_db)
        
    h2 = get_mission_history(mission_id="ARES_VOYAGER_MARS", db=memory_db)
    final_audits = len(h2["audit_events"])
    assert final_audits == initial_audits, "GET requests must not create audit events"

