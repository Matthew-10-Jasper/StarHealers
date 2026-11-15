import pytest
from app.integrations.module123_adapter import module123_adapter
from app.integrations.module4_adapter import module4_adapter
from app.integrations.module5_adapter import module5_adapter
from app.integrations.module6_adapter import module6_adapter
from app.integrations.module7_adapter import module7_adapter

def test_module123_adapter_data():
    astros = module123_adapter.get_astronauts()
    assert len(astros) >= 4
    first_id = astros[0]["astronaut_id"]
    
    astro = module123_adapter.get_astronaut(first_id)
    assert astro is not None
    assert astro["name"] is not None

    alerts = module123_adapter.get_triage_alerts()
    assert isinstance(alerts, list)

def test_module4_adapter_data():
    ctx = module4_adapter.get_current_context()
    assert "mission_id" in ctx
    assert "operational_state" in ctx
    assert "gravity_environment" in ctx

    missions = module4_adapter.list_missions()
    assert len(missions) >= 3

def test_module5_adapter_engines():
    scenarios = module5_adapter.get_scenarios()
    assert len(scenarios) >= 5

    # Run radiation engine through adapter without duplication
    rad_res = module5_adapter.run_radiation_simulation(total_duration_hours=24.0, has_spe=False)
    assert rad_res["final_cumulative_dose_msv"] > 0

    # Run CO2 engine through adapter
    co2_res = module5_adapter.run_co2_simulation(total_duration_hours=24.0, scrubber_active=True)
    assert co2_res["final_co2_mmhg"] > 0

def test_module6_adapter_cognitive_readiness():
    readiness = module6_adapter.get_readiness("ASTRO-01")
    assert 0.0 <= readiness["overall_readiness_score"] <= 100.0
    assert "factor_weights" in readiness
    assert "non_clinical_disclaimer" in readiness

def test_module7_adapter_composite_risk():
    risk = module7_adapter.get_composite_risk()
    assert 0.0 <= risk["overall_risk_index"] <= 100.0
    assert risk["operational_risk_level"] in ["NOMINAL", "MONITORING_REQUIRED", "CONTINGENCY", "EMERGENCY"]
    
    rad = module7_adapter.get_radiation()
    assert rad["cumulative_dose_msv"] > 0
    assert rad["provenance"] == "SIMULATED_MODULE5_ENGINE"
