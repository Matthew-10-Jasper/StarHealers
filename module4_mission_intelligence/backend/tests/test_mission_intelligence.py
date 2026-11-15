import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.session import Base, get_db
from app.main import app
from app.models.entities import MissionStateEntity, EnvironmentalObservationEntity
from app.schemas.enums import (
    OperationalState, DataSource, GravityEnvironment, DeviationSeverity, QualityStatus, CommStatus
)
from app.schemas.mission_profile import MissionProfile, CommunicationCharacteristics
from app.schemas.observation import ObservationCreate
from app.schemas.context import (
    MissionContextResponse, ActualMissionContext, CommunicationContext, EnvironmentStatus, DataQualityContext,
    ContextTransitionRequest, ContextUpdateRequest
)
from app.services.profile_manager import MissionProfileManager
from app.services.environment_manager import ActualEnvironmentManager
from app.services.deviation_engine import MissionDeviationEngine
from app.services.contingency_manager import ContingencyStateManager
from app.services.reconfiguration_engine import ContextReconfigurationEngine
from app.services.constraints_manager import MissionConstraintsManager
from app.integrations.contracts import generate_standard_context_contract
from app.integrations.mock_consumers import (
    MockModule1HealthAdapter, MockModule3TriageAdapter, MockModule5SimulationAdapter
)

# Test SQLite in-memory database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

# ==============================================================================
# 1. MISSION PROFILES TESTS
# ==============================================================================

def test_load_mission_profiles():
    mgr = MissionProfileManager()
    profiles = mgr.list_profiles()
    assert len(profiles) >= 3
    ids = [p.mission_id for p in profiles]
    assert "ISS_EXPEDITION_LEO" in ids
    assert "ARTEMIS_BASECAMP_LUNAR" in ids
    assert "ARES_VOYAGER_MARS" in ids

def test_scientific_gravity_distinctions():
    mgr = MissionProfileManager()
    iss = mgr.get_profile("ISS_EXPEDITION_LEO")
    moon = mgr.get_profile("ARTEMIS_BASECAMP_LUNAR")
    mars = mgr.get_profile("ARES_VOYAGER_MARS")

    # ISS is microgravity
    assert iss.gravity_environment == GravityEnvironment.MICROGRAVITY
    assert iss.gravity_value_g < 0.01

    # Lunar surface is lunar gravity (~0.166g)
    assert moon.gravity_environment == GravityEnvironment.LUNAR_GRAVITY
    assert abs(moon.gravity_value_g - 0.166) < 0.01

    # Mars Transit is microgravity
    assert mars.gravity_environment == GravityEnvironment.MICROGRAVITY

def test_invalid_profile_rejection():
    mgr = MissionProfileManager()
    with pytest.raises(Exception):
        # Missing required fields like destination and communication_characteristics
        mgr.register_profile({"mission_id": "INVALID_MISSION"})

def test_mission_profile_versioning():
    mgr = MissionProfileManager()
    mars = mgr.get_profile("ARES_VOYAGER_MARS")
    assert mars.configuration_version is not None
    assert mars.configuration_version == "1.0.0"

# ==============================================================================
# 2. ACTUAL ENVIRONMENT TESTS
# ==============================================================================

def test_valid_observation_validation():
    env_mgr = ActualEnvironmentManager()
    obs_in = ObservationCreate(
        parameter="CABIN_PRESSURE",
        value=101.3,
        unit="kPa",
        source=DataSource.SIMULATED
    )
    validated = env_mgr.validate_observation(obs_in)
    assert validated.validation_status is True
    assert validated.quality_status == QualityStatus.VERIFIED

def test_invalid_units_rejection():
    env_mgr = ActualEnvironmentManager()
    obs_in = ObservationCreate(
        parameter="CABIN_PRESSURE",
        value=101.3,
        unit="INVALID_UNIT_XYZ",
        source=DataSource.SIMULATED
    )
    validated = env_mgr.validate_observation(obs_in)
    assert validated.validation_status is False
    assert validated.quality_status == QualityStatus.INVALID_UNIT

