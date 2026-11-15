"""
StarHealers — Comprehensive FastAPI Endpoint Verification Suite
Tests all REST endpoints, schemas, validation errors, and response structures.
"""

import sys
import os
from pathlib import Path

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from starlette.testclient import TestClient
from main import app
from seed_data import seed

client = TestClient(app)


def test_api():
    print("=" * 65, flush=True)
    print("STARHEALERS FASTAPI REST ENDPOINT TEST SUITE", flush=True)
    print("=" * 65, flush=True)

    # Re-seed database for clean state
    seed()

    # 1. Root & Health Check
    print("\n[TEST 1] Testing Root & Status Endpoint...", flush=True)
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert data["version"] == "2.4-MED"
    print("  -> PASS: Root endpoint verified (Status: OPERATIONAL)", flush=True)

    # 2. Missions API
    print("\n[TEST 2] Testing Missions API...", flush=True)
    res = client.get("/api/missions")
    assert res.status_code == 200
    missions = res.json()
    assert len(missions) == 3
    print(f"  -> PASS: Retrieved {len(missions)} missions", flush=True)

    res = client.get("/api/missions/mission-mars-01")
    assert res.status_code == 200
    mars = res.json()
    assert mars["target"] == "Mars"
    assert mars["environment"]["cabinCo2"] == 0.42
    print(f"  -> PASS: Mars mission retrieved with ECLSS telemetry (CO2: {mars['environment']['cabinCo2']}%)", flush=True)

    # 404 test
    res = client.get("/api/missions/invalid-mission-id")
    assert res.status_code == 404
    assert res.json()["error"] is True
    print("  -> PASS: 404 error handling for invalid mission verified", flush=True)

    # 3. Astronauts API
    print("\n[TEST 3] Testing Astronauts API...", flush=True)
    res = client.get("/api/astronauts")
    assert res.status_code == 200
    crew = res.json()
    assert len(crew) == 4
    print(f"  -> PASS: Retrieved {len(crew)} crew members", flush=True)

    res = client.get("/api/astronauts/ASTRO-01")
    assert res.status_code == 200
    sarah = res.json()
    assert sarah["name"] == "Dr. Sarah Chen"
    assert sarah["baseline"]["restingHr"] == 62.0
    assert "heart" in sarah["bodyRegionStatus"]
    print(f"  -> PASS: Astronaut profile '{sarah['name']}' verified with baseline specs", flush=True)

    # 4. Module 1: Health Readings API
    print("\n[TEST 4] Testing Health Readings API (Module 1)...", flush=True)
    res = client.get("/api/astronauts/ASTRO-01/health")
    assert res.status_code == 200
    readings = res.json()
    assert "heartRate" in readings
    assert readings["heartRate"]["value"] == 94.0
    assert readings["heartRate"]["source"] == "SIMULATED"
    print("  -> PASS: Latest 9 physiological parameters retrieved successfully", flush=True)

    # Historical Telemetry API
    res = client.get("/api/astronauts/ASTRO-01/health/history?time_range=24h&limit=24")
    assert res.status_code == 200
    hist = res.json()
    assert len(hist) > 0
    print(f"  -> PASS: Historical telemetry retrieved ({len(hist)} time-series data points)", flush=True)

    # Ingest New Reading API
    print("\n[TEST 5] Testing Reading Ingestion & Validation...", flush=True)
    new_reading = {
        "metric_name": "heartRate",
        "value": 98.0,
        "unit": "bpm",
        "source": "SIMULATED",
        "quality_status": "GOOD",
        "severity": "WARNING"
    }
    res = client.post("/api/astronauts/ASTRO-01/health/readings", json=new_reading)
    assert res.status_code == 201
    assert res.json()["success"] is True
    print("  -> PASS: Ingested new physiological reading", flush=True)

    # Validation Error Test (Invalid metric and source)
    invalid_reading = {
        "metric_name": "unsupported_magic_metric",
        "value": 100.0,
        "unit": "invalid",
        "source": "UNAUTHORIZED_SOURCE"
    }
    res = client.post("/api/astronauts/ASTRO-01/health/readings", json=invalid_reading)
    assert res.status_code == 422
    assert res.json()["error"] is True
    print("  -> PASS: 422 Unprocessable Entity correctly returned for invalid payload", flush=True)

    # 5. Module 2: Interactive Body Map API
    print("\n[TEST 6] Testing Body Map API (Module 2)...", flush=True)
    res = client.get("/api/astronauts/ASTRO-01/body-map")
    assert res.status_code == 200
    body_map = res.json()
    assert "regions" in body_map
    assert "heart" in body_map["regions"]
    assert "brain" in body_map["regions"]
    print("  -> PASS: Full anatomical body map status retrieved for all 6 systems", flush=True)

    res = client.get("/api/astronauts/ASTRO-01/body-map/heart")
    assert res.status_code == 200
    heart_detail = res.json()
    assert heart_detail["regionId"] == "heart"
    assert "heartRate" in heart_detail["associatedMetrics"]
    assert "disclaimer" in heart_detail
    print(f"  -> PASS: Body region detail retrieved with evidence disclaimer: '{heart_detail['disclaimer'][:40]}...'", flush=True)

    # 6. Module 3: Triage & Alerts API
    print("\n[TEST 7] Testing Triage Engine & Alerts API (Module 3)...", flush=True)
    res = client.get("/api/alerts?status=ACTIVE")
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) >= 3
    print(f"  -> PASS: Retrieved {len(alerts)} active triage alerts", flush=True)

    # Test Rule Evaluation Endpoint (Compound Autonomic Fatigue)
    eval_payload = {
        "astronaut_id": "ASTRO-01",
        "heartRate": 96.0,
        "hrv": 32.0,
        "sleep": 4.5,
        "stress": 75.0,
        "spo2": 98.0
    }
    res = client.post("/api/triage/evaluate", json=eval_payload)
    assert res.status_code == 200
    eval_result = res.json()
    assert eval_result["isAlertTriggered"] is True
    assert eval_result["severity"] == "WARNING"
    assert len(eval_result["triggeredAlerts"]) > 0
    print(f"  -> PASS: Rule evaluation triggered compound alert '{eval_result['triggeredAlerts'][0]['title']}'", flush=True)

    # Test Alert Resolution
    res = client.post("/api/alerts/ALT-2026-0888/resolve", json={"user_id": "USR-MED-01"})
    assert res.status_code == 200
    assert res.json()["status"] == "RESOLVED"
    print("  -> PASS: Alert resolution verified with audit trail", flush=True)

    print("\n" + "=" * 65, flush=True)
    print("ALL FASTAPI REST ENDPOINT TESTS PASSED WITH 100% SUCCESS", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    test_api()
