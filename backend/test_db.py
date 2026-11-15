"""
StarHealers - Database Verification & Integrity Test Suite
Verifies table creation, foreign keys, relationships, NULL handling, and CRUD operations.
"""

import sys
import sqlite3
from database import init_db, get_db, DB_PATH
from seed_data import seed
import crud


def run_tests():
    print("=" * 60)
    print("STARHEALERS DATABASE INTEGRITY TEST SUITE")
    print("=" * 60)

    # 1. Test Seed & Initialization
    print("\n[TEST 1] Initializing and Seeding Database...")
    seed()
    assert DB_PATH.exists(), f"Database file does not exist at {DB_PATH}"
    print("  -> PASS: Database created and seeded at", DB_PATH)

    # 2. Test Missions Retrieval
    print("\n[TEST 2] Retrieving Missions...")
    missions = crud.get_missions()
    assert len(missions) == 3, f"Expected 3 missions, got {len(missions)}"
    mars = crud.get_mission("mission-mars-01")
    assert mars is not None, "Mars mission not found"
    assert mars["target"] == "Mars", f"Expected Mars target, got {mars['target']}"
    print(f"  -> PASS: Retrieved {len(missions)} missions (Mars delay: {mars['comms_delay_sec']}s)")

    # 3. Test Astronauts Retrieval & Baselines
    print("\n[TEST 3] Retrieving Astronauts...")
    astronauts = crud.get_astronauts("mission-mars-01")
    assert len(astronauts) == 4, f"Expected 4 astronauts, got {len(astronauts)}"
    sarah = crud.get_astronaut("ASTRO-01")
    assert sarah["name"] == "Dr. Sarah Chen", "Sarah Chen not found"
    assert sarah["baseline_resting_hr"] == 62.0, "Baseline resting HR mismatch"
    print(f"  -> PASS: Retrieved {len(astronauts)} crew members (Found: {sarah['name']})")

    # 4. Test Health Readings Retrieval & Missing Data Handling
    print("\n[TEST 4] Testing Health Readings & NULL Value Handling...")
    sarah_readings = crud.get_latest_readings_by_astronaut("ASTRO-01")
    assert len(sarah_readings) == 9, f"Expected 9 metrics for Sarah, got {len(sarah_readings)}"
    assert sarah_readings["heartRate"]["value"] == 94.0, "HR mismatch"
    assert sarah_readings["heartRate"]["source"] == "SIMULATED", "Source mismatch"

    # Test Alex Tanaka (ASTRO-04) missing values
    alex_readings = crud.get_latest_readings_by_astronaut("ASTRO-04")
    assert alex_readings["heartRate"]["value"] is None, "Missing reading must be None, not 0"
    assert alex_readings["heartRate"]["severity"] == "NO_DATA", "Missing reading severity must be NO_DATA"
    print("  -> PASS: Health readings retrieved. NULL handling verified (not converted to 0)")

    # 5. Test Triage Alerts & JSON Parsing
    print("\n[TEST 5] Testing Rule-Based Triage Alerts...")
    alerts = crud.get_alerts(status="ACTIVE")
    assert len(alerts) >= 3, f"Expected at least 3 active alerts, got {len(alerts)}"
    elena_alert = next((a for a in alerts if a["astronaut_id"] == "ASTRO-03"), None)
    assert elena_alert is not None, "Elena's critical hypoxia alert missing"
    assert elena_alert["severity"] == "CRITICAL", "Severity mismatch"
    assert isinstance(elena_alert["contributing_measurements"], list), "JSON parsing failed"
    print(f"  -> PASS: Retrieved active alerts. Critical alert '{elena_alert['title']}' parsed correctly")

    # 6. Test Alert Resolution
    print("\n[TEST 6] Testing Alert Acknowledgement & Resolution...")
    success = crud.resolve_alert("ALT-2026-0891", "USR-MED-01")
    assert success is True, "Failed to resolve alert"
    resolved_alert = crud.get_alert_by_id("ALT-2026-0891")
    assert resolved_alert["status"] == "RESOLVED", "Alert status was not updated to RESOLVED"
    assert resolved_alert["acknowledged_by"] == "USR-MED-01", "Acknowledged user not set"
    print("  -> PASS: Alert resolution and audit trail confirmed")

    # 7. Test Foreign Key Enforcement
    print("\n[TEST 7] Testing Foreign Key Enforcement...")
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO astronauts 
                (astronaut_id, mission_id, name, role, age, blood_type, height_cm, weight_kg, status,
                 baseline_resting_hr, baseline_hrv, baseline_bp_systolic, baseline_bp_diastolic, baseline_spo2, baseline_temp,
                 baseline_glucose, baseline_hydration, baseline_stress)
                VALUES ('ASTRO-99', 'INVALID-MISSION-99', 'Unknown', 'Test', 30, 'O+', 170, 70, 'NORMAL', 60, 60, 120, 80, 98, 36.5, 90, 60, 20)
                """
            )
        assert False, "Foreign key violation should have raised an exception!"
    except sqlite3.IntegrityError:
        print("  -> PASS: Foreign key violation correctly caught and rejected by SQLite")

    # 8. Test Teammate Anomaly Dock
    print("\n[TEST 8] Testing Teammate Anomaly Integration Dock...")
    crud.insert_statistical_anomaly("ANOM-Z-002", "ASTRO-01", "hrv", -2.45, 0.98)
    with get_db() as conn:
        anom = conn.execute("SELECT * FROM teammate_anomalies_dock WHERE anomaly_id = 'ANOM-Z-002'").fetchone()
        assert anom is not None, "Failed to retrieve docked anomaly"
        assert anom["z_score"] == -2.45, "Z-score mismatch"
    print("  -> PASS: Teammate statistical anomaly dock verified")

    print("\n" + "=" * 60)
    print("ALL 8 DATABASE INTEGRITY TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
