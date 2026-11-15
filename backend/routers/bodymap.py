"""
Interactive Human Body Map API Router (Module 2)
Provides anatomical subsystem telemetry associations, system status, related alerts,
and mandatory evidence-based medical disclaimers.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
import crud
from schemas import BodyRegionDetailResponse

router = APIRouter(prefix="/api/astronauts/{astronaut_id}/body-map", tags=["Interactive Body Map (Module 2)"])

REGIONS_METADATA = {
    "brain": {
        "label": "Brain & Eyes (Neuro-Cognitive)",
        "subsystems": ["Neuro-Cognitive Performance", "Circadian Rhythm Equilibrium", "Visual Acuity"],
        "associatedMetrics": ["sleep", "stress"],
        "description": "Monitors sleep duration, fatigue debt, intracranial cephalad fluid shifts, and autonomic stress.",
        "disclaimer": "Biometric signals correlated with neuro-cognitive monitoring; this is not a diagnostic intracranial scan."
    },
    "heart": {
        "label": "Cardiovascular (Heart)",
        "subsystems": ["Cardiac Myocardium", "Sinus Rhythm Autonomic Balance", "Hemodynamic Perfusion"],
        "associatedMetrics": ["heartRate", "hrv", "bloodPressure"],
        "description": "Evaluates cardiac chronotropic response, vagal parasympathetic reserve (HRV), and systemic arterial pressure.",
        "disclaimer": "Fluid shifts in microgravity alter stroke volume. Deviations require standardized rest-state confirmation."
    },
    "lungs": {
        "label": "Respiratory (Lungs)",
        "subsystems": ["Gas Diffusion Efficiency", "Arterial O2 Saturation", "Cabin CO2 Compensation"],
        "associatedMetrics": ["spo2"],
        "description": "Tracks peripheral hemoglobin oxygenation (SpO2) cross-referenced against cabin environmental CO2 levels.",
        "disclaimer": "Low SpO2 triggers respiratory escalation but requires sensor probe verification to distinguish artifact from pathology."
    },
    "metabolic": {
        "label": "Metabolic & Renal",
        "subsystems": ["Glycemic Regulation", "Electrolyte Hydration Balance", "Core Thermoregulation"],
        "associatedMetrics": ["glucose", "hydration", "temperature"],
        "description": "Supervises caloric metabolism, bioimpedance hydration estimates, and deep-body core temperature.",
        "disclaimer": "Hydration indexes represent bioelectrical estimation models; not an automated diagnosis of renal dysfunction."
    },
    "musculoskeletal": {
        "label": "Musculoskeletal",
        "subsystems": ["Neuromuscular Integrity", "Bone Mineral Density", "Countermeasure Exercise Compliance"],
        "associatedMetrics": ["temperature"],
        "description": "Observes core thermogenic output, deep tissue strain, and microgravity neuromuscular deconditioning.",
        "disclaimer": "Extensor muscle atrophy and calcium loss in microgravity require daily countermeasure exercise."
    },
    "immune": {
        "label": "Immune & Hematologic",
        "subsystems": ["Cellular Immunity Reserve", "Latent Viral Reactivation Risk", "Radiation Vulnerability"],
        "associatedMetrics": ["temperature", "stress"],
        "description": "Monitors peripheral fever spikes, persistent inflammatory stress biomarkers, and radiation vulnerability.",
        "disclaimer": "Immune dysregulation indicators represent observational risk trends; laboratory blood analysis required for diagnosis."
    }
}


@router.get("", response_model=Dict[str, Any])
def get_full_body_map(astronaut_id: str):
    """
    Retrieve aggregate status across all 6 anatomical systems for the selected astronaut.
    """
    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Astronaut '{astronaut_id}' not found.")

    readings = crud.get_latest_readings_by_astronaut(astronaut_id)
    alerts = crud.get_alerts(astronaut_id=astronaut_id, status="ACTIVE")

    # Determine region status
    system_overview = {}
    for region_id, meta in REGIONS_METADATA.items():
        if astro["status"] == "NO_DATA":
            reg_status = "NO_DATA"
        else:
            # Check if any associated metric is critical or warning
            has_crit = any(readings.get(m, {}).get("severity") == "CRITICAL" for m in meta["associatedMetrics"])
            has_warn = any(readings.get(m, {}).get("severity") == "WARNING" for m in meta["associatedMetrics"])
            has_nodata = all(readings.get(m, {}).get("value") is None for m in meta["associatedMetrics"])

            if has_crit:
                reg_status = "CRITICAL"
            elif has_warn:
                reg_status = "WARNING"
            elif has_nodata:
                reg_status = "NO_DATA"
            else:
                reg_status = "NORMAL"

        system_overview[region_id] = {
            "label": meta["label"],
            "status": reg_status,
            "associatedMetricsCount": len(meta["associatedMetrics"]),
            "activeAlertsCount": len([a for a in alerts if any(m in [x["name"].lower() for x in a["contributing_measurements"]] for m in meta["associatedMetrics"])]),
        }

    return {
        "astronautId": astronaut_id,
        "name": astro["name"],
        "overallStatus": astro["status"],
        "regions": system_overview
    }


@router.get("/{region_id}", response_model=BodyRegionDetailResponse)
def get_body_region_detail(astronaut_id: str, region_id: str):
    """
    Retrieve in-depth telemetry for a specific anatomical system, including associated biometrics,
    current readings, active triage alerts, and non-diagnostic disclaimers.
    """
    reg_key = region_id.lower()
    if reg_key not in REGIONS_METADATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anatomical region '{region_id}' not recognized. Supported: {list(REGIONS_METADATA.keys())}"
        )

    astro = crud.get_astronaut(astronaut_id)
    if not astro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Astronaut '{astronaut_id}' not found.")

    meta = REGIONS_METADATA[reg_key]
    readings = crud.get_latest_readings_by_astronaut(astronaut_id)
    region_readings = {m: readings.get(m) for m in meta["associatedMetrics"] if m in readings}

    # Filter alerts related to this body region's metrics
    all_alerts = crud.get_alerts(astronaut_id=astronaut_id, status="ACTIVE")
    related_alerts = []
    for alert in all_alerts:
        for contrib in alert["contributing_measurements"]:
            if any(m.lower() in contrib["name"].lower() for m in meta["associatedMetrics"]):
                related_alerts.append(alert)
                break

    # Determine status
    if astro["status"] == "NO_DATA":
        reg_status = "NO_DATA"
    elif any(r.get("severity") == "CRITICAL" for r in region_readings.values() if r):
        reg_status = "CRITICAL"
    elif any(r.get("severity") == "WARNING" for r in region_readings.values() if r):
        reg_status = "WARNING"
    elif not region_readings or all(r.get("value") is None for r in region_readings.values() if r):
        reg_status = "NO_DATA"
    else:
        reg_status = "NORMAL"

    return {
        "regionId": reg_key,
        "label": meta["label"],
        "status": reg_status,
        "subsystems": meta["subsystems"],
        "associatedMetrics": meta["associatedMetrics"],
        "currentReadings": region_readings,
        "activeAlerts": related_alerts,
        "description": meta["description"],
        "disclaimer": meta["disclaimer"],
    }
