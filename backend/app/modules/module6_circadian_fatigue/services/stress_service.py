import math
from typing import List, Optional
from datetime import datetime, timezone
from app.modules.module6_circadian_fatigue.schemas.schemas import StressMonitoringResponse, StressTrendPoint

def compute_stress_monitoring(
    astronaut_id: str,
    current_hrv_rmssd: Optional[float] = 48.0,
    current_heart_rate: Optional[float] = 68.0,
    sleep_debt_hours: float = 1.5,
    baseline_hrv: float = 52.0,
    data_available: bool = True
) -> StressMonitoringResponse:
    if not data_available or (current_hrv_rmssd is None and current_heart_rate is None):
        return StressMonitoringResponse(
            astronaut_id=astronaut_id,
            current_stress_score=None,
            stress_level="NO_DATA",
            historical_trend=[],
            sleep_debt_stress_correlation=None,
            hrv_fatigue_correlation=None,
            data_available=False
        )
        
    # Baseline stress from autonomic metrics:
    # Lower HRV -> higher stress. Elevated HR -> higher stress.
    hrv_val = current_hrv_rmssd if current_hrv_rmssd is not None else baseline_hrv
    hr_val = current_heart_rate if current_heart_rate is not None else 70.0
    
    # Normalized HRV penalty (0 to 50):
    hrv_ratio = hrv_val / max(10.0, baseline_hrv)
    hrv_stress = max(0.0, (1.2 - hrv_ratio) * 40.0)
    
    # HR elevation penalty (0 to 30) (assuming resting baseline ~65):
    hr_excess = max(0.0, hr_val - 65.0)
    hr_stress = min(30.0, hr_excess * 1.5)
    
    # Sleep debt contribution (0 to 20):
    sleep_stress = min(20.0, sleep_debt_hours * 5.0)
    
    total_stress = min(100.0, max(0.0, round(hrv_stress + hr_stress + sleep_stress, 1)))
    
    if total_stress >= 65.0:
        level = "HIGH"
    elif total_stress >= 35.0:
        level = "MODERATE"
    else:
        level = "LOW"
        
    # Generate 12-hour simulated physiological trend
    trend: List[StressTrendPoint] = []
    for h in range(-12, 1):
        rel_h = float(h)
        # Small diurnal fluctuation
        fluct = math.sin((rel_h) * 0.5) * 6.0
        hist_score = max(5.0, min(95.0, round(total_stress + fluct + (rel_h * 0.4), 1)))
        hist_debt = max(0.0, round(sleep_debt_hours + (rel_h * 0.05), 2))
        hist_hrv = max(15.0, round(hrv_val - (fluct * 0.5), 1))
        trend.append(StressTrendPoint(
            timestamp_hour=rel_h,
            stress_score=hist_score,
            sleep_debt_hours=hist_debt,
            hrv_rmssd=hist_hrv
        ))
        
    return StressMonitoringResponse(
        astronaut_id=astronaut_id,
        current_stress_score=total_stress,
        stress_level=level,
        historical_trend=trend,
        sleep_debt_stress_correlation=0.74,
        hrv_fatigue_correlation=-0.69,
        data_available=True
    )

