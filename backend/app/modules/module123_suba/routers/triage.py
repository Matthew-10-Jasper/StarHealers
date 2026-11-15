"""
Intelligent Health Triage Engine API Router (Module 3 - Rule-Based Alert & Triage)
Provides endpoints to list active and resolved alerts, configure demonstration medical rules,
acknowledge/resolve incidents, and execute multi-signal explainable triage evaluations.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from app.modules.module123_suba import crud
from app.modules.module123_suba import rules_engine
from app.modules.module123_suba.schemas import (
    TriageAlertResponse,
    AlertResolutionRequest,
    TriageEvaluateRequest,
    TriageEvaluateResponse
)

router = APIRouter(prefix="/api", tags=["Triage & Alerts (Module 3)"])


def _format_alert(a: dict) -> dict:
    return {
        "alert_id": a["alert_id"],
        "astronaut_id": a["astronaut_id"],
        "rule_id": a["rule_id"],
        "title": a["title"],
        "severity": a["severity"],
        "status": a["status"],
        "trigger_reason": a["trigger_reason"],
        "explanation": a["explanation"],
        "contributing_measurements": a["contributing_measurements"],
        "escalation_steps": a["escalation_steps"],
        "timestamp": a["timestamp"],
        "acknowledged_by": a.get("acknowledged_by"),
        "resolved_at": a.get("resolved_at"),
    }


@router.get("/alerts", response_model=List[TriageAlertResponse])
def list_all_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="ACTIVE or RESOLVED"),
    severity: Optional[str] = Query(None, description="CRITICAL, WARNING, NORMAL, NO_DATA"),
    astronaut_id: Optional[str] = Query(None, description="Filter by astronaut ID")
):
    """List triage alerts across all crew members with optional status and severity filtering."""
    raw = crud.get_alerts(astronaut_id=astronaut_id, status=status_filter, severity=severity)
    return [_format_alert(a) for a in raw]


@router.get("/astronauts/{astronaut_id}/alerts", response_model=List[TriageAlertResponse])
def get_alerts_by_astronaut(
    astronaut_id: str,
    status_filter: Optional[str] = Query(None, alias="status")
):
    """Retrieve all triage alerts for a specific astronaut."""
    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Astronaut '{astronaut_id}' not found.")
    raw = crud.get_alerts(astronaut_id=astronaut_id, status=status_filter)
    return [_format_alert(a) for a in raw]


@router.get("/alerts/{alert_id}", response_model=TriageAlertResponse)
def get_alert_detail(alert_id: str):
    """Retrieve full clinical reasoning, contributing measurements, and escalation steps for an alert."""
    a = crud.get_alert_by_id(alert_id)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert '{alert_id}' not found.")
    return _format_alert(a)


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert_endpoint(alert_id: str, payload: AlertResolutionRequest):
    """Acknowledge or resolve an active triage incident, recording medical officer audit trail."""
    a = crud.get_alert_by_id(alert_id)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert '{alert_id}' not found.")

    success = crud.resolve_alert(alert_id=alert_id, user_id=payload.user_id)
    return {
        "success": success,
        "message": f"Alert '{alert_id}' marked as RESOLVED by {payload.user_id}",
        "alert_id": alert_id,
        "status": "RESOLVED"
    }


# ==========================================
# RULE ENGINE CONFIGURATION ENDPOINTS
# ==========================================

@router.get("/triage/rules")
def get_configured_rules():
    """Retrieve current clinical thresholds and active rule configurations."""
    return {
        "thresholds": rules_engine.get_current_thresholds(),
        "disclaimer": "Thresholds represent demonstration parameters aligned with NASA Flight Rule medical guidelines."
    }


@router.post("/triage/rules")
def update_configured_rules(thresholds: Dict[str, Any]):
    """Update configurable clinical rule thresholds."""
    updated = rules_engine.update_thresholds(thresholds)
    return {
        "success": True,
        "message": "Clinical rule thresholds updated successfully",
        "thresholds": updated
    }


@router.post("/triage/rules/reset")
def reset_configured_rules():
    """Reset all clinical rule thresholds to NASA baseline standards."""
    resetted = rules_engine.reset_thresholds()
    return {
        "success": True,
        "message": "Reset to NASA standard thresholds complete",
        "thresholds": resetted
    }


# ==========================================
# RULE EVALUATION ENDPOINT
# ==========================================

@router.post("/triage/evaluate", response_model=TriageEvaluateResponse)
def evaluate_triage_rules(payload: TriageEvaluateRequest):
    """
    Transparent rule-based evaluation engine. Evaluates single-signal thresholds and multi-signal
    compound patterns (such as Autonomic Fatigue and Acute Hypoxemia) without clinical black boxes.
    """
    astro = crud.get_astronaut(payload.astronaut_id)
    if not astro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Astronaut '{payload.astronaut_id}' not found.")

    readings = {
        "heartRate": payload.heartRate,
        "hrv": payload.hrv,
        "spo2": payload.spo2,
        "sleep": payload.sleep,
        "stress": payload.stress,
        "temperature": payload.temperature,
        "hydration": payload.hydration,
    }

    baseline = {
        "restingHr": astro["baseline_resting_hr"],
        "hrv": astro["baseline_hrv"],
        "spo2": astro["baseline_spo2"],
    }

    result = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id=payload.astronaut_id,
        astronaut_name=astro["name"],
        readings=readings,
        baseline=baseline,
    )

    return {
        "astronautId": payload.astronaut_id,
        "evaluatedRulesCount": 4,
        "severity": result["highestSeverity"],
        "isAlertTriggered": result["isAlertTriggered"],
        "triggeredAlerts": result["activeAlerts"],
        "explanation": result["explanation"]
    }
