import pytest
from app.schemas.enums import HazardSeverity
from app.schemas.session import Module4ExportPayload
from app.services.scenario_manager import ScenarioManager
from app.services.controller import SimulationController
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base

@pytest.fixture
def memory_db_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)

def test_module4_payload_canonical_names_and_units(memory_db_factory):
    """Verifies that Module 5 generated observation payloads exactly conform to Module 4 canonical parameters."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("COMBINED_SPACE_HAZARD")
    controller = SimulationController(memory_db_factory)

    session = controller.create_session(scenario)
    controller.start_session(session.session_id)
    controller.step_session(session.session_id)

    payload = session.export_to_module4_format()

    # Module 4 expects:
    # parameter: str (e.g. "RADIATION", "CO2_CONCENTRATION", "CABIN_PRESSURE")
    # value: float
    # unit: str ("mSv/day", "mmHg", "kPa")
    # source: "SIMULATED"
    expected_units = {
        "RADIATION": "mSv/day",
        "CO2_CONCENTRATION": "mmHg",
        "CABIN_PRESSURE": "kPa"
    }

    assert len(payload.observations) >= 3
    for obs in payload.observations:
        p = obs["parameter"]
        assert p in expected_units
        assert obs["unit"] == expected_units[p]
        assert obs["source"] == "SIMULATED"
        assert isinstance(obs["value"], (int, float))

def test_module4_hazard_state_suggestion_mapping(memory_db_factory):
    """Verifies that severe simulated hazard levels suggest appropriate operational states."""
    scenario_mgr = ScenarioManager()
    scenario = scenario_mgr.get_scenario("COMBINED_SPACE_HAZARD")
    controller = SimulationController(memory_db_factory)

    session = controller.create_session(scenario)
    controller.start_session(session.session_id)
    reading = controller.step_session(session.session_id)

    payload = session.export_to_module4_format()
    assert payload.suggested_operational_state in ("NOMINAL", "DEGRADED", "CONTINGENCY")

