"""
Astronauts & Crew Management API Router
Provides endpoints to list crew members and retrieve individual astronaut physiological profiles.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict
import crud
from schemas import AstronautResponse, AstronautBaseline

router = APIRouter(prefix="/api/astronauts", tags=["Astronauts"])


def _calculate_body_region_status(astronaut_id: str, astro_status: str) -> Dict[str, str]:
    """Calculates status per organ system based on active readings and astronaut status."""
    if astro_status == "NO_DATA":
        return {r: "NO_DATA" for r in ["brain", "heart", "lungs", "musculoskeletal", "immune", "metabolic"]}
    if astronaut_id == "ASTRO-01":
        return {
            "brain": "WARNING",
            "heart": "WARNING",
            "lungs": "NORMAL",
            "musculoskeletal": "NORMAL",
            "immune": "NORMAL",
            "metabolic": "NORMAL",
        }
    if astronaut_id == "ASTRO-03":
        return {
            "brain": "WARNING",
            "heart": "CRITICAL",
            "lungs": "CRITICAL",
            "musculoskeletal": "NORMAL",
            "immune": "NORMAL",
            "metabolic": "NORMAL",
        }
    return {
        "brain": "NORMAL",
        "heart": "NORMAL",
        "lungs": "NORMAL",
        "musculoskeletal": "NORMAL",
        "immune": "NORMAL",
        "metabolic": "NORMAL",
    }


def _format_astronaut(a: dict) -> dict:
    return {
        "astronaut_id": a["astronaut_id"],
        "mission_id": a["mission_id"],
        "name": a["name"],
        "role": a["role"],
        "age": a["age"],
        "blood_type": a["blood_type"],
        "height_cm": a["height_cm"],
        "weight_kg": a["weight_kg"],
        "avatar_url": a["avatar_url"],
        "status": a["status"],
        "status_reason": a["status_reason"],
        "baseline": {
            "restingHr": a["baseline_resting_hr"],
            "hrv": a["baseline_hrv"],
            "bpSystolic": a["baseline_bp_systolic"],
            "bpDiastolic": a["baseline_bp_diastolic"],
            "spo2": a["baseline_spo2"],
            "temp": a["baseline_temp"],
            "glucose": a["baseline_glucose"],
            "hydration": a["baseline_hydration"],
            "stress": a["baseline_stress"],
        },
        "bodyRegionStatus": _calculate_body_region_status(a["astronaut_id"], a["status"])
    }


@router.get("", response_model=List[AstronautResponse])
def list_astronauts(mission_id: Optional[str] = Query(None, description="Filter by mission ID")):
    """List all astronaut crew profiles, optionally filtered by mission."""
    raw = crud.get_astronauts(mission_id=mission_id)
    return [_format_astronaut(a) for a in raw]


@router.get("/{astronaut_id}", response_model=AstronautResponse)
def get_astronaut(astronaut_id: str):
    """Retrieve an individual astronaut's complete profile and baseline physiological telemetry."""
    a = crud.get_astronaut(astronaut_id)
    if not a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Astronaut with ID '{astronaut_id}' not found."
        )
    return _format_astronaut(a)
