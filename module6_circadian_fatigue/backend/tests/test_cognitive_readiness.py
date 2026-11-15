import pytest
from app.services.readiness_engine import calculate_cognitive_readiness

def test_optimal_readiness():
    res = calculate_cognitive_readiness(
        astronaut_id="ASTRO-01",
        sleep_debt_hours=0.5,
        circadian_alertness=90.0,
        circadian_alignment=0.98,
        fatigue_score=15.0,
        stress_score=20.0,
        pvt_avg_rt_ms=240.0,
        pvt_lapses=0
    )
    assert res.overall_readiness_score >= 85.0
    assert res.rating == "OPTIMAL_PERFORMANCE"
    assert res.data_completeness == 1.0
    assert "Non-clinical decision-support metric" in res.non_clinical_disclaimer

def test_degraded_and_impaired_readiness():
    # Degraded
    res_deg = calculate_cognitive_readiness(
        astronaut_id="ASTRO-02",
        sleep_debt_hours=4.0,
        circadian_alertness=65.0,
        circadian_alignment=0.70,
        fatigue_score=55.0,
        stress_score=60.0,
        pvt_avg_rt_ms=380.0,
        pvt_lapses=2
    )
    assert 50.0 <= res_deg.overall_readiness_score < 70.0
    assert res_deg.rating == "DEGRADED_RESTRICTED"

    # Impaired
    res_imp = calculate_cognitive_readiness(
        astronaut_id="ASTRO-03",
        sleep_debt_hours=7.0,
        circadian_alertness=40.0,
        circadian_alignment=0.40,
        fatigue_score=85.0,
        stress_score=85.0,
        pvt_avg_rt_ms=620.0,
        pvt_lapses=5
    )
    assert res_imp.overall_readiness_score < 50.0
    assert res_imp.rating == "IMPAIRED"

def test_weights_sum_to_one():
    res = calculate_cognitive_readiness("ASTRO-04")
    weights = res.factor_weights
    total_weight = sum(weights.values())
    assert abs(total_weight - 1.0) < 1e-5