def test_stale_observation_detection():
    env_mgr = ActualEnvironmentManager(stale_threshold_seconds=10.0)
    old_time = datetime.now(timezone.utc) - timedelta(seconds=20)
    obs_in = ObservationCreate(
        parameter="RADIATION",
        value=1.5,
        unit="mSv/day",
        timestamp=old_time,
        source=DataSource.TELEMETRY
    )
    validated = env_mgr.validate_observation(obs_in)
    assert validated.validation_status is False
    assert validated.quality_status == QualityStatus.STALE

def test_contradictory_observation_detection():
    env_mgr = ActualEnvironmentManager()
    now = datetime.now(timezone.utc)
    recent_obs = [
        env_mgr.validate_observation(ObservationCreate(
            parameter="CABIN_PRESSURE",
            value=100.0,
            unit="kPa",
            timestamp=now - timedelta(seconds=5)
        ))
    ]
    # Wild jump from 100.0 to 10.0 within 5 seconds without physical ramp
    divergent_obs = ObservationCreate(
        parameter="CABIN_PRESSURE",
        value=10.0,
        unit="kPa",
        timestamp=now
    )
    validated = env_mgr.validate_observation(divergent_obs, recent_history=recent_obs)
    assert validated.validation_status is False
    assert validated.quality_status == QualityStatus.CONTRADICTORY

def test_missing_observation_remains_unknown():
    env_mgr = ActualEnvironmentManager()
    env = EnvironmentStatus()
    new_env, dq = env_mgr.evaluate_environment_state(env, [])
    # Missing radiation or CO2 must remain UNKNOWN
    assert new_env.radiation_status == "UNKNOWN"
    assert new_env.co2_status == "UNKNOWN"
    assert "radiation_status" in dq.unknown_parameters

# ==============================================================================
# 3. DEVIATION ENGINE TESTS
# ==============================================================================

def test_nominal_conditions_no_deviations():
    mgr = MissionProfileManager()
    planned = mgr.get_profile("ARES_VOYAGER_MARS")
    dev_engine = MissionDeviationEngine()
    actual = ActualMissionContext(
        actual_mission_phase=planned.mission_phase,
        gravity_environment=planned.gravity_environment,
        gravity_value_g=planned.gravity_value_g,
        communication=CommunicationContext(status=CommStatus.NOMINAL, expected_delay_seconds=1200.0),
        environment=EnvironmentStatus(
            radiation_status="NOMINAL",
            cabin_pressure_status="NOMINAL",
            co2_status="NOMINAL",
            life_support_status="NOMINAL",
            habitat_status="NOMINAL"
        ),
        data_quality=DataQualityContext(overall_status=QualityStatus.VERIFIED)
    )
    deviations = dev_engine.evaluate_deviations(planned, actual)
    assert len(deviations) == 0

def test_mission_phase_deviation():
    mgr = MissionProfileManager()
    planned = mgr.get_profile("ARES_VOYAGER_MARS")
    dev_engine = MissionDeviationEngine()
    actual = ActualMissionContext(
        actual_mission_phase="OFF_NOMINAL_ABORT_TRAJECTORY",
        gravity_environment=planned.gravity_environment,
        gravity_value_g=planned.gravity_value_g,
        communication=CommunicationContext(status=CommStatus.NOMINAL),
        environment=EnvironmentStatus(),
        data_quality=DataQualityContext(overall_status=QualityStatus.VERIFIED)
    )
    deviations = dev_engine.evaluate_deviations(planned, actual)
    phase_devs = [d for d in deviations if d.deviation_name == "MISSION_PHASE_DEVIATION"]
    assert len(phase_devs) == 1
    assert phase_devs[0].severity == DeviationSeverity.CRITICAL

def test_communication_loss_deviation():
    mgr = MissionProfileManager()
    planned = mgr.get_profile("ARES_VOYAGER_MARS")
    dev_engine = MissionDeviationEngine()
    actual = ActualMissionContext(
        actual_mission_phase=planned.mission_phase,
        gravity_environment=planned.gravity_environment,
        gravity_value_g=planned.gravity_value_g,
        communication=CommunicationContext(status=CommStatus.BLACKOUT, earth_reachable=False),
        environment=EnvironmentStatus(),
        data_quality=DataQualityContext(overall_status=QualityStatus.VERIFIED)
    )
    deviations = dev_engine.evaluate_deviations(planned, actual)
    blackout_devs = [d for d in deviations if d.deviation_name == "COMMUNICATION_BLACKOUT"]
    assert len(blackout_devs) == 1
    assert blackout_devs[0].severity == DeviationSeverity.CRITICAL

