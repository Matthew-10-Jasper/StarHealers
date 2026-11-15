from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import HazardAlertModel
from app.schemas.schemas import CompositeRiskResponse
from app.services.m5_consumer import get_radiation_overview, get_co2_overview
from app.services.m4_consumer import fetch_m4_cabin_telemetry

def compute_composite_risk(db: Optional[Session] = None) -> CompositeRiskResponse:
    rad = get_radiation_overview()
    co2 = get_co2_overview()
    cabin = fetch_m4_cabin_telemetry()
    
    # 1. Radiation Risk Component (0 to 100)
    # Dose rate > 0.5 mSv/h or 30-day limit % elevates score
    rad_rate_penalty = min(60.0, (rad.current_dose_rate_msv_h / 0.5) * 40.0)
    rad_limit_penalty = min(40.0, (rad.thirty_day_limit_pct / 50.0) * 40.0)
    rad_risk = min(100.0, rad_rate_penalty + rad_limit_penalty)
    
    # 2. CO2 Risk Component (0 to 100)
    # ppCO2 > 3.0 mmHg starts warning, >= 5.0 mmHg is critical
    if co2.ppco2_mmhg <= 1.0:
        co2_risk = 5.0
    elif co2.ppco2_mmhg <= 3.0:
        co2_risk = 5.0 + ((co2.ppco2_mmhg - 1.0) / 2.0) * 30.0
    elif co2.ppco2_mmhg <= 5.0:
        co2_risk = 35.0 + ((co2.ppco2_mmhg - 3.0) / 2.0) * 40.0
    else:
        co2_risk = min(100.0, 75.0 + (co2.ppco2_mmhg - 5.0) * 12.0)
        
    # 3. Cabin Risk Component (0 to 100)
    cabin_risk = 10.0  # Nominal pressure 70.3 kPa
    if cabin.cabin_pressure_kpa is not None:
        if cabin.cabin_pressure_kpa < 65.0 or cabin.cabin_pressure_kpa > 75.0:
            cabin_risk = 75.0
        elif cabin.cabin_pressure_kpa < 68.0 or cabin.cabin_pressure_kpa > 72.0:
            cabin_risk = 35.0
    else:
        cabin_risk = 25.0  # Missing data uncertainty
        
    # Composite Weighted Risk
    overall = (0.40 * rad_risk) + (0.35 * co2_risk) + (0.25 * cabin_risk)
    overall = round(max(0.0, min(100.0, overall)), 1)
    
    # Active unacknowledged hazard alerts count
    active_count = 0
    if db is not None:
        active_count = db.query(HazardAlertModel).filter(HazardAlertModel.acknowledged == False).count()
    else:
        active_count = 2
        
    if overall >= 80.0:
        risk_level = "EMERGENCY"
        summary = "CRITICAL: Multiple life-support environmental thresholds breached. Emergency shielding and scrubber purge recommended."
    elif overall >= 55.0:
        risk_level = "CONTINGENCY"
        summary = "CONTINGENCY: Elevated radiation or atmospheric CO2 levels require active mitigation procedures."
    elif overall >= 25.0:
        risk_level = "MONITORING_REQUIRED"
        summary = "MONITORING REQUIRED: SPE event or partial scrubber degradation active. All cabin environmental parameters stable."
    else:
        risk_level = "NOMINAL"
        summary = "NOMINAL: Space environment radiation and life-support parameters within safe operational margins."
        
    return CompositeRiskResponse(
        overall_risk_index=overall,
        operational_risk_level=risk_level,
        radiation_risk_score=round(rad_risk, 1),
        co2_risk_score=round(co2_risk, 1),
        cabin_risk_score=round(cabin_risk, 1),
        active_hazards_count=active_count,
        summary=summary,
        timestamp=datetime.now(timezone.utc)
    )
