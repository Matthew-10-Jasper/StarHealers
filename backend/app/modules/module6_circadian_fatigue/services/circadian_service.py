import math
from typing import List, Dict, Any, Optional
from app.modules.module6_circadian_fatigue.schemas.schemas import CircadianPhasePoint, CircadianRhythmResponse

def compute_circadian_phase(local_hour: float) -> str:
    h = local_hour % 24.0
    if 2.0 <= h < 6.0:
        return "CIRCADIAN_TROUGH"
    elif 9.0 <= h < 13.0:
        return "PEAK_ALERTNESS"
    elif 13.0 <= h < 17.0:
        return "MAINTENANCE_ZONE"
    elif 21.0 <= h or h < 2.0:
        return "SLEEP_GATE"
    else:
        return "NOMINAL_ACTIVE"

def compute_alertness_at_hour(hour: float, sleep_debt_hours: float = 0.0) -> float:
    h = hour % 24.0
    # Process C: 24h sinusoidal circadian oscillation, peak around 12:00-14:00, trough around 04:00
    phase_rad = (h - 14.0) * (2.0 * math.pi / 24.0)
    process_c = math.cos(phase_rad)  # -1.0 to 1.0
    
    # Process S: homeostatic debt penalty (each hour of debt reduces baseline by ~4%)
    debt_penalty = min(35.0, sleep_debt_hours * 4.0)
    
    # Base alertness around 75, Process C swing +/- 20
    alertness = 75.0 + (process_c * 20.0) - debt_penalty
    return max(5.0, min(100.0, round(alertness, 1)))

def get_circadian_rhythm(
    astronaut_id: str,
    mission_elapsed_hours: float = 72.0,
    sleep_debt_hours: float = 1.5,
    local_shift_hours: float = 0.0
) -> CircadianRhythmResponse:
    local_hour = (mission_elapsed_hours + local_shift_hours) % 24.0
    mission_day = int(mission_elapsed_hours // 24) + 1
    current_phase = compute_circadian_phase(local_hour)
    
    # 24h Alertness curve projection
    curve: List[CircadianPhasePoint] = []
    for h in range(24):
        h_float = float(h)
        a_score = compute_alertness_at_hour(h_float, sleep_debt_hours)
        b_phase = compute_circadian_phase(h_float)
        curve.append(CircadianPhasePoint(
            hour=h_float,
            alertness_score=a_score,
            biological_phase=b_phase
        ))
        
    current_alertness = compute_alertness_at_hour(local_hour, sleep_debt_hours)
    
    # Alignment index: 1.0 optimal, degraded if local shift or high debt
    shift_penalty = abs(local_shift_hours % 24.0)
    if shift_penalty > 12.0:
        shift_penalty = 24.0 - shift_penalty
    alignment_index = max(0.1, min(1.0, round(1.0 - (shift_penalty / 24.0) * 0.6 - (sleep_debt_hours / 20.0), 2)))
    
    potential_disruption = (alignment_index < 0.65) or (sleep_debt_hours >= 4.0)
    disruption_notes = (
        f"Circadian phase alignment is {int(alignment_index*100)}%. Sleep debt of {sleep_debt_hours:.1f}h contributes to phase lag."
        if potential_disruption else "Circadian alignment is optimal for current mission sol."
    )
    
    return CircadianRhythmResponse(
        astronaut_id=astronaut_id,
        mission_elapsed_hours=mission_elapsed_hours,
        mission_day=mission_day,
        local_mission_hour=round(local_hour, 2),
        current_phase=current_phase,
        circadian_alignment_index=alignment_index,
        alertness_estimate=current_alertness,
        potential_disruption=potential_disruption,
        disruption_notes=disruption_notes,
        alertness_curve_24h=curve,
        model_provenance="ESTIMATED_TWO_PROCESS_CIRCADIAN_MODEL"
    )

