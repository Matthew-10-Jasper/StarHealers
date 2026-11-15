"""
Regression tests for Telemetry Reconciliation and Stale Deviation Lifecycle.
Verifies:
1. Old alias observation followed by fresh canonical observation.
2. Canonical and alias entries do not produce duplicate stale streams.
3. A fresh reading clears stale status for its canonical parameter.
4. Old data-quality deviations are reconciled (evidence updated, resolved when complete).
5. Remaining unknown parameters remain visible in data quality context.
6. Historical deviations remain available in audit trail after resolution.
7. Unrelated new observations do not resolve physical safety deviations.
8. Suggested operational state and authorized operational state remain strictly separated.
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
from app.services.environment_manager import ActualEnvironmentManager
from app.services.history_manager import ContextHistoryManager
from app.repositories.mission_repository import MissionRepository
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

def test_alias_superseded_by_canonical_no_duplicates(memory_db):
    """
    Submitting an old alias followed by a fresh canonical observation:
    - observed_parameters contains only CABIN_PRESSURE
    - parameter_timestamps contains only CABIN_PRESSURE
    - stale_parameters does not contain CABIN_PRESSURE_KPA
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    # 1. Old alias observation (simulated 400 seconds ago)
    old_time = datetime.now(timezone.utc) - timedelta(seconds=400)
    batch_old = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=69.5,
                unit="kPa",
                timestamp=old_time,
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch_old, db=memory_db)

    # 2. Fresh canonical observation (now)
    now = datetime.now(timezone.utc)
    batch_fresh = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="CABIN_PRESSURE",
                value=70.3,
                unit="kPa",
                timestamp=now,
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch_fresh, db=memory_db)

    # 3. Verify current context
    ctx = get_current_mission_context(db=memory_db)
    
    # Only canonical parameter must exist
    assert "CABIN_PRESSURE" in ctx.environment.observed_parameters
    assert "CABIN_PRESSURE_KPA" not in ctx.environment.observed_parameters
    assert ctx.environment.observed_parameters["CABIN_PRESSURE"] == 70.3
    
    assert "CABIN_PRESSURE" in ctx.environment.parameter_timestamps
    assert "CABIN_PRESSURE_KPA" not in ctx.environment.parameter_timestamps

    # Stale parameters must not contain alias, and must be empty because CABIN_PRESSURE is fresh
    assert "CABIN_PRESSURE_KPA" not in ctx.data_quality.stale_parameters
    assert "CABIN_PRESSURE" not in ctx.data_quality.stale_parameters
    assert len(ctx.data_quality.stale_parameters) == 0

def test_fresh_reading_clears_stale_status(memory_db):
    """A fresh reading must immediately clear stale status for its canonical parameter."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    env_mgr = ActualEnvironmentManager()

    # 1. Start with an existing observed parameter whose timestamp aged beyond 300s
    old_time = datetime.now(timezone.utc) - timedelta(seconds=400)
    current_env = EnvironmentStatus(
        cabin_pressure_status="NOMINAL",
        observed_parameters={"CABIN_PRESSURE": 70.3},
        parameter_timestamps={"CABIN_PRESSURE": old_time}
    )

    # Evaluating current state without new readings shows parameter is stale
    env_stale, dq_stale = env_mgr.evaluate_environment_state(current_env, [])
    assert "CABIN_PRESSURE" in dq_stale.stale_parameters
    assert dq_stale.overall_status == QualityStatus.STALE

    # 2. Ingest a fresh reading
    now = datetime.now(timezone.utc)
    fresh_obs = ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa", timestamp=now)
    validated_fresh = env_mgr.validate_observation(fresh_obs)
    assert validated_fresh.validation_status is True

    # 3. Evaluating with the fresh observation must clear stale status
    env_fresh, dq_fresh = env_mgr.evaluate_environment_state(env_stale, [validated_fresh])
    assert "CABIN_PRESSURE" not in dq_fresh.stale_parameters
    assert dq_fresh.overall_status != QualityStatus.STALE

def test_data_quality_deviation_evidence_reconciliation(memory_db):
    """
    When cabin pressure is verified, active ENVIRONMENTAL_TELEMETRY_UNKNOWN
    must update its evidence to exclude cabin pressure, while retaining remaining unknown parameters.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    repo = MissionRepository(memory_db)
    history_mgr = ContextHistoryManager(memory_db)

    # Initial state has all 5 parameters unknown -> create initial deviation entity in DB
    init_dev = MissionDeviation(
        deviation_name="ENVIRONMENTAL_TELEMETRY_UNKNOWN",
        category="DATA_QUALITY",
        expected_condition="Verified active telemetry streams",
        actual_condition="Environmental parameters cannot be verified from active telemetry",
        evidence={"unknown_parameters": ["cabin_pressure_status", "co2_concentration_status", "radiation_status", "life_support_status", "habitat_integrity_status"]},
        severity=DeviationSeverity.UNKNOWN
    )
    history_mgr.record_deviation("ARES_VOYAGER_MARS", init_dev)

    # Ingest fresh verified cabin pressure
    ingest_observations(
        ObservationBatchCreate(
            observations=[
                ObservationCreate(parameter="cabin_pressure_kpa", value=70.3, unit="kPa")
            ]
        ),
        db=memory_db
    )

    ctx = get_current_mission_context(db=memory_db)
    # The data quality deviation must still be active (since CO2, Rad, Life Support, Habitat are still unknown)
    dq_devs = [d for d in ctx.active_deviations if d.deviation_name == "ENVIRONMENTAL_TELEMETRY_UNKNOWN"]
    assert len(dq_devs) == 1
    
    # Evidence MUST be updated and must NOT contain cabin_pressure_status
    evidence = dq_devs[0].evidence
    unknown_in_evidence = evidence.get("unknown_parameters", [])
    assert "cabin_pressure_status" not in unknown_in_evidence
    assert "co2_concentration_status" in unknown_in_evidence
    assert "radiation_status" in unknown_in_evidence

