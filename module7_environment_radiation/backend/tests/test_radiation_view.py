import pytest
from app.services.m5_consumer import get_radiation_overview

def test_radiation_gcr_and_limits():
    rad = get_radiation_overview(mission_hours=24.0, has_active_spe=False)
    assert rad.cumulative_dose_msv > 0.0
    assert rad.current_dose_rate_msv_h > 0.0
    assert rad.thirty_day_limit_pct < 100.0
    assert rad.career_limit_pct < 100.0
    assert len(rad.time_series) == 25
    assert rad.provenance == "SIMULATED_MODULE5_ENGINE"

def test_radiation_spe_spike():
    rad_spe = get_radiation_overview(mission_hours=72.0, has_active_spe=True)
    assert rad_spe.active_spe_event is True
    assert rad_spe.spe_component_msv > 0.0
    assert rad_spe.cumulative_dose_msv > rad_spe.gcr_component_msv

