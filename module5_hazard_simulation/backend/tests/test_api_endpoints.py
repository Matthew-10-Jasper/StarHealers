import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_health(client):
    """GET /health returns 200 OK and valid status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["module_id"] == "MODULE_5"

def test_api_get_engines(client):
    """GET /engines lists all 3 engines."""
    res = client.get("/engines")
    assert res.status_code == 200
    engines = res.json()
    assert len(engines) == 3
    names = [e["engine"] for e in engines]
    assert "RADIATION" in names
    assert "CO2" in names
    assert "SLEEP" in names

def test_api_list_scenarios(client):
    """GET /scenarios lists predefined scenarios."""
    res = client.get("/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 5

def test_api_simulation_lifecycle(client):
    """Creates a simulation session, advances step, checks results."""
    # 1. Create session
    create_res = client.post("/simulations", json={
        "scenario_id": "NORMAL_MISSION",
        "engine_type": "COMBINED",
        "mission_duration_hours": 24.0,
        "timestep_hours": 1.0
    })
    assert create_res.status_code == 200
    session_data = create_res.json()
    session_id = session_data["session_id"]
    assert session_data["status"] == "IDLE"

    # 2. Start
    start_res = client.post(f"/simulations/{session_id}/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "RUNNING"

    # 3. Step
    step_res = client.post(f"/simulations/{session_id}/step")
    assert step_res.status_code == 200
    step_data = step_res.json()
    assert step_data["step_index"] == 0
    assert step_data["simulation_time_hours"] == 0.0
    assert "radiation" in step_data
    assert "co2" in step_data
    assert "sleep" in step_data

    # 4. Results
    res_res = client.get(f"/simulations/{session_id}/results")
    assert res_res.status_code == 200
    res_data = res_res.json()
    assert res_data["session_id"] == session_id
    assert len(res_data["timeline"]) >= 1

    # 5. Export to Module 4 format
    exp_res = client.get(f"/simulations/{session_id}/export-module4")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["source_session_id"] == session_id
    assert len(exp_data["observations"]) >= 3

def test_api_standalone_engine_runs(client):
    """Tests /engines/radiation/run, /engines/co2/run, /engines/sleep/run."""
    rad_res = client.post("/engines/radiation/run", json={"mission_duration_hours": 12.0})
    assert rad_res.status_code == 200
    assert rad_res.json()["engine"] == "RADIATION"

    co2_res = client.post("/engines/co2/run", json={"mission_duration_hours": 12.0})
    assert co2_res.status_code == 200
    assert co2_res.json()["engine"] == "CO2"

    sleep_res = client.post("/engines/sleep/run", json={"mission_days": 3})
    assert sleep_res.status_code == 200
    assert sleep_res.json()["engine"] == "SLEEP"

