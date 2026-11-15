from typing import List, Dict, Any, Optional
from app.modules.module123_suba import crud
from app.modules.module123_suba.schemas import (
    AstronautResponse,
    MetricReadingItem,
    TriageAlertResponse,
    MissionResponse
)

class SubaModuleAdapter:
    """Adapter interface exposing Suba Modules 1-3 to the unified platform."""

    @staticmethod
    def get_astronauts() -> List[Dict[str, Any]]:
        return crud.get_astronauts()

    @staticmethod
    def get_astronaut(astronaut_id: str) -> Optional[Dict[str, Any]]:
        return crud.get_astronaut(astronaut_id)

    @staticmethod
    def get_latest_vitals(astronaut_id: str) -> Dict[str, Any]:
        return crud.get_latest_readings_by_astronaut(astronaut_id)

    @staticmethod
    def get_vitals_history(astronaut_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return crud.get_historical_telemetry(astronaut_id)

    @staticmethod
    def get_triage_alerts(status: Optional[str] = None) -> List[Dict[str, Any]]:
        return crud.get_alerts(status=status)

    @staticmethod
    def get_astronaut_alerts(astronaut_id: str) -> List[Dict[str, Any]]:
        alerts = crud.get_alerts()
        return [a for a in alerts if a.get("astronaut_id") == astronaut_id]

    @staticmethod
    def get_missions() -> List[Dict[str, Any]]:
        return crud.get_missions()

module123_adapter = SubaModuleAdapter()