def test_full_telemetry_resolves_data_quality_deviation(memory_db):
    """When all core environmental telemetry streams arrive nominal, data-quality deviation is resolved."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    repo = MissionRepository(memory_db)
    history_mgr = ContextHistoryManager(memory_db)

    # Create initial unknown telemetry deviation
    init_dev = MissionDeviation(
        deviation_name="ENVIRONMENTAL_TELEMETRY_UNKNOWN",
        category="DATA_QUALITY",
        expected_condition="Verified streams",
        actual_condition="Streams unknown",
        evidence={"unknown_parameters": ["cabin_pressure_status", "co2_concentration_status"]},
        severity=DeviationSeverity.UNKNOWN
    )
    history_mgr.record_deviation("ARES_VOYAGER_MARS", init_dev)

    # Ingest all 5 required parameters nominal
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa"),
            ObservationCreate(parameter="CO2_CONCENTRATION", value=1.0, unit="mmHg"),
            ObservationCreate(parameter="RADIATION", value=1.8, unit="mSv/day"),
            ObservationCreate(parameter="LIFE_SUPPORT", value="NOMINAL", unit="status"),
            ObservationCreate(parameter="HABITAT_INTEGRITY", value="NOMINAL", unit="status"),
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    ctx = get_current_mission_context(db=memory_db)
    # Active data quality deviation must be resolved
    active_dq = [d for d in ctx.active_deviations if d.category == "DATA_QUALITY"]
    assert len(active_dq) == 0

    # Historical deviation must remain in database marked as resolved
    history = get_mission_history(mission_id="ARES_VOYAGER_MARS", db=memory_db)
    audit_resolved = [a for a in history["audit_events"] if a["event_type"] == "DEVIATION_RESOLVED"]
    assert len(audit_resolved) >= 1

def test_unrelated_observations_do_not_resolve_physical_deviations(memory_db):
    """
    Submitting cabin pressure MUST NOT resolve an active radiation spike or ECLSS failure.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    history_mgr = ContextHistoryManager(memory_db)

    # Ingest severe radiation spike -> creates SEVERE_RADIATION_SPIKE deviation
    rad_dev = MissionDeviation(
        deviation_name="SEVERE_RADIATION_SPIKE",
        category="RADIATION",
        expected_condition="Nominal background radiation",
        actual_condition="Severe radiation spike detected",
        evidence={"radiation_msv_day": 8.5},
        severity=DeviationSeverity.CRITICAL
    )
    history_mgr.record_deviation("ARES_VOYAGER_MARS", rad_dev)

    ctx_rad = get_current_mission_context(db=memory_db)
    assert any(d.deviation_name == "SEVERE_RADIATION_SPIKE" for d in ctx_rad.active_deviations)

    # Now ingest nominal CABIN PRESSURE
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa")
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    # SEVERE_RADIATION_SPIKE MUST REMAIN ACTIVE!
    ctx_after = get_current_mission_context(db=memory_db)
    active_names = [d.deviation_name for d in ctx_after.active_deviations]
    assert "SEVERE_RADIATION_SPIKE" in active_names, "Unrelated cabin pressure telemetry must not resolve radiation deviation"

def test_operational_state_separation_from_suggestion(memory_db):
    """
    suggested_operational_state may be NOMINAL or UNKNOWN, but operational_state must remain
    controlled by explicit transition authorization (cannot automatically become NOMINAL without authorization).
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    # Start in DEGRADED via operator transition
    request_state_transition(
        ContextTransitionRequest(target_state=OperationalState.DEGRADED, reason="Manual operator drill"),
        db=memory_db
    )
    ctx_init = get_current_mission_context(db=memory_db)
    assert ctx_init.operational_state == OperationalState.DEGRADED

    # Ingest a single normal cabin pressure reading
    res = ingest_observations(
        ObservationBatchCreate(
            observations=[
                ObservationCreate(parameter="cabin_pressure_kpa", value=70.3, unit="kPa")
            ]
        ),
        db=memory_db
    )

    # Operational state MUST NOT be automatically switched to NOMINAL
    assert res["operational_state"] == OperationalState.DEGRADED.value
    ctx_final = get_current_mission_context(db=memory_db)
    assert ctx_final.operational_state == OperationalState.DEGRADED

def test_zero_deviations_does_not_trigger_automatic_state_transition(memory_db):
    """
    Having 0 critical and 0 warning deviations must NEVER trigger an autonomous
    state transition to UNKNOWN or NOMINAL.
    """
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    ctx_start = get_current_mission_context(db=memory_db)
    initial_state = ctx_start.operational_state

    # Ingest a verified observation
    res = ingest_observations(
        ObservationBatchCreate(
            observations=[
                ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa")
            ]
        ),
        db=memory_db
    )

    # Check state transitions in history
    history = get_mission_history(mission_id="ARES_VOYAGER_MARS", db=memory_db)
    transitions = history.get("state_transitions", [])
    for t in transitions:
        # No transition reason should mention "0 critical / 0 warning deviations"
        assert "0 critical / 0 warning deviations" not in t.get("reason", "")

    # State must remain whatever was explicitly set, not degraded to UNKNOWN autonomously
    assert res["operational_state"] == initial_state.value
