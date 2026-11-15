import pytest
from app.services.scenario_manager import ScenarioManager
from app.schemas.scenario import SimulationScenarioConfig
from app.schemas.radiation import RadiationInput
from app.schemas.co2 import CO2Input
from app.schemas.sleep import SleepInput

def test_predefined_scenarios_registration():
    """All 5 predefined scenarios exist with valid parameters."""
    mgr = ScenarioManager()
    scenarios = mgr.list_scenarios()
    assert len(scenarios) >= 5

    ids = [s.scenario_id for s in scenarios]
    assert "NORMAL_MISSION" in ids
    assert "SOLAR_RADIATION_EVENT" in ids
    assert "CO2_REMOVAL_FAILURE" in ids
    assert "SLEEP_DISRUPTION" in ids
    assert "COMBINED_SPACE_HAZARD" in ids

def test_custom_scenario_creation():
    """Custom scenario with user-configured parameters can be registered and retrieved."""
    mgr = ScenarioManager()
    custom = SimulationScenarioConfig(
        scenario_id="CUSTOM_DEEP_SPACE_EXTENDED",
        scenario_name="Extended Deep Space Scenario",
        description="Testing custom configuration registration",
        radiation_params=RadiationInput(initial_dose_rate_msv_day=2.2, shielding_factor=0.3),
        co2_params=CO2Input(crew_count=6, cabin_volume_m3=200.0),
        sleep_params=SleepInput(baseline_sleep_hours=7.5),
        mission_duration_hours=72.0
    )
    registered = mgr.register_scenario(custom)
    assert registered.scenario_id == "CUSTOM_DEEP_SPACE_EXTENDED"

    retrieved = mgr.get_scenario("CUSTOM_DEEP_SPACE_EXTENDED")
    assert retrieved is not None
    assert retrieved.radiation_params.initial_dose_rate_msv_day == 2.2
    assert retrieved.co2_params.crew_count == 6

