import pytest
from app.api.v1.overview import get_unified_mission_overview

def test_unified_overview_aggregation():
    ov = get_unified_mission_overview()
    assert ov["title"] == "STARHEALERS Unified Situational Overview"
    
    # Mission intelligence
    m_intel = ov["mission_intelligence"]
    assert "mission_id" in m_intel
    assert "operational_state" in m_intel
    assert "active_deviations_count" in m_intel

    # Astronaut health
    a_health = ov["astronaut_health"]
    assert a_health["crew_count"] >= 4
    assert len(a_health["roster"]) >= 4
    assert "active_triage_alerts_count" in a_health

    # Human performance
    h_perf = ov["human_performance"]
    assert 0.0 <= h_perf["cognitive_readiness_score"] <= 100.0
    assert h_perf["readiness_rating"] in ["OPTIMAL_PERFORMANCE", "QUALIFIED_MONITORED", "DEGRADED_RESTRICTED", "IMPAIRED"]
    assert "fatigue_level" in h_perf

    # Space environment hazards
    s_env = ov["space_environment_hazards"]
    assert 0.0 <= s_env["composite_risk_score"] <= 100.0
    assert s_env["operational_risk_level"] in ["NOMINAL", "MONITORING_REQUIRED", "CONTINGENCY", "EMERGENCY"]
    assert s_env["radiation_cumulative_dose_msv"] >= 0.0
    assert s_env["co2_ppco2_mmhg"] >= 0.0
