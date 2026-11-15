"""
Missions API Router
Provides endpoints to list space missions and inspect environmental life support telemetry.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import crud
from schemas import MissionResponse, MissionEnvironment

router = APIRouter(prefix="/api/missions", tags=["Missions"])


def _format_mission(m: dict) -> dict:
    return {
        "mission_id": m["mission_id"],
        "name": m["name"],
        "target": m["target"],
        "phase": m["phase"],
        "commsDelaySec": m["comms_delay_sec"],
        "status": m["status"],
        "environment": {
            "cabinCo2": m["cabin_co2"],
            "cabinO2": m["cabin_o2"],
            "cabinPressure": m["cabin_pressure"],
            "ambientTemp": m["ambient_temp"],
            "radiationDoseRate": m["radiation_dose_rate"],
            "gravityG": m["gravity_g"],
        }
    }


@router.get("", response_model=List[MissionResponse])
def list_missions():
    """Retrieve all operational space missions (ISS, Moon Artemis, Mars Ares)."""
    raw_missions = crud.get_missions()
    return [_format_mission(m) for m in raw_missions]


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: str):
    """Retrieve detailed telemetry and communication delay specs for a given mission."""
    m = crud.get_mission(mission_id)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with ID '{mission_id}' not found."
        )
    return _format_mission(m)
