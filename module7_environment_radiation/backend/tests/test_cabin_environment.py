import pytest
from app.services.m4_consumer import fetch_m4_cabin_telemetry

def test_cabin_telemetry_fetch_or_fallback():
    cabin = fetch_m4_cabin_telemetry()
    assert cabin.mission_id == "ARES_VOYAGER_MARS"
    assert cabin.cabin_pressure_kpa == 70.3
    assert cabin.cabin_pressure_status == "NOMINAL"
    assert cabin.telemetry_freshness in ["FRESH", "STALE"]
    assert cabin.completeness in ["PARTIAL", "COMPLETE"]

