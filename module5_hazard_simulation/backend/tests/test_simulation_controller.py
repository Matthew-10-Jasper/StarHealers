import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.schemas.enums import SimulationStatus, EngineType, HazardSeverity
from app.services.scenario_manager import ScenarioManager
from app.services.controller import SimulationController

@pytest.fixture
def memory_db_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session

def test_controller_session_lifecycle(memory_db_factory):
    """Verifies complete session lifecycle: create -> start -> step -> pause -> resume -> reset."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("NORMAL_MISSION")
    controller = SimulationController(memory_db_factory)

    # 1. Create
    session = controller.create_session(scenario, engine_type=EngineType.COMBINED)
    assert session.status == SimulationStatus.IDLE
    assert session.current_time_hours == 0.0

    # 2. Start
    started = controller.start_session(session.session_id)
    assert started.status == SimulationStatus.RUNNING

    # 3. Step
    reading = controller.step_session(session.session_id)
    assert reading.step_index == 0
    assert reading.simulation_time_hours == 0.0
    assert reading.radiation is not None
    assert reading.co2 is not None
    assert reading.sleep is not None

    # Step again
    reading2 = controller.step_session(session.session_id)
    assert reading2.step_index == 1
    assert reading2.simulation_time_hours == 1.0

    # 4. Pause & Resume
    paused = controller.pause_session(session.session_id)
    assert paused.status == SimulationStatus.PAUSED
    resumed = controller.resume_session(session.session_id)
    assert resumed.status == SimulationStatus.RUNNING

    # 5. Reset
    reset = controller.reset_session(session.session_id)
    assert reset.status == SimulationStatus.IDLE
    assert reset.current_time_hours == 0.0
    assert reset.step_index == 0
    assert len(reset.timeline) == 0

def test_controller_combined_multi_hazard_run_to_end(memory_db_factory):
    """Executes a full multi-stressor simulation run to completion on a synchronized clock."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("COMBINED_SPACE_HAZARD")
    # Truncate duration to 24h for fast unit testing
    scenario.mission_duration_hours = 24.0
    controller = SimulationController(memory_db_factory)

    session = controller.create_session(scenario, engine_type=EngineType.COMBINED, mission_duration_hours=24.0)
    results = controller.run_session_to_end(session.session_id)

    assert results.status == SimulationStatus.COMPLETED
    assert results.total_steps == 25
    assert results.radiation_summary is not None
    assert results.co2_summary is not None
    assert results.sleep_summary is not None
    assert len(results.timeline) == 25

def test_controller_module4_export_payload(memory_db_factory):
    """Verifies that Module 4 export payload accurately extracts simulated observations."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("NORMAL_MISSION")
    controller = SimulationController(memory_db_factory)

    session = controller.create_session(scenario)
    controller.start_session(session.session_id)
    controller.step_session(session.session_id)

    payload = session.export_to_module4_format()
    assert payload.source_session_id == session.session_id
    assert payload.provenance == "SIMULATED"
    assert len(payload.observations) >= 3

    params = {obs["parameter"]: obs["value"] for obs in payload.observations}
    assert "RADIATION" in params
    assert "CO2_CONCENTRATION" in params
    assert "CABIN_PRESSURE" in params

def test_controller_boundary_timestep_inclusion_regression(memory_db_factory):
    """Regression test ensuring that stepping to completion evaluates the final boundary hour."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("NORMAL_MISSION")
    controller = SimulationController(memory_db_factory)

    # 12-hour mission with 1-hour timesteps must produce exactly 13 steps (0 to 12 inclusive)
    session = controller.create_session(scenario, mission_duration_hours=12.0, timestep_hours=1.0)
    controller.start_session(session.session_id)
    
    while session.status != SimulationStatus.COMPLETED:
        controller.step_session(session.session_id)

    assert session.status == SimulationStatus.COMPLETED
    assert len(session.timeline) == 13
    assert session.timeline[0].simulation_time_hours == 0.0
    assert session.timeline[-1].simulation_time_hours == 12.0
    assert session.current_time_hours == 12.0

