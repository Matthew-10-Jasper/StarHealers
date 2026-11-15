import pytest
from app.schemas.enums import HazardSeverity, ProvenanceType
from app.schemas.sleep import SleepInput
from app.services.engines.sleep_engine import AstronautSleepEngine

def test_nominal_sleep_schedule():
    """Adequate daily sleep produces minimal sleep debt and zero warning days."""
    params = SleepInput(
        baseline_sleep_hours=8.0,
        nominal_sleep_hours=8.0,
        initial_sleep_debt_hours=0.0,
        mission_days=10,
        disruption_active=False
    )
    engine = AstronautSleepEngine(params)
    res = engine.run_full_simulation("TEST_NOMINAL_SLEEP")

    assert res.final_sleep_debt_hours == 0.0
    assert res.days_above_warning == 0
    assert res.days_above_critical == 0
    assert res.provenance == ProvenanceType.SIMULATED

def test_sleep_deficit_accumulation_and_recovery():
    """Chronic sleep loss accumulates debt; subsequent surplus sleep recovers debt with sub-unity efficiency."""
    # 4 days of 4h sleep (deficit = 4h/day), followed by 3 days of 10h sleep (surplus = 2h/day)
    custom_sched = [4.0, 4.0, 4.0, 4.0, 10.0, 10.0, 10.0]
    params = SleepInput(
        baseline_sleep_hours=8.0,
        initial_sleep_debt_hours=0.0,
        recovery_efficiency=0.75,
        mission_days=7,
        custom_daily_schedule=custom_sched
    )
    engine = AstronautSleepEngine(params)
    res = engine.run_full_simulation("TEST_RECOVERY")

    # Day 4: 4 days * 4h deficit = 16.0h debt
    day4_step = res.timesteps[3]
    assert day4_step.cumulative_debt_hours == 16.0
    assert day4_step.severity == HazardSeverity.CRITICAL

    # Days 5-7: 3 days * 2h surplus * 0.75 recovery = 4.5h recovered
    # Final debt should be 16.0 - 4.5 = 11.5h
    assert pytest.approx(res.final_sleep_debt_hours, rel=1e-2) == 11.5
    assert res.peak_sleep_debt_hours == 16.0
    assert res.days_above_warning > 0

def test_acute_sleep_disruption_scenario():
    """Disruption active flags days appropriately and elevates hazard severity."""
    params = SleepInput(
        baseline_sleep_hours=8.0,
        nominal_sleep_hours=7.5,
        mission_days=10,
        disruption_active=True,
        disruption_start_day=3,
        disruption_duration_days=4,
        disrupted_sleep_hours=3.0
    )
    engine = AstronautSleepEngine(params)
    res = engine.run_full_simulation("TEST_DISRUPTION")

    # Peak sleep debt should be significantly elevated during disruption
    assert res.peak_sleep_debt_hours > 12.0
    assert res.days_above_warning >= 4

def test_days_above_warning_includes_critical_days_regression():
    """Regression test ensuring days_above_warning encompasses all days >= warning threshold (including critical)."""
    # 3 days with 2h sleep -> debt accumulates to 6h (Elevated), 12h (Warning), 18h (Critical)
    params = SleepInput(
        baseline_sleep_hours=8.0,
        initial_sleep_debt_hours=0.0,
        mission_days=3,
        custom_daily_schedule=[2.0, 2.0, 2.0]
    )
    engine = AstronautSleepEngine(params)
    res = engine.run_full_simulation("TEST_THRESHOLD_SEMANTICS")

    # Day 1: debt 6.0h (Elevated)
    # Day 2: debt 12.0h (Warning >= 8.0h)
    # Day 3: debt 18.0h (Critical >= 16.0h)
    # days_above_warning must count Day 2 and Day 3 (2 days)
    # days_above_critical must count Day 3 (1 day)
    assert res.days_above_warning == 2
    assert res.days_above_critical == 1

