import pytest
from app.schemas.enums import HazardSeverity, ProvenanceType
from app.schemas.co2 import CO2Input
from app.services.engines.co2_engine import SpacecraftCO2Engine

def test_co2_equilibrium_balance():
    """Under nominal conditions, CO2 scrubber removal balances generation, maintaining low steady state."""
    params = CO2Input(
        cabin_volume_m3=150.0,
        initial_co2_mmhg=1.0,
        crew_count=4,
        co2_generation_rate_per_crew_l_h=18.0,      # 72 L/h generation
        nominal_scrubber_capacity_l_h=80.0,         # 80 L/h capacity at 1.0 mmHg
        baseline_removal_efficiency=1.0,
        mission_duration_hours=48.0,
        timestep_hours=1.0,
        failure_active=False
    )
    engine = SpacecraftCO2Engine(params)
    res = engine.run_full_simulation("TEST_EQUILIBRIUM")

    # Final CO2 should remain nominal (< 2.0 mmHg)
    assert res.final_co2_mmhg < 2.0
    assert res.time_above_warning_hours == 0.0
    assert res.time_above_critical_hours == 0.0
    assert res.provenance == ProvenanceType.SIMULATED

def test_co2_scrubber_failure_accumulation():
    """Scrubber failure causes rapid accumulation of CO2 crossing warning and critical thresholds."""
    params_failure = CO2Input(
        cabin_volume_m3=100.0,
        initial_co2_mmhg=1.0,
        crew_count=4,
        co2_generation_rate_per_crew_l_h=20.0,      # 80 L/h generation
        nominal_scrubber_capacity_l_h=80.0,
        baseline_removal_efficiency=1.0,
        mission_duration_hours=72.0,
        timestep_hours=1.0,
        failure_active=True,
        failure_start_hour=10.0,
        failure_duration_hours=40.0,
        failure_removal_efficiency=0.05             # 95% loss of scrubber efficiency
    )
    engine = SpacecraftCO2Engine(params_failure)
    res = engine.run_full_simulation("TEST_FAILURE")

    # Peak CO2 should exceed warning (3.0 mmHg) and critical (5.0 mmHg)
    assert res.peak_co2_mmhg > 5.0
    assert res.peak_co2_ppm > 6500.0
    assert res.time_above_warning_hours > 0.0
    assert res.time_above_critical_hours > 0.0

def test_co2_unit_conversions():
    """Validates volume fraction, partial pressure (mmHg), and ppm conversions."""
    params = CO2Input(cabin_pressure_kpa=101.325)
    engine = SpacecraftCO2Engine(params)

    # At 101.325 kPa, cabin pressure is ~760 mmHg
    # 7.6 mmHg should be exactly 1% = 10,000 ppm
    frac = engine.mmhg_to_volume_fraction(7.6)
    assert pytest.approx(frac, rel=1e-2) == 0.01
    ppm = frac * 1e6
    assert pytest.approx(ppm, rel=1e-2) == 10000.0
    mmhg_back = engine.volume_fraction_to_mmhg(frac)
    assert pytest.approx(mmhg_back, rel=1e-2) == 7.6

