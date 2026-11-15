"""
Tests for Layered Spacecraft Anomaly Detection Engine.
Verifies Layer 1 (Sensor limits), Layer 3 (Engineering physics),
Layer 4 (SciPy statistical Z-score), and Layer 5 (scikit-learn Isolation Forest).
"""

import pytest
from app.services.anomaly_detector import LayeredAnomalyDetector
from app.schemas.observation import EnvironmentalObservation
from app.schemas.enums import DeviationSeverity, DataSource, QualityStatus

@pytest.fixture
def detector():
    return LayeredAnomalyDetector(history_window_size=20)

def test_sensor_limit_violation(detector):
    """Layer 1: Sensor hardware limit checks."""
    obs = [
        EnvironmentalObservation(
            parameter="CABIN_PRESSURE",
            value=-15.0,
            canonical_value=-15.0,
            unit="kPa",
            validation_status=True
        )
    ]
    report = detector.analyze(obs, [])
    assert report.total_anomalies_detected >= 1
    sensor_anomalies = [a for a in report.anomalies if a.layer == "SENSOR_LIMITS"]
    assert len(sensor_anomalies) == 1
    assert sensor_anomalies[0].severity == DeviationSeverity.CRITICAL

def test_engineering_depressurization_and_radiation(detector):
    """Layer 3: Aerospace engineering physics rules."""
    obs = [
        EnvironmentalObservation(
            parameter="CABIN_PRESSURE",
            value=65.0,
            canonical_value=65.0,
            unit="kPa",
            validation_status=True
        ),
        EnvironmentalObservation(
            parameter="RADIATION",
            value=25.0,
            canonical_value=25.0,
            unit="mSv/day",
            validation_status=True
        )
    ]
    report = detector.analyze(obs, [])
    assert report.total_anomalies_detected >= 2
    assert report.highest_severity == DeviationSeverity.CRITICAL
    physics_anomalies = [a for a in report.anomalies if a.layer == "ENGINEERING_PHYSICS"]
    assert len(physics_anomalies) == 2
    assert any("depressurization" in a.explanation.lower() for a in physics_anomalies)
    assert any("solar particle event" in a.explanation.lower() for a in physics_anomalies)

def test_statistical_zscore_outlier(detector):
    """Layer 4: SciPy statistical dispersion Z-score check."""
    # Build 15 nominal readings with mean ~101.3 and std ~0.2
    history = [
        EnvironmentalObservation(
            parameter="CABIN_PRESSURE",
            value=101.3 + (i % 3) * 0.1,
            canonical_value=101.3 + (i % 3) * 0.1,
            unit="kPa",
            validation_status=True
        )
        for i in range(15)
    ]
    # Current reading spikes to 105.0 kPa (more than 10 std deviations away)
    current = [
        EnvironmentalObservation(
            parameter="CABIN_PRESSURE",
            value=105.0,
            canonical_value=105.0,
            unit="kPa",
            validation_status=True
        )
    ]
    report = detector.analyze(current, history)
    stat_anomalies = [a for a in report.anomalies if a.layer == "STATISTICAL_ZSCORE"]
    assert len(stat_anomalies) == 1
    assert stat_anomalies[0].parameter == "CABIN_PRESSURE"
    assert "standard deviations" in stat_anomalies[0].explanation

def test_multivariate_isolation_forest_explainability(detector):
    """Layer 5: Multivariate explainable Isolation Forest."""
    # Joint anomaly: moderate drop in pressure coupled with high CO2 and high radiation
    current = [
        EnvironmentalObservation(
            parameter="CABIN_PRESSURE",
            value=88.0,
            canonical_value=88.0,
            unit="kPa",
            validation_status=True
        ),
        EnvironmentalObservation(
            parameter="CO2",
            value=6500.0,
            canonical_value=6500.0,
            unit="ppm",
            validation_status=True
        ),
        EnvironmentalObservation(
            parameter="RADIATION",
            value=8.5,
            canonical_value=8.5,
            unit="mSv/day",
            validation_status=True
        )
    ]
    report = detector.analyze(current, [])
    assert report.ml_isolation_score is not None
    assert report.ml_is_anomaly is True
    ml_anomalies = [a for a in report.anomalies if a.layer == "ML_ISOLATION_FOREST"]
    assert len(ml_anomalies) == 1
    assert ml_anomalies[0].is_advisory is True
    assert len(ml_anomalies[0].contributing_factors) >= 2
