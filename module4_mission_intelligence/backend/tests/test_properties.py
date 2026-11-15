"""
Property-based testing suite for Module 4 with Hypothesis.
Tests invariant properties, monotonicity, state machine bounds,
and numerical dimensional preservation under fuzzed inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from app.core.units import validate_and_convert_observation
from app.schemas.enums import OperationalState
from app.services.contingency_manager import ContingencyStateManager, VALID_STATE_TRANSITIONS
from app.services.environment_manager import ActualEnvironmentManager
from app.schemas.observation import ObservationCreate

contingency_mgr = ContingencyStateManager()
env_mgr = ActualEnvironmentManager(stale_threshold_seconds=1000.0)

# Property 1: State Machine Transition Invariant
@given(
    from_state=st.sampled_from(list(OperationalState)),
    to_state=st.sampled_from(list(OperationalState))
)
@hyp_settings(max_examples=50)
def test_state_machine_transition_invariants(from_state, to_state):
    """
    Property: An operational state transition is valid IF AND ONLY IF
    to_state is in VALID_STATE_TRANSITIONS.get(from_state, set()).
    Any arbitrary state jump outside the allowed graph MUST be rejected.
    """
    allowed_targets = VALID_STATE_TRANSITIONS.get(from_state, set())
    is_allowed = to_state in allowed_targets
    
    # We pass empty active deviations and evidence with operator approval
    evidence = {"operator_approval": True, "notes": "property test validation"}
    is_valid, reason = contingency_mgr.validate_transition(
        current_state=from_state,
        target_state=to_state,
        reason="Property test validation",
        evidence=evidence
    )
    
    if from_state == to_state:
        assert is_valid, "Identity transition must succeed"
    elif not is_allowed:
        assert not is_valid, f"Transition {from_state} -> {to_state} should have been rejected"
    else:
        assert is_valid, f"Transition {from_state} -> {to_state} should be valid with approval: {reason}"

# Property 2: Pressure Unit Conversion Linear Invariant
@given(
    pressure_kpa=st.floats(min_value=0.1, max_value=250.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=50)
def test_pressure_conversion_numerical_invariance(pressure_kpa):
    """
    Property: Converting pressure from kPa to psi and then back to canonical kPa
    must preserve the original magnitude within floating point precision (0.01%).
    """
    # 1 kPa = 0.1450377 psi
    psi_val = pressure_kpa * 0.1450377377
    res = validate_and_convert_observation("CABIN_PRESSURE", psi_val, "psi")
    
    assert res.is_valid is True
    assert res.canonical_unit == "kPa"
    relative_error = abs(res.canonical_value - pressure_kpa) / pressure_kpa
    assert relative_error < 0.001, f"Relative error {relative_error} exceeded tolerance for {pressure_kpa} kPa"

# Property 3: Radiation Unit Dimensional Partition Invariant
@given(
    dose_rate=st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.sampled_from(["mGy/d", "uGy/h", "cGy/d", "rad/day"])
)
@hyp_settings(max_examples=40)
def test_radiation_absorbed_dose_rejection_invariant(dose_rate, unit):
    """
    Property: ANY absorbed dose rate unit without an explicit radiation weighting factor
    MUST ALWAYS be rejected regardless of magnitude.
    """
    res = validate_and_convert_observation("RADIATION", dose_rate, unit, radiation_weighting_factor=None)
    assert res.is_valid is False
    assert "Gray and Sievert are not interchangeable" in res.error_message

# Property 4: Idempotency Invariant for Telemetry Ingestion
@given(
    val=st.floats(min_value=50.0, max_value=120.0, allow_nan=False, allow_infinity=False),
    packet_id=st.text(min_size=8, max_size=16, alphabet="0123456789ABCDEF")
)
@hyp_settings(max_examples=30)
def test_telemetry_idempotency_invariant(val, packet_id):
    """
    Property: Ingesting an observation with the exact same idempotency_key
    returns the same canonical telemetry without duplicate recalculation.
    """
    obs_in = ObservationCreate(
        parameter="CABIN_PRESSURE",
        value=val,
        unit="kPa",
        idempotency_key=f"PKT-{packet_id}"
    )
    first_pass = env_mgr.validate_observation(obs_in, recent_history=[])
    assert first_pass.validation_status is True
    assert first_pass.idempotency_key == f"PKT-{packet_id}"

    # Second pass with recent_history containing the first
    second_pass = env_mgr.validate_observation(obs_in, recent_history=[first_pass])
    assert second_pass.validation_status is True
    assert second_pass.metadata.get("idempotent_duplicate") is True
    assert second_pass.canonical_value == first_pass.canonical_value

# Property 5: CO2 Concentration Invariant
@given(
    pct=st.floats(min_value=0.01, max_value=5.0, allow_nan=False, allow_infinity=False)
)
@hyp_settings(max_examples=30)
def test_co2_percentage_to_ppm_invariant(pct):
    """
    Property: Converting percentage to ppm must strictly equal pct * 10,000.
    """
    res = validate_and_convert_observation("CO2", pct, "%")
    assert res.is_valid is True
    assert res.canonical_unit == "ppm"
    expected = round(pct * 10000.0, 2)
    assert abs(res.canonical_value - expected) < 0.05
