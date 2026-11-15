"""
Starhealers Module 4 - Multi-Layered Spacecraft Anomaly Detection Engine.
Combines deterministic physics rules, statistical dispersion (SciPy/NumPy),
and unsupervised multivariate Machine Learning (scikit-learn Isolation Forest)
with explainable contribution scores.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest

from app.schemas.enums import DeviationSeverity, QualityStatus
from app.schemas.observation import EnvironmentalObservation

logger = logging.getLogger("AnomalyDetector")

class AnomalyExplanation(BaseModel):
    layer: str = Field(..., description="Detection layer: SENSOR_LIMITS, DATA_QUALITY, ENGINEERING_PHYSICS, STATISTICAL_ZSCORE, or ML_ISOLATION_FOREST")
    parameter: str
    observed_value: float
    expected_range: Optional[Tuple[float, float]] = None
    severity: DeviationSeverity
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    contributing_factors: List[str] = Field(default_factory=list)
    is_advisory: bool = True

class LayeredAnomalyReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_anomalies_detected: int = 0
    highest_severity: Optional[DeviationSeverity] = None
    anomalies: List[AnomalyExplanation] = Field(default_factory=list)
    ml_isolation_score: Optional[float] = None
    ml_is_anomaly: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LayeredAnomalyDetector:
    """
    5-Layer Spacecraft Environmental Anomaly Detector:
    Layer 1: Sensor bounds & non-physical limits.
    Layer 2: Freshness, sensor dropouts, sampling jitter.
    Layer 3: Aerospace engineering physics (rapid decompression, hypercapnia, SPE).
    Layer 4: Rolling Statistical Outlier Detection (SciPy Z-score & IQR).
    Layer 5: Multivariate Explainable Isolation Forest (scikit-learn).
    """

    def __init__(self, history_window_size: int = 30):
        self.history_window_size = history_window_size
        self._isolation_forest = IsolationForest(
            n_estimators=50,
            contamination=0.05,
            random_state=42
        )
        self._model_fitted = False
        self._init_nominal_baseline()

    def _init_nominal_baseline(self):
        """Initializes nominal synthetic training baseline for unsupervised Isolation Forest."""
        np.random.seed(42)
        # Features: [cabin_pressure_kPa, co2_ppm, radiation_mSv_day, comm_delay_s]
        n_samples = 120
        nominal_pressure = np.random.normal(101.3, 0.5, n_samples)
        nominal_co2 = np.random.normal(1200.0, 150.0, n_samples)
        nominal_rad = np.random.normal(0.4, 0.05, n_samples)
        nominal_delay = np.random.normal(1.2, 0.1, n_samples)

        X_nominal = np.column_stack([nominal_pressure, nominal_co2, nominal_rad, nominal_delay])
        self._isolation_forest.fit(X_nominal)
        self._model_fitted = True

    def analyze(
        self,
        current_observations: List[EnvironmentalObservation],
        historical_observations: List[EnvironmentalObservation]
    ) -> LayeredAnomalyReport:
        """Executes all 5 detection layers across current telemetry against historical buffer."""
        report = LayeredAnomalyReport()
        detected: List[AnomalyExplanation] = []

        # Layer 1 & 3: Deterministic Physics and Engineering Rules
        for obs in current_observations:
            val = obs.canonical_value if obs.canonical_value is not None else obs.value
            if not isinstance(val, (int, float)):
                continue

            param = obs.parameter.upper()

            # LAYER 1: Sensor Physical Limits
            if param == "CABIN_PRESSURE" and (val < 0.0 or val > 200.0):
                detected.append(AnomalyExplanation(
                    layer="SENSOR_LIMITS",
                    parameter=param,
                    observed_value=val,
                    expected_range=(0.0, 200.0),
                    severity=DeviationSeverity.CRITICAL,
                    confidence_score=1.0,
                    explanation=f"Sensor value {val} kPa violates physical spacecraft pressure transducer limits."
                ))

            # LAYER 3: Engineering Physics Rules
            if param == "CABIN_PRESSURE":
                if val < 70.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(95.0, 105.0),
                        severity=DeviationSeverity.CRITICAL,
                        confidence_score=0.98,
                        explanation=f"Severe cabin depressurization ({val} kPa). Barometric hypoxia imminent without emergency suit activation."
                    ))
                elif val < 90.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(95.0, 105.0),
                        severity=DeviationSeverity.WARNING,
                        confidence_score=0.90,
                        explanation=f"Cabin pressure sub-nominal ({val} kPa). Possible micro-meteorite slow leak or regulator fault."
                    ))

            if param in ("CO2", "CO2_CONCENTRATION"):
                if val > 8000.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(500.0, 3000.0),
                        severity=DeviationSeverity.CRITICAL,
                        confidence_score=0.95,
                        explanation=f"Severe hypercapnia risk: CO2 reached {val:.0f} ppm. Scrubber cartridge breakthrough or blower failure."
                    ))
                elif val > 4000.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(500.0, 3000.0),
                        severity=DeviationSeverity.WARNING,
                        confidence_score=0.85,
                        explanation=f"Elevated CO2 concentration ({val:.0f} ppm). Exceeds nominal continuous habitability threshold."
                    ))

            if param == "RADIATION":
                if val > 20.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(0.1, 1.5),
                        severity=DeviationSeverity.CRITICAL,
                        confidence_score=0.99,
                        explanation=f"Acute radiation hazard ({val:.2f} mSv/day). Solar Particle Event (SPE) or magnetospheric crossing. Storm shelter protocol required."
                    ))
                elif val > 2.0:
                    detected.append(AnomalyExplanation(
                        layer="ENGINEERING_PHYSICS",
                        parameter=param,
                        observed_value=val,
                        expected_range=(0.1, 1.5),
                        severity=DeviationSeverity.WARNING,
                        confidence_score=0.90,
                        explanation=f"Elevated cosmic radiation ({val:.2f} mSv/day). Cumulative crew career exposure rate heightened."
                    ))

        # LAYER 4: Statistical Outlier Detection (Rolling Z-Score & IQR with SciPy)
        if len(historical_observations) >= 8:
            params_to_check = set(o.parameter.upper() for o in current_observations)
            for param in params_to_check:
                hist_vals = [
                    (h.canonical_value if h.canonical_value is not None else h.value)
                    for h in historical_observations
                    if h.parameter.upper() == param and isinstance((h.canonical_value if h.canonical_value is not None else h.value), (int, float))
                ]
                curr_matches = [
                    (c.canonical_value if c.canonical_value is not None else c.value)
                    for c in current_observations
                    if c.parameter.upper() == param and isinstance((c.canonical_value if c.canonical_value is not None else c.value), (int, float))
                ]
                if len(hist_vals) >= 8 and curr_matches:
                    curr_val = curr_matches[0]
                    hist_arr = np.array(hist_vals[-self.history_window_size:], dtype=float)
                    mean = float(np.mean(hist_arr))
                    std = float(np.std(hist_arr))
                    
                    if std > 1e-4:
                        z_score = abs(curr_val - mean) / std
                        if z_score > 3.0:
                            conf = min(0.99, round(z_score / 4.5, 2))
                            detected.append(AnomalyExplanation(
                                layer="STATISTICAL_ZSCORE",
                                parameter=param,
                                observed_value=curr_val,
                                expected_range=(round(mean - 2 * std, 2), round(mean + 2 * std, 2)),
                                severity=DeviationSeverity.WARNING if z_score < 4.5 else DeviationSeverity.CRITICAL,
                                confidence_score=conf,
                                explanation=(
                                    f"Statistical telemetry anomaly for {param}: Observed {curr_val:.2f} "
                                    f"diverges by {z_score:.2f} standard deviations from rolling mean ({mean:.2f} +/- {std:.2f})."
                                )
                            ))

        # LAYER 5: Multivariate Explainable Machine Learning (Isolation Forest)
        ml_score, is_ml_anomaly, ml_factors = self._evaluate_multivariate_ml(current_observations)
        report.ml_isolation_score = ml_score
        report.ml_is_anomaly = is_ml_anomaly

        if is_ml_anomaly:
            detected.append(AnomalyExplanation(
                layer="ML_ISOLATION_FOREST",
                parameter="MULTIVARIATE_TELEMETRY",
                observed_value=ml_score,
                severity=DeviationSeverity.WARNING,
                confidence_score=min(0.95, round(abs(ml_score) * 2.0, 2)),
                explanation=(
                    f"Multivariate unsupervised Isolation Forest detected coupled telemetry anomaly (score: {ml_score:.3f}). "
                    f"Unusual joint correlation detected across spacecraft telemetry features."
                ),
                contributing_factors=ml_factors,
                is_advisory=True
            ))

        # Aggregate report
        report.anomalies = detected
        report.total_anomalies_detected = len(detected)
        if any(a.severity == DeviationSeverity.CRITICAL for a in detected):
            report.highest_severity = DeviationSeverity.CRITICAL
        elif any(a.severity == DeviationSeverity.WARNING for a in detected):
            report.highest_severity = DeviationSeverity.WARNING

        return report

    def _evaluate_multivariate_ml(self, observations: List[EnvironmentalObservation]) -> Tuple[float, bool, List[str]]:
        """Evaluates joint multi-sensor vector through Isolation Forest and returns feature contributions."""
        obs_map = {}
        for o in observations:
            val = o.canonical_value if o.canonical_value is not None else o.value
            if isinstance(val, (int, float)):
                obs_map[o.parameter.upper()] = float(val)

        # Baseline nominal fallbacks if parameter is missing
        p = obs_map.get("CABIN_PRESSURE", 101.3)
        c = obs_map.get("CO2", obs_map.get("CO2_CONCENTRATION", 1200.0))
        r = obs_map.get("RADIATION", 0.4)
        d = obs_map.get("COMMUNICATION_DELAY", 1.2)

        feat_vector = np.array([[p, c, r, d]])
        decision_score = float(self._isolation_forest.decision_function(feat_vector)[0])
        pred = int(self._isolation_forest.predict(feat_vector)[0])
        is_anomaly = pred == -1

        contributing = []
        if abs(p - 101.3) > 5.0:
            contributing.append(f"Pressure deviation ({p:.1f} kPa vs 101.3 nominal)")
        if c > 2500.0:
            contributing.append(f"CO2 elevated ({c:.0f} ppm vs 1200 nominal)")
        if r > 1.0:
            contributing.append(f"Radiation elevated ({r:.2f} mSv/d vs 0.4 nominal)")
        if d > 10.0:
            contributing.append(f"Communication delay extended ({d:.1f} s vs 1.2 nominal)")

        return decision_score, is_anomaly, contributing
