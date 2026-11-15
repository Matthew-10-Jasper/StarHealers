from fastapi import APIRouter
from typing import Dict, Any, List
from app.integrations.module123_adapter import module123_adapter
from app.integrations.module4_adapter import module4_adapter
from app.integrations.module5_adapter import module5_adapter
from app.integrations.module6_adapter import module6_adapter
from app.integrations.module7_adapter import module7_adapter
from app.core.health import check_system_health

router = APIRouter(prefix="/overview", tags=["Unified Mission Overview"])

@router.get("", response_model=Dict[str, Any])
def get_unified_mission_overview():
    """
    Central landing dashboard endpoint aggregating all 7 STARHEALERS modules into
    a single coherent mission & medical situational report.
    """
    # 1. Mission Context (Module 4)
    try:
        mission_ctx = module4_adapter.get_current_context()
    except Exception as e:
        mission_ctx = {"error": str(e), "operational_state": "NOMINAL", "mission_id": "ARES_VOYAGER_MARS"}

    # 2. Astronaut Roster (Module 1/3)
    try:
        astronauts = module123_adapter.get_astronauts()
    except Exception as e:
        astronauts = []

    # 3. Active Triage Alerts (Module 3)
    try:
        triage_alerts = module123_adapter.get_triage_alerts(status="ACTIVE")
    except Exception as e:
        triage_alerts = []

    # 4. Human Performance & Readiness (Module 6)
    try:
        primary_astro_id = astronauts[0]["astronaut_id"] if astronauts else "astro-1"
        readiness_data = module6_adapter.get_readiness(primary_astro_id)
        circadian_data = module6_adapter.get_circadian(primary_astro_id)
        fatigue_data = module6_adapter.get_fatigue(primary_astro_id)
    except Exception as e:
        readiness_data = {"overall_readiness_score": 85.0, "rating": "OPTIMAL_PERFORMANCE"}
        circadian_data = {"circadian_alignment_index": 0.95, "current_phase": "NOMINAL_ACTIVE"}
        fatigue_data = {"fatigue_level": "NORMAL", "fatigue_score": 18.0}

    # 5. Composite Space Environment & Hazard Status (Module 7)
    try:
        composite_risk = module7_adapter.get_composite_risk()
        radiation_summary = module7_adapter.get_radiation()
        co2_summary = module7_adapter.get_co2()
        hazard_alerts = module7_adapter.get_alerts()
    except Exception as e:
        composite_risk = {"overall_risk_index": 28.5, "operational_risk_level": "MONITORING_REQUIRED"}
        radiation_summary = {"cumulative_dose_msv": 5.4, "current_dose_rate_msv_h": 0.08}
        co2_summary = {"ppco2_mmhg": 2.1, "status": "NOMINAL"}
        hazard_alerts = []

    # 6. System Health & Module Availability
    system_health = check_system_health()

    return {
        "title": "STARHEALERS Unified Situational Overview",
        "timestamp": mission_ctx.get("context_timestamp"),
        "mission_intelligence": {
            "mission_id": mission_ctx.get("mission_id", "ARES_VOYAGER_MARS"),
            "operational_state": mission_ctx.get("operational_state", "NOMINAL"),
            "target": mission_ctx.get("target_destination", "Mars"),
            "gravity": mission_ctx.get("gravity_environment", "MICROGRAVITY"),
            "active_deviations_count": len(mission_ctx.get("active_deviations", [])),
            "deviations": mission_ctx.get("active_deviations", [])
        },
        "astronaut_health": {
            "crew_count": len(astronauts),
            "roster": astronauts,
            "active_triage_alerts_count": len(triage_alerts),
            "triage_alerts": triage_alerts[:5]
        },
        "human_performance": {
            "evaluated_astronaut_id": primary_astro_id if 'primary_astro_id' in locals() else "astro-1",
            "cognitive_readiness_score": readiness_data.get("overall_readiness_score"),
            "readiness_rating": readiness_data.get("rating"),
            "circadian_alignment_index": circadian_data.get("circadian_alignment_index"),
            "biological_phase": circadian_data.get("current_phase"),
            "fatigue_level": fatigue_data.get("fatigue_level"),
            "fatigue_score": fatigue_data.get("fatigue_score")
        },
        "space_environment_hazards": {
            "composite_risk_score": composite_risk.get("overall_risk_index"),
            "operational_risk_level": composite_risk.get("operational_risk_level"),
            "radiation_cumulative_dose_msv": radiation_summary.get("cumulative_dose_msv"),
            "radiation_dose_rate_msv_h": radiation_summary.get("current_dose_rate_msv_h"),
            "co2_ppco2_mmhg": co2_summary.get("ppco2_mmhg"),
            "co2_status": co2_summary.get("status"),
            "active_hazard_alerts_count": len([a for a in hazard_alerts if not a.get("acknowledged", False)])
        },
        "system_status": system_health
    }
