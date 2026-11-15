from typing import List, Dict, Any, Optional
from app.modules.module6_circadian_fatigue.database.session import SessionLocal
from app.modules.module6_circadian_fatigue.services.circadian_service import get_circadian_rhythm
from app.modules.module6_circadian_fatigue.services.fatigue_service import compute_fatigue_assessment
from app.modules.module6_circadian_fatigue.services.stress_service import compute_stress_monitoring
from app.modules.module6_circadian_fatigue.services.readiness_engine import calculate_cognitive_readiness

class Module6Adapter:
    """Adapter exposing Module 6 Circadian, Fatigue & Cognitive Readiness."""

    @staticmethod
    def get_readiness(astronaut_id: str) -> Dict[str, Any]:
        # Cross-module correlation using Module 6 engine
        res = calculate_cognitive_readiness(astronaut_id=astronaut_id)
        return res.model_dump()

    @staticmethod
    def get_circadian(astronaut_id: str, mission_hour: float = 72.0) -> Dict[str, Any]:
        res = get_circadian_rhythm(astronaut_id=astronaut_id, mission_elapsed_hours=mission_hour)
        return res.model_dump()

    @staticmethod
    def get_fatigue(astronaut_id: str) -> Dict[str, Any]:
        res = compute_fatigue_assessment(astronaut_id=astronaut_id)
        return res.model_dump()

    @staticmethod
    def get_stress(astronaut_id: str) -> Dict[str, Any]:
        res = compute_stress_monitoring(astronaut_id=astronaut_id)
        return res.model_dump()

module6_adapter = Module6Adapter()
