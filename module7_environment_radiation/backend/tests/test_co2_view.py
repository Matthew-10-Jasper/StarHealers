import pytest
from app.services.m5_consumer import get_co2_overview

def test_co2_nominal_operation():
    co2 = get_co2_overview(mission_hours=24.0, scrubber_degraded=False)
    assert co2.status == "NOMINAL"
    assert co2.ppco2_mmhg < 3.0
    assert co2.scrubber_efficiency_pct > 90.0
    assert len(co2.time_series) == 25

def test_co2_scrubber_degradation():
    co2_deg = get_co2_overview(mission_hours=72.0, scrubber_degraded=True)
    assert co2_deg.status in ["ELEVATED", "CRITICAL"]
    assert co2_deg.ppco2_mmhg >= 2.0
    assert co2_deg.scrubber_efficiency_pct < 80.0
    assert co2_deg.accumulated_exposure_hours > 0.0

