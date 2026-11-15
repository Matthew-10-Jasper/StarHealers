import pytest
from app.services.fatigue_service import compute_fatigue_assessment
from app.services.stress_service import compute_stress_monitoring

def test_fatigue_assessment_normal():
    res = compute_fatigue_assessment(
        astronaut_id="ASTRO-01",
        sleep_deficit_hours=0.5,
        cumulative_debt_hours=1.0,
        hrv_rmssd_ms=52.0,
        baseline_hrv=52.0
    )
    assert res.fatigue_level == "NORMAL"
    assert res.fatigue_score < 25.0
    assert res.reliable_data is True
    assert "calculation_breakdown" in res.model_dump()

def test_fatigue_assessment_high_and_unreliable():
    # High fatigue with low HRV suppression
    res_high = compute_fatigue_assessment(
        astronaut_id="ASTRO-02",
        sleep_deficit_hours=3.0,
        cumulative_debt_hours=6.0,
        hrv_rmssd_ms=28.0,
        baseline_hrv=50.0
    )
    assert res_high.fatigue_level == "HIGH"
    assert res_high.fatigue_score >= 55.0

    # Sensor artifact
    res_artifact = compute_fatigue_assessment(
        astronaut_id="ASTRO-03",
        hrv_rmssd_ms=250.0
    )
    assert res_artifact.reliable_data is False
    assert res_artifact.fatigue_level == "UNRELIABLE"

def test_stress_monitoring_metrics_and_no_data():
    res = compute_stress_monitoring(
        astronaut_id="ASTRO-01",
        current_hrv_rmssd=45.0,
        current_heart_rate=72.0,
        sleep_debt_hours=2.0
    )
    assert res.data_available is True
    assert res.current_stress_score is not None
    assert len(res.historical_trend) == 13
    assert res.sleep_debt_stress_correlation is not None

    # No data test
    res_nodata = compute_stress_monitoring(
        astronaut_id="ASTRO-02",
        data_available=False
    )
    assert res_nodata.data_available is False
    assert res_nodata.current_stress_score is None
    assert res_nodata.stress_level == "NO_DATA"

