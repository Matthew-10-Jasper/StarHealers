from typing import List, Dict, Any, Optional
from app.modules.module7_space_environment.database.session import SessionLocal
from app.modules.module7_space_environment.services.environmental_engine import compute_composite_risk
from app.modules.module7_space_environment.services.m5_consumer import get_radiation_overview, get_co2_overview
from app.modules.module7_space_environment.services.m4_consumer import fetch_m4_cabin_telemetry
from app.modules.module7_space_environment.services.alert_service import list_hazard_alerts

class Module7Adapter:
    """Adapter exposing Module 7 Space Environment, Radiation & Life Support."""

    @staticmethod
    def get_composite_risk() -> Dict[str, Any]:
        with SessionLocal() as db:
            risk = compute_composite_risk(db=db)
            return risk.model_dump()

    @staticmethod
    def get_radiation(mission_hours: float = 72.0, has_spe: bool = True) -> Dict[str, Any]:
        rad = get_radiation_overview(mission_hours=mission_hours, has_active_spe=has_spe)
        return rad.model_dump()

    @staticmethod
    def get_co2(mission_hours: float = 72.0, degraded: bool = True) -> Dict[str, Any]:
        co2 = get_co2_overview(mission_hours=mission_hours, scrubber_degraded=degraded)
        return co2.model_dump()

    @staticmethod
    def get_cabin() -> Dict[str, Any]:
        cab = fetch_m4_cabin_telemetry()
        return cab.model_dump()

    @staticmethod
    def get_alerts() -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            alerts = list_hazard_alerts(db=db)
            return [a.model_dump() for a in alerts]

module7_adapter = Module7Adapter()
