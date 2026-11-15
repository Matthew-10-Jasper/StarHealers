from typing import Dict, Any, Optional
from app.schemas.schemas import FatigueAssessmentResponse

def compute_fatigue_assessment(
    astronaut_id: str,
    sleep_deficit_hours: float = 1.0,
    cumulative_debt_hours: float = 2.5,
    hrv_rmssd_ms: Optional[float] = 48.0,
    heart_rate_bpm: Optional[float] = 68.0,
    baseline_hrv: float = 52.0
) -> FatigueAssessmentResponse:
    # Baseline fatigue starting from sleep debt components:
    # 1h daily deficit adds ~15 points; cumulative debt adds ~8 points per hour
    debt_component = (sleep_deficit_hours * 15.0) + (cumulative_debt_hours * 8.0)
    debt_component = min(60.0, max(0.0, debt_component))
    
    # Autonomic component (HRV suppression):
    # Lower HRV RMSSD compared to baseline indicates autonomic fatigue
    autonomic_component = 0.0
    reliable_data = True
    
    if hrv_rmssd_ms is not None:
        if hrv_rmssd_ms < 10.0 or hrv_rmssd_ms > 200.0:
            # Unrealistic physiological artifact
            reliable_data = False
        else:
            ratio = hrv_rmssd_ms / max(10.0, baseline_hrv)
            if ratio < 0.7:  # Severe suppression
                autonomic_component = 30.0
            elif ratio < 0.9:  # Mild suppression
                autonomic_component = 15.0
            else:
                autonomic_component = 5.0
    else:
        reliable_data = False
        autonomic_component = 10.0  # neutral estimated default
        
    raw_fatigue = debt_component + autonomic_component
    fatigue_score = min(100.0, max(0.0, round(raw_fatigue, 1)))
    
    if not reliable_data:
        level = "UNRELIABLE"
        notes = "Physiological sensors offline or transmitting unverified artifacts; fatigue estimated solely from schedule deficit."
    elif fatigue_score >= 55.0:
        level = "HIGH"
        notes = "High fatigue detected. Sustained sleep deficit and autonomic suppression present."
    elif fatigue_score >= 25.0:
        level = "ELEVATED"
        notes = "Moderate fatigue detected. Monitor during safety-critical operational windows."
    else:
        level = "NORMAL"
        notes = "Fatigue markers within normal operational parameters."
        
    stress_idx = round(min(100.0, max(0.0, (100.0 - (hrv_rmssd_ms or 50.0)) * 0.8 + (sleep_deficit_hours * 5.0))), 1)

    breakdown = {
        "sleep_deficit_penalty": round(debt_component, 1),
        "autonomic_hrv_penalty": round(autonomic_component, 1),
        "baseline_hrv_reference": baseline_hrv,
        "current_hrv_rmssd": hrv_rmssd_ms,
        "calculation_formula": "fatigue = min(100, (deficit*15 + cumulative*8) + autonomic_penalty)"
    }
    
    return FatigueAssessmentResponse(
        astronaut_id=astronaut_id,
        fatigue_level=level,
        fatigue_score=fatigue_score,
        heart_rate_bpm=heart_rate_bpm,
        hrv_rmssd_ms=hrv_rmssd_ms,
        sleep_deficit_hours=sleep_deficit_hours,
        cumulative_debt_hours=cumulative_debt_hours,
        stress_index=stress_idx,
        reliable_data=reliable_data,
        assessment_notes=notes,
        calculation_breakdown=breakdown
    )

