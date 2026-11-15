"""
StarHealers - Module 3 Rule Engine Scenario Verification Suite
Systematically tests all 5 required clinical demonstration scenarios:
1. Normal Scenario
2. Warning Scenario
3. Critical Scenario
4. Missing Data Scenario
5. Combined-Signal Scenario
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import rules_engine


def run_scenario_tests():
    print("=" * 65, flush=True)
    print("STARHEALERS MODULE 3 - RULE ENGINE SCENARIO VERIFICATION")
    print("=" * 65, flush=True)

    # SCENARIO 1: NORMAL SCENARIO (Nominal astronaut telemetry)
    print("\n[SCENARIO 1] Testing Normal Physiological Scenario...", flush=True)
    normal_readings = {
        "heartRate": 64.0,
        "hrv": 76.0,
        "spo2": 99.0,
        "sleep": 7.9,
        "stress": 22.0,
        "temperature": 36.6,
        "hydration": 63.0,
    }
    res_normal = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id="ASTRO-02",
        astronaut_name="Cmdr. Marcus Vance",
        readings=normal_readings
    )
    assert res_normal["highestSeverity"] == "NORMAL", f"Expected NORMAL, got {res_normal['highestSeverity']}"
    assert res_normal["isAlertTriggered"] is False, "Expected no alerts triggered"
    assert len(res_normal["activeAlerts"]) == 0
    print("  -> PASS: Normal scenario verified (Severity: NORMAL, 0 alerts triggered)", flush=True)

    # SCENARIO 2: WARNING SCENARIO (Elevated Resting Heart Rate)
    print("\n[SCENARIO 2] Testing Warning Scenario (Tachycardia)...", flush=True)
    warning_readings = {
        "heartRate": 108.0,
        "hrv": 55.0,
        "spo2": 98.0,
        "sleep": 7.0,
        "stress": 30.0,
        "temperature": 36.7,
        "hydration": 60.0,
    }
    res_warning = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id="ASTRO-02",
        astronaut_name="Cmdr. Marcus Vance",
        readings=warning_readings
    )
    assert res_warning["highestSeverity"] == "WARNING", f"Expected WARNING, got {res_warning['highestSeverity']}"
    assert res_warning["isAlertTriggered"] is True
    tachy_alert = next((a for a in res_warning["activeAlerts"] if a["ruleId"] == "RULE-CARDIO-HR-01"), None)
    assert tachy_alert is not None
    print(f"  -> PASS: Warning scenario verified (Alert: '{tachy_alert['title']}')", flush=True)

    # SCENARIO 3: CRITICAL SCENARIO (Acute Hypoxemia with Compensatory Tachycardia)
    print("\n[SCENARIO 3] Testing Critical Scenario (Acute Hypoxia)...", flush=True)
    critical_readings = {
        "heartRate": 114.0,
        "hrv": 24.0,
        "spo2": 89.0,
        "sleep": 6.0,
        "stress": 80.0,
        "temperature": 37.4,
        "hydration": 55.0,
    }
    res_crit = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id="ASTRO-03",
        astronaut_name="Dr. Elena Rostova",
        readings=critical_readings
    )
    assert res_crit["highestSeverity"] == "CRITICAL", f"Expected CRITICAL, got {res_crit['highestSeverity']}"
    assert res_crit["isAlertTriggered"] is True
    hypo_alert = next((a for a in res_crit["activeAlerts"] if a["ruleId"] == "RULE-HYPOXIA-ACUTE-01"), None)
    assert hypo_alert is not None
    print(f"  -> PASS: Critical scenario verified (Alert: '{hypo_alert['title']}')", flush=True)
    print(f"     Reasoning: {hypo_alert['triggerReason']}")

    # SCENARIO 4: MISSING-DATA SCENARIO (Sensor Link Offline / Packet Loss)
    print("\n[SCENARIO 4] Testing Missing-Data Scenario (Sensor Node Disconnected)...", flush=True)
    missing_readings = {
        "heartRate": None,
        "hrv": None,
        "spo2": None,
        "sleep": None,
        "stress": None,
        "temperature": None,
        "hydration": None,
    }
    res_nodata = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id="ASTRO-04",
        astronaut_name="Alex Tanaka",
        readings=missing_readings
    )
    assert res_nodata["highestSeverity"] == "NO_DATA", f"Expected NO_DATA, got {res_nodata['highestSeverity']}"
    assert res_nodata["isAlertTriggered"] is True
    sensor_alert = next((a for a in res_nodata["activeAlerts"] if a["ruleId"] == "RULE-SENSOR-LINK-01"), None)
    assert sensor_alert is not None
    print(f"  -> PASS: Missing-data scenario verified (Alert: '{sensor_alert['title']}')", flush=True)
    print(f"     Explanation: {sensor_alert['explanation']}")

    # SCENARIO 5: COMBINED-SIGNAL SCENARIO (Multi-Signal Autonomic Fatigue Compound Pattern)
    print("\n[SCENARIO 5] Testing Multi-Signal Combined Pattern Scenario...", flush=True)
    compound_readings = {
        "heartRate": 96.0,
        "hrv": 32.0,
        "spo2": 97.0,
        "sleep": 4.5,
        "stress": 74.0,
        "temperature": 37.1,
        "hydration": 58.0,
    }
    res_compound = rules_engine.evaluate_astronaut_telemetry(
        astronaut_id="ASTRO-01",
        astronaut_name="Dr. Sarah Chen",
        readings=compound_readings,
        baseline={"restingHr": 62.0, "hrv": 68.0}
    )
    assert res_compound["highestSeverity"] == "WARNING", f"Expected WARNING, got {res_compound['highestSeverity']}"
    assert res_compound["isAlertTriggered"] is True
    fatigue_alert = next((a for a in res_compound["activeAlerts"] if a["ruleId"] == "RULE-FATIGUE-COMPOUND-03"), None)
    assert fatigue_alert is not None
    assert len(fatigue_alert["contributingMeasurements"]) == 4
    print(f"  -> PASS: Combined multi-signal pattern verified (Alert: '{fatigue_alert['title']}')", flush=True)
    print(f"     Reasoning: {fatigue_alert['triggerReason']}")
    print(f"     Escalation Steps: {len(fatigue_alert['escalationSteps'])} flight rule actions recommended")

    print("\n" + "=" * 65, flush=True)
    print("ALL 5 CLINICAL TRIAGE SCENARIOS PASSED WITH 100% SUCCESS")
    print("=" * 65, flush=True)


if __name__ == "__main__":
    run_scenario_tests()