def test_life_support_degradation_deviation():
    mgr = MissionProfileManager()
    planned = mgr.get_profile("ARES_VOYAGER_MARS")
    dev_engine = MissionDeviationEngine()
    actual = ActualMissionContext(
        actual_mission_phase=planned.mission_phase,
        gravity_environment=planned.gravity_environment,
        gravity_value_g=planned.gravity_value_g,
        communication=CommunicationContext(status=CommStatus.NOMINAL),
        environment=EnvironmentStatus(life_support_status="DEGRADED"),
        data_quality=DataQualityContext(overall_status=QualityStatus.VERIFIED)
    )
    deviations = dev_engine.evaluate_deviations(planned, actual)
    lss_devs = [d for d in deviations if d.deviation_name == "LIFE_SUPPORT_DEGRADATION"]
    assert len(lss_devs) == 1
    assert lss_devs[0].severity == DeviationSeverity.WARNING

# ==============================================================================
# 4. CONTINGENCY STATE MANAGER TESTS
# ==============================================================================

def test_valid_state_transitions():
    cm = ContingencyStateManager()
    # NOMINAL -> DEGRADED
    valid, msg = cm.validate_transition(OperationalState.NOMINAL, OperationalState.DEGRADED, "Scrubber warning", {})
    assert valid is True

    # DEGRADED -> CONTINGENCY
    valid, msg = cm.validate_transition(OperationalState.DEGRADED, OperationalState.CONTINGENCY, "Cabin breach detected", {})
    assert valid is True

    # CONTINGENCY -> RECOVERY
    valid, msg = cm.validate_transition(OperationalState.CONTINGENCY, OperationalState.RECOVERY, "Breach patched", {})
    assert valid is True

    # RECOVERY -> NOMINAL with verified evidence
    valid, msg = cm.validate_transition(
        OperationalState.RECOVERY,
        OperationalState.NOMINAL,
        "Pressure stable for 12 hours",
        evidence={"sensor_check": "PASS", "has_active_critical_deviations": False}
    )
    assert valid is True

def test_invalid_state_transition_rejection():
    cm = ContingencyStateManager()
    # Direct jump from CONTINGENCY to NOMINAL without RECOVERY
    valid, msg = cm.validate_transition(
        OperationalState.CONTINGENCY,
        OperationalState.NOMINAL,
        "Attempting jump without recovery",
        {}
    )
    assert valid is False
    assert "Illegal state transition" in msg

def test_return_to_nominal_requires_evidence():
    cm = ContingencyStateManager()
    # RECOVERY -> NOMINAL without evidence payload
    valid, msg = cm.validate_transition(
        OperationalState.RECOVERY,
        OperationalState.NOMINAL,
        "Trying to return without proof",
        evidence={}
    )
    assert valid is False
    assert "requires verified evidence" in msg

def test_return_to_nominal_blocked_by_critical_deviation():
    cm = ContingencyStateManager()
    valid, msg = cm.validate_transition(
        OperationalState.RECOVERY,
        OperationalState.NOMINAL,
        "Trying to return while critical deviation exists",
        evidence={"has_active_critical_deviations": True}
    )
    assert valid is False
    assert "active critical mission deviations remain" in msg

# ==============================================================================
# 5. CONTEXT RECONFIGURATION TESTS
# ==============================================================================

def test_context_reconfiguration_increments_version():
    reconfig = ContextReconfigurationEngine()
    current = app_state_mock_context()
    update_req = ContextUpdateRequest(
        actual_mission_phase="OFF_NOMINAL_TRAJECTORY_CORRECTION",
        reason="Trajectory burn deviation",
        evidence={"burn_delta_v": -4.2}
    )
    updated, audit = reconfig.apply_reconfiguration(current, update_req)
    assert updated.context_version == current.context_version + 1
    assert updated.actual_mission_phase == "OFF_NOMINAL_TRAJECTORY_CORRECTION"
    assert audit.context_version == updated.context_version
    # Unaffected attributes preserved
    assert updated.mission_id == current.mission_id
    assert updated.gravity_environment == current.gravity_environment

