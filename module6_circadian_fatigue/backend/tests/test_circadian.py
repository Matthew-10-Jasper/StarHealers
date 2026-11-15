import pytest
from app.services.circadian_service import (
    compute_circadian_phase,
    compute_alertness_at_hour,
    get_circadian_rhythm
)

def test_circadian_phases():
    assert compute_circadian_phase(3.0) == "CIRCADIAN_TROUGH"
    assert compute_circadian_phase(10.5) == "PEAK_ALERTNESS"
    assert compute_circadian_phase(15.0) == "MAINTENANCE_ZONE"
    assert compute_circadian_phase(23.0) == "SLEEP_GATE"
    assert compute_circadian_phase(1.0) == "SLEEP_GATE"
    assert compute_circadian_phase(7.0) == "NOMINAL_ACTIVE"

def test_alertness_curve_generation():
    response = get_circadian_rhythm(
        astronaut_id="ASTRO-TEST",
        mission_elapsed_hours=48.0,
        sleep_debt_hours=1.0
    )
    assert response.astronaut_id == "ASTRO-TEST"
    assert response.mission_day == 3
    assert len(response.alertness_curve_24h) == 24
    
    # Check that trough hours have lower alertness than peak hours
    trough_pt = next(p for p in response.alertness_curve_24h if p.hour == 4.0)
    peak_pt = next(p for p in response.alertness_curve_24h if p.hour == 14.0)
    assert trough_pt.alertness_score < peak_pt.alertness_score

def test_circadian_alignment_index():
    # Optimal alignment
    res_opt = get_circadian_rhythm("ASTRO-OPT", mission_elapsed_hours=24.0, sleep_debt_hours=0.0, local_shift_hours=0.0)
    assert res_opt.circadian_alignment_index >= 0.9
    assert res_opt.potential_disruption is False

    # Disrupted alignment with high shift and debt
    res_dis = get_circadian_rhythm("ASTRO-DIS", mission_elapsed_hours=24.0, sleep_debt_hours=5.0, local_shift_hours=8.0)
    assert res_dis.circadian_alignment_index < 0.7
    assert res_dis.potential_disruption is True

