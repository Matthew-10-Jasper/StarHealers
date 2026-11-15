from typing import List, Dict, Any, Optional
from app.modules.module4_mission_intelligence.database.session import SessionLocal
from app.modules.module4_mission_intelligence.api.endpoints import (
    get_current_mission_context,
    list_missions as m4_list_missions,
    get_mission_history as m4_get_history,
    get_current_deviations as m4_get_deviations
)

class Module4Adapter:
    """Adapter exposing Module 4 Mission Context Intelligence to the unified platform."""

    @staticmethod
    def get_current_context() -> Dict[str, Any]:
        with SessionLocal() as db:
            ctx = get_current_mission_context(db=db)
            return ctx.model_dump()

    @staticmethod
    def list_missions() -> List[Dict[str, Any]]:
        missions = m4_list_missions()
        return [m.model_dump() for m in missions]

    @staticmethod
    def get_history() -> Dict[str, Any]:
        with SessionLocal() as db:
            hist = m4_get_history(db=db)
            return hist.model_dump()

    @staticmethod
    def get_deviations() -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            devs = m4_get_deviations(db=db)
            return [d.model_dump() for d in devs]

module4_adapter = Module4Adapter()