# ==============================================================================
# 6. INTEGRATION CONTRACT AND MOCK CONSUMERS TESTS
# ==============================================================================

def test_context_integration_contract_generation():
    current = app_state_mock_context()
    contract = generate_standard_context_contract(current)
    assert contract["contract_name"] == "STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT"
    assert contract["schema_version"] == "1.0.0"
    assert "communication" in contract
    assert "environment" in contract
    assert "data_quality" in contract
    assert "MODULE_1_ASTRONAUT_HEALTH_MONITORING" in contract["consumer_targets"]

def test_mock_consumers_delivery():
    current = app_state_mock_context()
    contract = generate_standard_context_contract(current)

    m1_adapter = MockModule1HealthAdapter()
    res1 = m1_adapter.deliver_mission_context(contract)
    assert res1["status"] == "ACCEPTED"
    assert res1["calibrated_gravity"] == current.gravity_environment.value

    m3_adapter = MockModule3TriageAdapter()
    res3 = m3_adapter.deliver_mission_context(contract)
    assert res3["status"] == "ACCEPTED"
    assert "triage_environmental_modifiers" in res3

    m5_adapter = MockModule5SimulationAdapter()
    res5 = m5_adapter.deliver_mission_context(contract)
    assert res5["status"] == "ACCEPTED"

# ==============================================================================
# 7. API ENDPOINTS & PERSISTENCE RESTARTS TESTS
# ==============================================================================

from app.api.endpoints import (
    get_health, list_missions, get_current_mission_context, select_mission_profile,
    get_mission_by_id, ingest_observations, request_state_transition, update_mission_context,
    get_mission_history, get_mission_hazards, get_context_integration_contract,
    deliver_context_to_mock_consumer, run_simulator_scenario
)
from fastapi import HTTPException
from app.schemas.mission_profile import MissionSelectRequest
from app.schemas.observation import ObservationBatchCreate

def test_api_health():
    res = get_health()
    assert res["status"] == "HEALTHY"
    assert res["mode"] == "STANDALONE_INDEPENDENT"

def test_api_list_missions():
    res = list_missions()
    assert len(res) >= 3

def test_api_get_current_mission(db_session):
    res = get_current_mission_context(db=db_session)
    assert res.mission_id is not None
    assert res.operational_state == OperationalState.NOMINAL

def test_api_select_mission(db_session):
    req = MissionSelectRequest(mission_id="ARTEMIS_BASECAMP_LUNAR")
    res = select_mission_profile(req=req, db=db_session)
    assert res.mission_id == "ARTEMIS_BASECAMP_LUNAR"
    assert res.gravity_environment == GravityEnvironment.LUNAR_GRAVITY

def test_api_observations_ingestion(db_session):
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa", source=DataSource.SIMULATED),
            ObservationCreate(parameter="CO2_CONCENTRATION", value=1.2, unit="mmHg", source=DataSource.SIMULATED)
        ]
    )
    res = ingest_observations(batch=batch, db=db_session)
    assert res["processed_count"] == 2
    assert res["verified_count"] == 2

def test_api_transition_endpoint(db_session):
    req = ContextTransitionRequest(
        target_state=OperationalState.DEGRADED,
        reason="Elevated CO2 scrubber degradation",
        evidence={"sensor": "CO2_SCRUBBER"}
    )
    res = request_state_transition(req=req, db=db_session)
    assert res.operational_state == OperationalState.DEGRADED

