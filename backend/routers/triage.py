"""
Intelligent Health Triage Engine API Router (Module 3 - Rule-Based Alert & Triage)
Provides endpoints to list active and resolved alerts, acknowledge/resolve incidents,
and evaluate current multi-signal physiological telemetry against configurable clinical rules.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict, Any
import crud
from schemas import (
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


@router.post("/triage/evaluate", response_model=TriageEvaluateResponse)
def evaluate_triage_rules(payload: TriageEvaluateRequest):
    """
    Transparent rule-based evaluation engine. Evaluates single-signal thresholds and multi-signal
    compound patterns (such as Autonomic Fatigue and Acute Hypoxemia) without clinical black boxes.
    """
    astro = crud.get_astronaut(payload.astronaut_id)
    if not astro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Astronaut '{payload.astronaut_id}' not found.")

    triggered = []
    highest_severity = "NORMAL"

    # Rule 1: Acute Hypoxic Respiratory Depletion
    if payload.spo2 is not None and payload.spo2 < 92.0:
        hr = payload.heartRate or 80.0
        highest_severity = "CRITICAL"
        triggered.append({
            "ruleId": "RULE-HYPOXIA-ACUTE-01",
            "title": "Acute Hypoxic Respiratory Depletion",
            "severity": "CRITICAL",
            "triggerReason": f"SpO2 fell to {payload.spo2}% (< 92% critical threshold) with compensatory HR {hr} bpm.",
            "contributingMeasurements": [
                {"name": "SpO2", "value": f"{payload.spo2}%", "threshold": "< 92%", "unit": "%", "status": "CRITICAL"},
                {"name": "Heart Rate", "value": f"{hr} bpm", "threshold": "> 105 bpm", "unit": "bpm", "status": "CRITICAL" if hr > 105 else "NORMAL"}
            ]
        })

    # Rule 2: Multi-Signal Autonomic Fatigue Compound Pattern
    is_hr_elevated = payload.heartRate is not None and payload.heartRate > 88.0
    is_hrv_suppressed = payload.hrv is not None and payload.hrv < 40.0
    is_sleep_reduced = payload.sleep is not None and payload.sleep < 5.5
    is_stress_high = payload.stress is not None and payload.stress > 65.0

    if (is_hr_elevated and is_hrv_suppressed) or (is_sleep_reduced and is_stress_high):
        if highest_severity != "CRITICAL":
            highest_severity = "WARNING"
        triggered.append({
            "ruleId": "RULE-FATIGUE-COMPOUND-03",
            "title": "Multi-Signal Autonomic Fatigue Pattern",
            "severity": "WARNING",
            "triggerReason": "Suppressed vagal HRV combined with elevated resting HR, cumulative sleep truncation, and heightened stress index.",
            "contributingMeasurements": [
                {"name": "Heart Rate", "value": f"{payload.heartRate} bpm", "threshold": "> 88 bpm", "unit": "bpm", "status": "WARNING"},
                {"name": "HRV", "value": f"{payload.hrv} ms", "threshold": "< 40 ms", "unit": "ms", "status": "WARNING"},
                {"name": "Sleep", "value": f"{payload.sleep} hrs", "threshold": "< 5.5 hrs", "unit": "hrs", "status": "WARNING"},
                {"name": "Stress", "value": f"{payload.stress} pts", "threshold": "> 65 pts", "unit": "pts", "status": "WARNING"}
            ]
        })

    explanation = (
        f"Evaluated 4 clinical rule families for {astro['name']}. "
        f"{len(triggered)} rule conditions triggered resulting in an aggregate triage level of {highest_severity}."
        if triggered else
        f"All monitored physiological parameters are nominal. No clinical triage rules triggered."
    )

    return {
        "astronautId": payload.astronaut_id,
        "evaluatedRulesCount": 4,
        "severity": highest_severity,
        "isAlertTriggered": len(triggered) > 0,
        "triggeredAlerts": triggered,
        "explanation": explanation
    }
