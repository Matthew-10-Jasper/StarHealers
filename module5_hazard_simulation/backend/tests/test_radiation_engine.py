import pytest
from app.schemas.enums import HazardSeverity, ProvenanceType, RadiationEnvironment
from app.schemas.radiation import RadiationInput
from app.services.engines.radiation_engine import SpaceRadiationEngine

def test_normal_gcr_exposure():
    """Nominal deep space GCR background produces constant dose rate and linear cumulative dose."""
    params = RadiationInput(
        initial_dose_rate_msv_day=1.8,
        mission_duration_hours=24.0,
        timestep_hours=1.0,
        shielding_factor=0.0,
        spe_active=False
    )
    engine = SpaceRadiationEngine(params)
    res = engine.run_full_simulation("TEST_NORMAL")

    assert res.engine == "RADIATION"
    assert res.provenance == ProvenanceType.SIMULATED
    # In 24 hours (1 day) with 1.8 mSv/day and 0 shielding, cumulative dose should be ~1.8 mSv
    assert pytest.approx(res.final_cumulative_dose_msv, rel=1e-2) == 1.8
    assert res.max_dose_rate_msv_day == 1.8
    assert res.time_above_warning_hours == 0.0
    assert res.time_above_critical_hours == 0.0

def test_shielding_attenuation():
    """Shielding factor reduces absorbed dose rate proportionally."""
    # 50% shielding
    params_shielded = RadiationInput(
        initial_dose_rate_msv_day=2.0,
        mission_duration_hours=24.0,
        timestep_hours=1.0,
        shielding_factor=0.50,
        spe_active=False
    )
    engine = SpaceRadiationEngine(params_shielded)
    res = engine.run_full_simulation("TEST_SHIELDED")

    # With 50% shielding, effective dose rate should be 1.0 mSv/day, cumulative in 1 day ~ 1.0 mSv
    assert pytest.approx(res.max_dose_rate_msv_day, rel=1e-2) == 1.0
    assert pytest.approx(res.final_cumulative_dose_msv, rel=1e-2) == 1.0

def test_spe_radiation_spike():
    """A solar particle event causes a significant dose rate spike and crosses critical threshold."""
    params_spe = RadiationInput(
        initial_dose_rate_msv_day=1.8,
        mission_duration_hours=72.0,
        timestep_hours=1.0,
        shielding_factor=0.10,
        spe_active=True,
        spe_start_hour=12.0,
        spe_duration_hours=24.0,
        spe_peak_intensity_msv_day=35.0,
        spe_profile_type="LOGNORMAL"
    )
    engine = SpaceRadiationEngine(params_spe)
    res = engine.run_full_simulation("TEST_SPE")

    # Peak dose rate should reach > 20 mSv/day (Critical)
    assert res.max_dose_rate_msv_day > 20.0
    assert res.time_above_warning_hours > 0.0
    assert res.time_above_critical_hours > 0.0
    assert res.final_cumulative_dose_msv > (1.8 * 3.0)  # Much higher than background alone

def test_weibull_profile_execution():
    """Weibull profile runs successfully and produces deterministic radiation curves."""
    params_weibull = RadiationInput(
        initial_dose_rate_msv_day=1.5,
        mission_duration_hours=48.0,
        timestep_hours=1.0,
        spe_active=True,
        spe_start_hour=10.0,
        spe_duration_hours=20.0,
        spe_peak_intensity_msv_day=20.0,
        spe_profile_type="WEIBULL"
    )
    engine = SpaceRadiationEngine(params_weibull)
    res = engine.run_full_simulation("TEST_WEIBULL")
    assert len(res.timesteps) == 49
    assert res.max_dose_rate_msv_day > 1.5