def test_api_history_survives_restart(db_session):
    # Select mission
    select_mission_profile(MissionSelectRequest(mission_id="ISS_EXPEDITION_LEO"), db=db_session)
    
    # Transition state
    request_state_transition(
        ContextTransitionRequest(target_state=OperationalState.DEGRADED, reason="Solar flare alert"),
        db=db_session
    )

    # Ingest observation
    ingest_observations(
        ObservationBatchCreate(observations=[ObservationCreate(parameter="RADIATION", value=2.2, unit="mSv/day")]),
        db=db_session
    )

    # Simulate database session closure and restart by opening a new session to the same database
    new_session = TestingSessionLocal()
    try:
        history = get_mission_history(mission_id=None, db=new_session)
        assert len(history["audit_events"]) > 0
        assert len(history["state_transitions"]) > 0

        # Verify active context restored cleanly
        current = get_current_mission_context(db=new_session)
        assert current.mission_id == "ISS_EXPEDITION_LEO"
        assert current.operational_state == OperationalState.DEGRADED
    finally:
        new_session.close()

def test_api_simulator_scenario(db_session):
    res = run_simulator_scenario(scenario="LIFE_SUPPORT", db=db_session)
    assert res["data_source"] == "SIMULATED"
    assert res["ingestion_result"]["detected_deviations_count"] > 0

def test_api_get_mission_history_routing_regression(db_session):
    """Regression test: Proves GET /missions/history routes to history rather than /missions/{mission_id}."""
    # 1. Verify Starlette route table resolves /missions/history to get_mission_history
    scope = {'type': 'http', 'method': 'GET', 'path': '/missions/history'}
    matched_endpoint = None
    for route in app.routes:
        match, _ = route.matches(scope)
        if match.value == 2:  # Match.FULL
            matched_endpoint = route.name
            break
    assert matched_endpoint == "get_mission_history", f"Expected 'get_mission_history' but matched '{matched_endpoint}'"

    # 2. Verify invoking get_mission_history returns historical data structures
    history = get_mission_history(mission_id=None, db=db_session)
    assert isinstance(history, dict)
    assert "audit_events" in history
    assert "state_transitions" in history
    assert "limit" in history
    assert "offset" in history

def test_api_get_mission_by_id():
    """Verifies GET /missions/{mission_id} returns valid mission profile and 404 for missing IDs."""
    # 1. Verify Starlette route table resolves /missions/ISS_EXPEDITION_LEO to get_mission_by_id
    scope = {'type': 'http', 'method': 'GET', 'path': '/missions/ISS_EXPEDITION_LEO'}
    matched_endpoint = None
    for route in app.routes:
        match, _ = route.matches(scope)
        if match.value == 2:
            matched_endpoint = route.name
            break
    assert matched_endpoint == "get_mission_by_id", f"Expected 'get_mission_by_id' but matched '{matched_endpoint}'"

    # 2. Test valid IDs
    iss_profile = get_mission_by_id("ISS_EXPEDITION_LEO")
    assert iss_profile.mission_id == "ISS_EXPEDITION_LEO"
    assert iss_profile.destination == "LOW_EARTH_ORBIT"

    mars_profile = get_mission_by_id("ARES_VOYAGER_MARS")
    assert mars_profile.mission_id == "ARES_VOYAGER_MARS"
    assert mars_profile.destination == "MARS"

    # 3. Test non-existent ID raises 404
    with pytest.raises(HTTPException) as excinfo:
        get_mission_by_id("NON_EXISTENT_ID_999")
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail.lower()

# Helper mock context generator
def app_state_mock_context():
    return MissionContextResponse(
        context_id="CTX_TEST_01",
        context_version=1,
        mission_id="ARES_VOYAGER_MARS",
        planned_profile="ARES_VOYAGER_MARS",
        actual_mission_phase="HELIOCENTRIC_MARS_TRANSIT",
        operational_state=OperationalState.NOMINAL,
        gravity_environment=GravityEnvironment.MICROGRAVITY,
        gravity_value_g=0.0001,
        communication=CommunicationContext(status=CommStatus.NOMINAL, expected_delay_seconds=1200.0),
        environment=EnvironmentStatus(
            radiation_status="NOMINAL",
            cabin_pressure_status="NOMINAL",
            co2_status="NOMINAL",
            life_support_status="NOMINAL",
            habitat_status="NOMINAL"
        ),
        data_quality=DataQualityContext(overall_status=QualityStatus.VERIFIED)
    )
