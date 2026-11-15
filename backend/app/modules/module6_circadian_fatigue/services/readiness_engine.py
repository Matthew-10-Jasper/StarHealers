import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.modules.module6_circadian_fatigue.schemas.schemas import CognitiveReadinessResponse

FACTOR_WEIGHTS = {
    "sleep": 0.30,
    "circadian": 0.25,
    "fatigue": 0.15,
    "stress": 0.10,
    "pvt": 0.20
}

def calculate_cognitive_readiness(
    astronaut_id: str,
    sleep_debt_hours: float = 1.0,
    circadian_alertness: float = 85.0,
    circadian_alignment: float = 0.95,
    fatigue_score: float = 20.0,
    stress_score: Optional[float] = 30.0,
    pvt_avg_rt_ms: Optional[float] = 270.0,
    pvt_lapses: int = 0
) -> CognitiveReadinessResponse:
    # 1. Sleep Component S_norm (0 to 100):
    # 0h debt -> 100. Each hour of debt deducts ~12 points.
    s_norm = max(10.0, min(100.0, 100.0 - (sleep_debt_hours * 12.0)))
    
    # 2. Circadian Component C_norm (0 to 100):
    # Combination of alertness score and alignment index
    c_norm = max(10.0, min(100.0, (circadian_alertness * 0.6) + (circadian_alignment * 100.0 * 0.4)))
    
    # 3. Fatigue Component F_norm (0 to 100):
    # Inverted fatigue score (lower fatigue -> higher readiness)
    f_norm = max(5.0, min(100.0, 100.0 - fatigue_score))
    
    # 4. Stress Component T_norm (0 to 100):
    # Inverted stress score, or fallback to 75.0 if unavailable
    stress_available = (stress_score is not None)
    if stress_available:
        t_norm = max(5.0, min(100.0, 100.0 - (stress_score or 0.0)))
    else:
        t_norm = 75.0
        
    # 5. PVT Component P_norm (0 to 100):
    pvt_available = (pvt_avg_rt_ms is not None)
    if pvt_available:
        rt = pvt_avg_rt_ms or 280.0
        # 220ms or faster is 100, 500ms is 40
        rt_score = 100.0 - max(0.0, (rt - 220.0) * 0.22)
        lapse_penalty = pvt_lapses * 15.0
        p_norm = max(5.0, min(100.0, rt_score - lapse_penalty))
    else:
        p_norm = 80.0  # nominal baseline
        
    # Data completeness indicator
    completeness_pts = 3.0  # sleep, circadian, fatigue are always modeled
    if stress_available:
        completeness_pts += 1.0
    if pvt_available:
        completeness_pts += 1.0
    data_completeness = round(completeness_pts / 5.0, 2)
    
    # Vectorized multi-factor dot product using numpy
    weights_vector = np.array([
        FACTOR_WEIGHTS["sleep"],
        FACTOR_WEIGHTS["circadian"],
        FACTOR_WEIGHTS["fatigue"],
        FACTOR_WEIGHTS["stress"],
        FACTOR_WEIGHTS["pvt"]
    ], dtype=np.float64)
    
    components_vector = np.array([s_norm, c_norm, f_norm, t_norm, p_norm], dtype=np.float64)
    
    overall_score = float(np.dot(weights_vector, components_vector))
    overall_score = max(0.0, min(100.0, round(overall_score, 1)))
    
    if overall_score >= 85.0:
        rating = "OPTIMAL_PERFORMANCE"
        explanation = "High cognitive readiness. All biological and psychomotor markers support mission-critical tasks and EVA activities."
    elif overall_score >= 70.0:
        rating = "QUALIFIED_MONITORED"
        explanation = "Acceptable readiness. Minor fatigue or circadian phase lag detected; monitor during high-stress operations."
    elif overall_score >= 50.0:
        rating = "DEGRADED_RESTRICTED"
        explanation = "Degraded cognitive capacity. Accumulating sleep debt and elevated reaction times indicate operational restriction recommended."
    else:
        rating = "IMPAIRED"
        explanation = "Critical cognitive impairment detected. Mandatory sleep recovery and psychomotor reassessment required prior to safety-critical duties."

    return CognitiveReadinessResponse(
        astronaut_id=astronaut_id,
        overall_readiness_score=overall_score,
        rating=rating,
        sleep_component=round(s_norm, 1),
        circadian_component=round(c_norm, 1),
        fatigue_component=round(f_norm, 1),
        stress_component=round(t_norm, 1),
        pvt_component=round(p_norm, 1),
        factor_weights=FACTOR_WEIGHTS,
        data_completeness=data_completeness,
        explanation=explanation,
        timestamp=datetime.now(timezone.utc)
    )

