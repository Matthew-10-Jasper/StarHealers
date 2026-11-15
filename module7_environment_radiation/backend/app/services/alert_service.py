from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import HazardAlertModel
from app.schemas.schemas import HazardAlertResponse, AlertAcknowledgeRequest

DEFAULT_ALERTS = [
    {
        "alert_id": "HAZ-RAD-SPE-01",
        "hazard_type": "RADIATION",
        "severity": "WARNING",
        "message": "SPE Solar Particle Event in progress. Hourly dose rate elevated to 0.42 mSv/h. Crew recommended to stay near radiation storm shelter.",
        "source_module": "MODULE_5_RADIATION",
        "acknowledged": False
    },
    {
        "alert_id": "HAZ-CO2-SCRUB-02",
        "hazard_type": "CO2",
        "severity": "WARNING",
        "message": "Cabin ppCO2 approaching 3.2 mmHg. Scrubber Bed 2 cycle efficiency reduced to 58%. Consider manual desiccant canister flush.",
        "source_module": "MODULE_5_CO2",
        "acknowledged": False
    },
    {
        "alert_id": "HAZ-ENV-PARTIAL-03",
        "hazard_type": "CABIN_PRESSURE",
        "severity": "INFO",
        "message": "Cabin pressure verified nominal at 70.3 kPa. Secondary sensors (O2, Temp) awaiting telemetry link synchronization.",
        "source_module": "MODULE_4_INTELLIGENCE",
        "acknowledged": False
    }
]

def seed_alerts_if_empty(db: Session):
    count = db.query(HazardAlertModel).count()
    if count == 0:
        for a in DEFAULT_ALERTS:
            db.add(HazardAlertModel(**a))
        db.commit()

def list_hazard_alerts(db: Session, acknowledged: Optional[bool] = None) -> List[HazardAlertResponse]:
    seed_alerts_if_empty(db)
    query = db.query(HazardAlertModel)
    if acknowledged is not None:
        query = query.filter(HazardAlertModel.acknowledged == acknowledged)
    records = query.order_by(HazardAlertModel.created_at.desc()).all()
    
    return [
        HazardAlertResponse(
            alert_id=r.alert_id,
            hazard_type=r.hazard_type,
            severity=r.severity,
            message=r.message,
            source_module=r.source_module,
            acknowledged=r.acknowledged,
            acknowledged_by=r.acknowledged_by,
            acknowledged_at=r.acknowledged_at,
            created_at=r.created_at
        ) for r in records
    ]

def acknowledge_hazard_alert(db: Session, alert_id: str, req: AlertAcknowledgeRequest) -> HazardAlertResponse:
    seed_alerts_if_empty(db)
    alert = db.query(HazardAlertModel).filter(HazardAlertModel.alert_id == alert_id).first()
    if not alert:
        return None
        
    alert.acknowledged = True
    alert.acknowledged_by = req.acknowledged_by
    alert.acknowledged_at = datetime.now(timezone.utc)
    if req.notes:
        alert.message += f" [Ack Note: {req.notes}]"
    db.commit()
    db.refresh(alert)
    
    return HazardAlertResponse(
        alert_id=alert.alert_id,
        hazard_type=alert.hazard_type,
        severity=alert.severity,
        message=alert.message,
        source_module=alert.source_module,
        acknowledged=alert.acknowledged,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        created_at=alert.created_at
    )

