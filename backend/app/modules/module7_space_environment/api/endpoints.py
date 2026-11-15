from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.modules.module7_space_environment.database.session import get_db
from app.modules.module7_space_environment.schemas.schemas import (
    RadiationOverviewResponse,
    CO2OverviewResponse,
    CabinTelemetryResponse,
    HazardAlertResponse,
    AlertAcknowledgeRequest,
    CompositeRiskResponse
)
from app.modules.module7_space_environment.services.m5_consumer import get_radiation_overview, get_co2_overview
from app.modules.module7_space_environment.services.m4_consumer import fetch_m4_cabin_telemetry
from app.modules.module7_space_environment.services.alert_service import list_hazard_alerts, acknowledge_hazard_alert
from app.modules.module7_space_environment.services.environmental_engine import compute_composite_risk

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "module7_environment_radiation",
        "port": 8007,
        "capabilities": [
            "radiation_exposure_tracking",
            "co2_atmospheric_monitoring",
            "m4_cabin_context_integration",
            "hazard_alert_triage",
            "composite_risk_engine"
        ]
    }

@router.get("/environment/overview", response_model=CompositeRiskResponse)
def get_environmental_overview(db: Session = Depends(get_db)):
    return compute_composite_risk(db=db)

@router.get("/environment/radiation", response_model=RadiationOverviewResponse)
def get_radiation(
    mission_hours: float = Query(72.0, ge=1.0),
    has_active_spe: bool = Query(True)
):
    return get_radiation_overview(mission_hours=mission_hours, has_active_spe=has_active_spe)

@router.get("/environment/co2", response_model=CO2OverviewResponse)
def get_co2(
    mission_hours: float = Query(72.0, ge=1.0),
    scrubber_degraded: bool = Query(True)
):
    return get_co2_overview(mission_hours=mission_hours, scrubber_degraded=scrubber_degraded)

@router.get("/environment/cabin", response_model=CabinTelemetryResponse)
def get_cabin():
    return fetch_m4_cabin_telemetry()

@router.get("/alerts", response_model=List[HazardAlertResponse])
def get_alerts(
    acknowledged: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    return list_hazard_alerts(db=db, acknowledged=acknowledged)

@router.post("/alerts/{alert_id}/acknowledge", response_model=HazardAlertResponse)
def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    alert = acknowledge_hazard_alert(db=db, alert_id=alert_id, req=payload)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Hazard alert '{alert_id}' not found.")
    return alert

