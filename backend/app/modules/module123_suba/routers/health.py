"""
Health Monitoring API Router (Module 1 - Core Vitals & Telemetry)
Provides endpoints to retrieve latest 9 physiological readings, time-series historical data,
and ingest newly observed or simulated telemetry packets.
"""

import uuid
from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.modules.module123_suba import crud
from app.modules.module123_suba.schemas import HealthReadingCreate, MetricReadingItem, HistoricalDataPoint

router = APIRouter(prefix="/api/astronauts/{astronaut_id}/health", tags=["Health Monitoring (Module 1)"])


@router.get("", response_model=Dict[str, MetricReadingItem])
def get_latest_health_vitals(astronaut_id: str):
    """
    Retrieve current readings across all 9 monitored physiological parameters for the astronaut.
    Handles missing telemetry gracefully by reporting NO_DATA without defaulting to zero.
    """
    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Astronaut '{astronaut_id}' not found."
        )

    readings = crud.get_latest_readings_by_astronaut(astronaut_id)
    return readings


@router.get("/history", response_model=List[HistoricalDataPoint])
def get_health_history(
    astronaut_id: str,
    time_range: str = Query("24h", description="Time window: 1h, 24h, 7d, full"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Retrieve historical time-series telemetry packets for Recharts data visualization.
    """
    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Astronaut '{astronaut_id}' not found."
        )

    records = crud.get_historical_telemetry(astronaut_id, limit=limit)
    return records


@router.post("/readings", status_code=status.HTTP_201_CREATED)
def post_health_reading(astronaut_id: str, payload: HealthReadingCreate):
    """
    Ingest a new physiological measurement with mandatory source provenance and data quality status.
    """
    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Astronaut '{astronaut_id}' not found."
        )

    reading_id = payload.reading_id or f"R-{uuid.uuid4().hex[:8].upper()}"
    ts = payload.timestamp or (datetime.utcnow().isoformat() + "Z")

    created = crud.insert_health_reading(
        reading_id=reading_id,
        astronaut_id=astronaut_id,
        metric_name=payload.metric_name,
        value=payload.value,
        secondary_value=payload.secondary_value,
        unit=payload.unit,
        source=payload.source,
        quality_status=payload.quality_status,
        severity=payload.severity,
        timestamp=ts
    )

    return {
        "success": True,
        "message": f"Successfully ingested {payload.metric_name} reading for {astronaut_id}",
        "reading": created
    }
