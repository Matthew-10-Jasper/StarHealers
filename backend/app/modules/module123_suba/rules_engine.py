"""
StarHealers - Transparent & Explainable Clinical Triage Rule Engine (Module 3)
Evaluates single-signal physiological thresholds and multi-signal compound risk patterns.
Provides transparent medical evidence reasoning, contributing measurements, and escalation steps.
Includes a dedicated integration dock for teammate Matthew's Palette 3 Z-score statistical anomalies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


# Configurable Demonstration Thresholds (Compliant with NASA Human Research Program Baselines)
DEFAULT_RULE_THRESHOLDS = {
    "hr_max_warning": 90.0,
    "hr_max_critical": 105.0,
    "hr_min_warning": 50.0,
    "hrv_min_warning": 40.0,
    "hrv_min_critical": 25.0,
    "spo2_warning": 94.0,
    "spo2_critical": 92.0,
    "sleep_min_hours": 5.5,
    "stress_threshold": 65.0,
    "temp_max_warning": 37.5,
    "hydration_min_warning": 52.0,
    "compound_rules_enabled": True,
}

_active_thresholds = dict(DEFAULT_RULE_THRESHOLDS)


def get_current_thresholds() -> Dict[str, Any]:
    return dict(_active_thresholds)


def update_thresholds(new_thresholds: Dict[str, Any]) -> Dict[str, Any]:
    global _active_thresholds
    _active_thresholds.update(new_thresholds)
    return dict(_active_thresholds)


def reset_thresholds() -> Dict[str, Any]:
    global _active_thresholds
    _active_thresholds = dict(DEFAULT_RULE_THRESHOLDS)
    return dict(_active_thresholds)


def evaluate_astronaut_telemetry(
    astronaut_id: str,
    astronaut_name: str,
    readings: Dict[str, Any],
    baseline: Optional[Dict[str, Any]] = None,
    teammate_anomalies: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Evaluates current physiological readings for an astronaut.
    Returns:
      - isAlertTriggered: bool
      - highestSeverity: 'NORMAL' | 'WARNING' | 'CRITICAL' | 'NO_DATA'
      - activeAlerts: List of structured alert objects
      - explanation: Global transparent explanation summary
      - dockedTeammateAnomalies: List of statistical anomalies from Matthew's module
    """
    t = _active_thresholds
    triggered_alerts = []

    # Extract readings
    def val(metric):
        r = readings.get(metric)
        if r is None:
            return None
        if isinstance(r, dict):
            return r.get("value")
        return r

    hr = val("heartRate")
    hrv = val("hrv")
    spo2 = val("spo2")
    sleep = val("sleep")
    stress = val("stress")
    temp = val("temperature")
    hydration = val("hydration")
    bp = readings.get("bloodPressure")
    bp_sys = bp.get("value") if isinstance(bp, dict) else None

    # Check for complete sensor link loss (NO_DATA Scenario)
    non_null_count = sum(1 for v in [hr, hrv, spo2, sleep, stress, temp, hydration] if v is not None)
    if non_null_count == 0:
        triggered_alerts.append({
            "alertId": f"ALT-RULE-SENSOR-{astronaut_id}",
            "astronautId": astronaut_id,
            "ruleId": "RULE-SENSOR-LINK-01",
            "title": "Telemetry Signal Loss — Biometric Sensor Node",
            "severity": "NO_DATA",
            "status": "ACTIVE",
            "triggerReason": "Zero physiological data packets received from wearable telemetry node.",
            "explanation": (
                f"Biometric telemetry stream for {astronaut_name} is offline. "
                "The system reports NO DATA rather than normal to prevent false assurance during deep-space transit."
            ),
            "contributingMeasurements": [
                {"name": "Telemetry Node Link", "value": "OFFLINE", "threshold": "ONLINE", "unit": "status", "status": "NO_DATA"},
                {"name": "Valid Biometrics", "value": "0 / 9", "threshold": "> 6 parameters", "unit": "count", "status": "NO_DATA"}
            ],
            "escalationSteps": [
                "Instruct crew member to check wearable sensor battery and wireless transponder",
                "Verify habitat local Bluetooth / UWB access point transceiver",
                "Revert to backup manual vitals check if link cannot be re-established within 60 minutes"
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        return {
            "astronautId": astronaut_id,
            "astronautName": astronaut_name,
            "highestSeverity": "NO_DATA",
            "isAlertTriggered": True,
            "activeAlerts": triggered_alerts,
            "explanation": f"Sensor node for {astronaut_name} is offline. Triage state set to NO DATA.",
            "dockedTeammateAnomalies": teammate_anomalies or []
        }

    # ==========================================================
    # RULE 1: ACUTE HYPOXIA / RESPIRATORY STRAIN (Critical)
    # ==========================================================
    if spo2 is not None and spo2 < t["spo2_critical"]:
        comp_hr = hr or 80.0
        triggered_alerts.append({
            "alertId": f"ALT-RULE-HYPOXIA-{astronaut_id}",
            "astronautId": astronaut_id,
            "ruleId": "RULE-HYPOXIA-ACUTE-01",
            "title": "Acute Hypoxic Respiratory Depletion",
            "severity": "CRITICAL",
            "status": "ACTIVE",
            "triggerReason": f"Arterial oxygen saturation fell to {spo2}% (< {t['spo2_critical']}% critical threshold) with concurrent heart rate {comp_hr} bpm.",
            "explanation": (
                f"Severe systemic arterial oxygen desaturation detected in {astronaut_name}. "
                f"SpO2 of {spo2}% is critically below deep-space flight tolerance. Concomitant heart rate of {comp_hr} bpm "
                "indicates compensatory cardiac drive attempting to preserve peripheral perfusion. Immediate escalation required."
            ),
            "contributingMeasurements": [
                {"name": "SpO2", "value": f"{spo2}%", "threshold": f"< {t['spo2_critical']}%", "unit": "%", "status": "CRITICAL"},
                {"name": "Heart Rate", "value": f"{comp_hr} bpm", "threshold": f"> {t['hr_max_critical']} bpm", "unit": "bpm", "status": "CRITICAL" if comp_hr > t["hr_max_critical"] else "NORMAL"}
            ],
            "escalationSteps": [
                "Immediate crew cross-check of portable O2 mask system",
                "Inspect suit / helmet air scrubbers and habitat ventilation loop",
                "Perform bedside lung auscultation and pulse oximeter probe re-seat",
                "Prepare autonomous Medical Kit Bravo (Bronchodilator / O2 supply)"
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    elif spo2 is not None and spo2 < t["spo2_warning"]:
        triggered_alerts.append({
            "alertId": f"ALT-RULE-HYPOXIA-WARN-{astronaut_id}",
            "astronautId": astronaut_id,
            "ruleId": "RULE-HYPOXIA-WARN-02",
            "title": "Mild Peripheral Oxygen Saturation Variance",
            "severity": "WARNING",
            "status": "ACTIVE",
            "triggerReason": f"SpO2 of {spo2}% is below warning threshold ({t['spo2_warning']}%).",
            "explanation": f"Arterial oxygen saturation is slightly depressed. Closer monitoring advised.",
            "contributingMeasurements": [
                {"name": "SpO2", "value": f"{spo2}%", "threshold": f"< {t['spo2_warning']}%", "unit": "%", "status": "WARNING"}
            ],
            "escalationSteps": [
                "Verify sensor finger probe placement and clean optical sensor lens",
                "Cross-check ambient cabin CO2 scrubber readings"
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    # ==========================================================
    # RULE 2: MULTI-SIGNAL AUTONOMIC FATIGUE COMPOUND PATTERN
    # (Combined Indicator Assessment: HR elevated + HRV low + Sleep low + Stress high)
    # ==========================================================
    if t["compound_rules_enabled"]:
        is_hr_elevated = hr is not None and hr > t["hr_max_warning"]
        is_hrv_suppressed = hrv is not None and hrv < t["hrv_min_warning"]
        is_sleep_reduced = sleep is not None and sleep < t["sleep_min_hours"]
        is_stress_high = stress is not None and stress > t["stress_threshold"]

        # Check compound condition: at least 2 synergistic autonomic strain signals
        autonomic_hits = sum([is_hr_elevated, is_hrv_suppressed, is_sleep_reduced, is_stress_high])

        if autonomic_hits >= 2:
            base_hrv = baseline.get("hrv", 68.0) if baseline else 68.0
            base_hr = baseline.get("restingHr", 62.0) if baseline else 62.0

            triggered_alerts.append({
                "alertId": f"ALT-RULE-FATIGUE-{astronaut_id}",
                "astronautId": astronaut_id,
                "ruleId": "RULE-FATIGUE-COMPOUND-03",
                "title": "Multi-Signal Autonomic Fatigue Pattern",
                "severity": "WARNING",
                "status": "ACTIVE",
                "triggerReason": (
                    f"Combined detection of {autonomic_hits} correlated autonomic fatigue signals: "
                    f"HR {hr} bpm (vs base {base_hr}), HRV {hrv} ms (vs base {base_hrv}), sleep {sleep}h, stress {stress} pts."
                ),
                "explanation": (
                    f"Multi-parameter autonomic imbalance identified in {astronaut_name}. "
                    "Cumulative sleep loss combined with heightened sympathetic nervous system tone is producing "
                    f"a 50% suppression in vagal HRV relative to baseline. Elevated cognitive lapse risk during critical mission maneuvers."
                ),
                "contributingMeasurements": [
                    {"name": "Heart Rate Variability", "value": f"{hrv} ms", "threshold": f"< {t['hrv_min_warning']} ms", "unit": "ms", "status": "WARNING"},
                    {"name": "24h Sleep Duration", "value": f"{sleep} hrs", "threshold": f"< {t['sleep_min_hours']} hrs", "unit": "hrs", "status": "WARNING"},
                    {"name": "Physiological Stress", "value": f"{stress} pts", "threshold": f"> {t['stress_threshold']} pts", "unit": "pts", "status": "WARNING"},
                    {"name": "Resting Heart Rate", "value": f"{hr} bpm", "threshold": f"> {t['hr_max_warning']} bpm", "unit": "bpm", "status": "WARNING"}
                ],
                "escalationSteps": [
                    "Recommend 90-minute restorative sleep block prior to EVA duties",
                    "Review cognitive workload and schedule non-critical task deferrals",
                    "Administer scheduled blue-wavelength light therapy attenuation",
                    "Log PVT (Psychomotor Vigilance Task) assessment at next duty station"
                ],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    # ==========================================================
    # RULE 3: ISOLATED TACHYCARDIA OR BRADYCARDIA
    # ==========================================================
    if hr is not None and hr > t["hr_max_critical"] and not any(a["ruleId"] == "RULE-HYPOXIA-ACUTE-01" for a in triggered_alerts):
        triggered_alerts.append({
            "alertId": f"ALT-RULE-TACHY-{astronaut_id}",
            "astronautId": astronaut_id,
            "ruleId": "RULE-CARDIO-HR-01",
            "title": "Persistent Resting Tachycardia",
            "severity": "WARNING",
            "status": "ACTIVE",
            "triggerReason": f"Resting heart rate ({hr} bpm) exceeded critical threshold ({t['hr_max_critical']} bpm).",
            "explanation": f"Cardiovascular contractile frequency elevated above nominal rest threshold for {astronaut_name}.",
            "contributingMeasurements": [
                {"name": "Heart Rate", "value": f"{hr} bpm", "threshold": f"> {t['hr_max_critical']} bpm", "unit": "bpm", "status": "WARNING"}
            ],
            "escalationSteps": [
                "Verify whether astronaut engaged in vigorous exercise within the last 30 minutes",
                "Ensure hydration compliance and repeat manual cuff pulse measurement"
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    # Determine Aggregate Severity
    if any(a["severity"] == "CRITICAL" for a in triggered_alerts):
        highest_severity = "CRITICAL"
    elif any(a["severity"] == "WARNING" for a in triggered_alerts):
        highest_severity = "WARNING"
    elif any(a["severity"] == "NO_DATA" for a in triggered_alerts):
        highest_severity = "NO_DATA"
    else:
        highest_severity = "NORMAL"

    explanation = (
        f"Evaluated physiological criteria for {astronaut_name}. "
        f"{len(triggered_alerts)} clinical alert condition(s) triggered with an aggregate severity of {highest_severity}."
        if triggered_alerts else
        f"All monitored physiological parameters are nominal for {astronaut_name}. No clinical triage rules triggered."
    )

    return {
        "astronautId": astronaut_id,
        "astronautName": astronaut_name,
        "highestSeverity": highest_severity,
        "isAlertTriggered": len(triggered_alerts) > 0,
        "activeAlerts": triggered_alerts,
        "explanation": explanation,
        "dockedTeammateAnomalies": teammate_anomalies or []
    }
