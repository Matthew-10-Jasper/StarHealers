"""
Comprehensive scientific unit validation test suite for Module 4.
Validates Pint integration, canonical unit conversions, dimensional checking,
and the non-interchangeability of absorbed dose (Gy) and equivalent dose (Sv).
"""

import pytest
from app.core.units import (
    validate_and_convert_observation,
    is_absorbed_dose_rate_unit,
    is_equivalent_dose_rate_unit
)
from app.services.environment_manager import ActualEnvironmentManager
from app.schemas.observation import ObservationCreate
from app.schemas.enums import QualityStatus

@pytest.fixture
def env_manager():
    return ActualEnvironmentManager(stale_threshold_seconds=600.0)

def test_cabin_pressure_conversions():
    """Verify pressure conversions across aerospace units to canonical kPa."""
    # 1 atm = 101.325 kPa
    res_atm = validate_and_convert_observation("CABIN_PRESSURE", 1.0, "atm")
    assert res_atm.is_valid
    assert abs(res_atm.canonical_value - 101.325) < 0.01
    assert res_atm.canonical_unit == "kPa"

    # 14.696 psi = 101.325 kPa
    res_psi = validate_and_convert_observation("CABIN_PRESSURE", 14.6959, "psi")
    assert res_psi.is_valid
    assert abs(res_psi.canonical_value - 101.325) < 0.05
    assert res_psi.canonical_unit == "kPa"

    # 1 bar = 100.0 kPa
    res_bar = validate_and_convert_observation("CABIN_PRESSURE", 1.0, "bar")
    assert res_bar.is_valid
    assert abs(res_bar.canonical_value - 100.0) < 0.01

    # 1013.25 hPa = 101.325 kPa
    res_hpa = validate_and_convert_observation("CABIN_PRESSURE", 1013.25, "hPa")
    assert res_hpa.is_valid
    assert abs(res_hpa.canonical_value - 101.325) < 0.01

def test_negative_cabin_pressure_rejection():
    """Verify that physically impossible negative pressures are rejected."""
    res = validate_and_convert_observation("CABIN_PRESSURE", -5.0, "kPa")
    assert not res.is_valid
    assert "Negative cabin pressure is physically impossible" in res.error_message

def test_incompatible_dimension_for_pressure():
    """Verify rejection of non-pressure dimensions (e.g. length, temperature)."""
    res = validate_and_convert_observation("CABIN_PRESSURE", 100.0, "meters")
    assert not res.is_valid
    assert "Incompatible unit 'meters' for pressure" in res.error_message

def test_co2_conversions():
    """Verify CO2 conversions between ppm, percentage, and partial pressure."""
    # 0.5% = 5000 ppm
    res_pct = validate_and_convert_observation("CO2", 0.5, "%")
    assert res_pct.is_valid
    assert res_pct.canonical_value == 5000.0
    assert res_pct.canonical_unit == "ppm"

    # 3.8 mmHg partial pressure (~5000 ppm at 1 atm)
    res_mmhg = validate_and_convert_observation("CO2", 3.8, "mmHg")
    assert res_mmhg.is_valid
    assert abs(res_mmhg.canonical_value - 5000.0) < 100.0
    assert res_mmhg.canonical_unit == "ppm"

def test_radiation_absorbed_vs_equivalent_distinction():
    """
    CRITICAL SCIENTIFIC PRINCIPLE:
    Gray (absorbed dose) and Sievert (equivalent dose) are physically distinct.
    Direct conversion from Gy/d or uGy/h to mSv/day MUST be rejected without w_R.
    """
    # 1. Absorbed dose without weighting factor -> REJECTED
    res_absorbed = validate_and_convert_observation("RADIATION", 1.5, "mGy/d")
    assert not res_absorbed.is_valid
    assert res_absorbed.quantity_type == "ABSORBED_DOSE_RATE"
    assert "Gray and Sievert are not interchangeable" in res_absorbed.error_message

    # 2. Absorbed dose with explicit weighting factor w_R=2.5 (e.g. space proton flux) -> ACCEPTED
    res_converted = validate_and_convert_observation(
        "RADIATION", 1.0, "mGy/d", radiation_weighting_factor=2.5
    )
    assert res_converted.is_valid
    assert res_converted.canonical_value == 2.5
    assert res_converted.canonical_unit == "mSv/day"
    assert res_converted.metadata["radiation_weighting_factor"] == 2.5

def test_radiation_equivalent_dose_rate_conversions():
    """Verify conversion between equivalent dose rate units (uSv/h -> mSv/day)."""
    # 41.6667 uSv/h * 24h = 1.0 mSv/day
    res = validate_and_convert_observation("RADIATION", 41.6667, "uSv/h")
    assert res.is_valid
    assert abs(res.canonical_value - 1.0) < 0.01
    assert res.canonical_unit == "mSv/day"

def test_gravity_conversions():
    """Verify gravity conversions between m/s^2 and standard g."""
    res = validate_and_convert_observation("GRAVITY", 9.80665, "m/s^2")
    assert res.is_valid
    assert abs(res.canonical_value - 1.0) < 0.001
    assert res.canonical_unit == "g"

    # Lunar gravity: 1.62 m/s^2 -> ~0.165 g
    res_lunar = validate_and_convert_observation("GRAVITY", 1.62, "m/s^2")
    assert res_lunar.is_valid
    assert abs(res_lunar.canonical_value - 0.165) < 0.01
    assert res_lunar.canonical_unit == "g"

def test_communication_delay_conversions():
    """Verify communication delay conversions between minutes and seconds."""
    # 12 minutes (Mars distance) = 720 seconds
    res = validate_and_convert_observation("COMMUNICATION_DELAY", 12.0, "min")
    assert res.is_valid
    assert res.canonical_value == 720.0
    assert res.canonical_unit == "s"

def test_missing_unit_rejection():
    """Verify that dimensional quantities with missing units are rejected."""
    res = validate_and_convert_observation("CABIN_PRESSURE", 101.3, None)
    assert not res.is_valid
    assert "Missing unit" in res.error_message

def test_environment_manager_unit_integration(env_manager):
    """Test full integration in ActualEnvironmentManager."""
    # Ingest pressure in psi
    obs_psi = ObservationCreate(parameter="CABIN_PRESSURE", value=14.6959, unit="psi")
    v_obs = env_manager.validate_observation(obs_psi)
    assert v_obs.validation_status is True
    assert v_obs.quality_status == QualityStatus.VERIFIED
    assert abs(v_obs.canonical_value - 101.325) < 0.05
    assert v_obs.canonical_unit == "kPa"
    assert v_obs.raw_value == 14.6959
    assert v_obs.raw_unit == "psi"

    # Ingest radiation in mGy without w_R -> rejected
    obs_mgy = ObservationCreate(parameter="RADIATION", value=2.0, unit="mGy/d")
    v_mgy = env_manager.validate_observation(obs_mgy)
    assert v_mgy.validation_status is False
    assert v_mgy.quality_status == QualityStatus.INVALID_UNIT
    assert "Gray and Sievert are not interchangeable" in v_mgy.metadata["error"]
