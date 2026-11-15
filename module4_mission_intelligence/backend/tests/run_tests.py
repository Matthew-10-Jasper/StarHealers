import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.api.endpoints import (
    get_health, list_missions, get_current_mission_context, select_mission_profile,
    get_mission_by_id, ingest_observations, request_state_transition, update_mission_context,
    get_mission_history, get_mission_hazards, get_context_integration_contract,
    deliver_context_to_mock_consumer, run_simulator_scenario
)
from app.main import app
from app.schemas.enums import OperationalState, GravityEnvironment, DataSource
from app.schemas.mission_profile import MissionSelectRequest
from app.schemas.observation import ObservationBatchCreate, ObservationCreate
from app.schemas.context import ContextTransitionRequest, ContextUpdateRequest

def main():
    print("--- 1. Testing get_health ---", flush=True)
    h = get_health()
    print("Health:", h["status"], flush=True)
    assert h["status"] == "HEALTHY"

    print("--- 2. Testing list_missions ---", flush=True)
    missions = list_missions()
    print("Missions count:", len(missions), flush=True)
    assert len(missions) >= 3

    print("--- 3. Setting up test in-memory SQLite database ---", flush=True)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    print("Database session ready.", flush=True)

    print("--- 4. Testing get_current_mission_context ---", flush=True)
    ctx = get_current_mission_context(db=db)
    print("Current mission:", ctx.mission_id, ctx.operational_state, flush=True)
    assert ctx.operational_state == OperationalState.NOMINAL

    print("--- 5. Testing select_mission_profile ---", flush=True)
    req = MissionSelectRequest(mission_id="ARTEMIS_BASECAMP_LUNAR")
    ctx_moon = select_mission_profile(req=req, db=db)
    print("Selected moon:", ctx_moon.mission_id, ctx_moon.gravity_environment, flush=True)
    assert ctx_moon.mission_id == "ARTEMIS_BASECAMP_LUNAR"
    assert ctx_moon.gravity_environment == GravityEnvironment.LUNAR_GRAVITY

    print("--- 6. Testing ingest_observations ---", flush=True)
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(parameter="CABIN_PRESSURE", value=70.3, unit="kPa", source=DataSource.SIMULATED),
            ObservationCreate(parameter="CO2_CONCENTRATION", value=1.2, unit="mmHg", source=DataSource.SIMULATED)
        ]
    )
    obs_res = ingest_observations(batch=batch, db=db)
    print("Obs processed:", obs_res["processed_count"], flush=True)
    assert obs_res["processed_count"] == 2

    print("--- 7. Testing request_state_transition ---", flush=True)
    trans_req = ContextTransitionRequest(
        target_state=OperationalState.DEGRADED,
        reason="Elevated CO2 scrubber test",
        evidence={"sensor": "CO2_SCRUBBER"}
    )
    trans_res = request_state_transition(req=trans_req, db=db)
    print("Transition state:", trans_res.operational_state, flush=True)
    assert trans_res.operational_state == OperationalState.DEGRADED

    print("--- 8. Testing update_mission_context (Phase deviation reconfiguration) ---", flush=True)
    up_req = ContextUpdateRequest(
        actual_mission_phase="OFF_NOMINAL_ABORT_TRAJECTORY",
        reason="Trajectory off-nominal burn",
        evidence={"sensor": "IMU"}
    )
    up_res = update_mission_context(req=up_req, db=db)
    print("Reconfigured version:", up_res.context_version, "Phase:", up_res.actual_mission_phase, flush=True)
    assert up_res.context_version >= 2

    print("--- 9. Testing get_mission_history & route resolution ---", flush=True)
    # Regression check: verify /missions/history routes to get_mission_history and NOT get_mission_by_id
    scope_hist = {'type': 'http', 'method': 'GET', 'path': '/missions/history'}
    matched_hist = None
    for r in app.routes:
        match, _ = r.matches(scope_hist)
        if match.value == 2:
            matched_hist = r.name
            break
    print("Route /missions/history matched:", matched_hist, flush=True)
    assert matched_hist == "get_mission_history"

    hist = get_mission_history(mission_id=None, db=db)
    print("History audits:", len(hist["audit_events"]), "transitions:", len(hist["state_transitions"]), flush=True)
    assert len(hist["audit_events"]) > 0

    print("--- 9b. Testing get_mission_by_id & dynamic route resolution ---", flush=True)
    scope_dyn = {'type': 'http', 'method': 'GET', 'path': '/missions/ISS_EXPEDITION_LEO'}
    matched_dyn = None
    for r in app.routes:
        match, _ = r.matches(scope_dyn)
        if match.value == 2:
            matched_dyn = r.name
            break
    print("Route /missions/ISS_EXPEDITION_LEO matched:", matched_dyn, flush=True)
    assert matched_dyn == "get_mission_by_id"

    p_iss = get_mission_by_id("ISS_EXPEDITION_LEO")
    print("Retrieved mission by ID:", p_iss.mission_id, p_iss.destination, flush=True)
    assert p_iss.mission_id == "ISS_EXPEDITION_LEO"
    assert p_iss.destination == "LOW_EARTH_ORBIT"

    print("--- 10. Testing run_simulator_scenario ---", flush=True)
    sim_res = run_simulator_scenario(scenario="LIFE_SUPPORT", db=db)
    print("Sim scenario:", sim_res["scenario"], flush=True)
    assert sim_res["data_source"] == "SIMULATED"

    print("--- 11. Testing get_context_integration_contract ---", flush=True)
    contract = get_context_integration_contract(db=db)
    print("Contract name:", contract["contract_name"], flush=True)
    assert contract["schema_version"] == "1.0.0"

    print("--- 12. Testing deliver_context_to_mock_consumer ---", flush=True)
    deliv = deliver_context_to_mock_consumer(target_module="MODULE_1_ASTRONAUT_HEALTH_MONITORING", db=db)
    print("Delivered:", deliv["status"], flush=True)
    assert deliv["status"] == "DELIVERED"

    print("\nALL 12 BACKEND API & PERSISTENCE TESTS PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    main()
