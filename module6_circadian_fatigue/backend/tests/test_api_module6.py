import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.schemas.schemas import AstronautSchema, PVTTrialCreate, PVTSessionSubmitRequest
from app.api.endpoints import (
    health_check,
    list_astronauts,
    register_astronaut,
    get_sleep_status,
    get_circadian,
    get_fatigue,
    get_stress,
    get_cognitive_readiness,
    submit_pvt,
    get_astronaut_pvt_history
)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_health_check():
    h = health_check()
    assert h["status"] == "healthy"
    assert h["port"] == 8006
    assert "circadian_two_process_model" in h["capabilities"]

def test_astronaut_listing_and_registration(db_session):
    # Initial list seeds default 4 astronauts
    astros = list_astronauts(db=db_session)
    assert len(astros) == 4
    ids = [a.astronaut_id for a in astros]
    assert "ASTRO-01" in ids
    assert "ASTRO-02" in ids

    # Register new
    new_one = AstronautSchema(
        astronaut_id="ASTRO-TEST-NEW",
        name="Cmdr. Test Astronaut",
        role="Commander",
        callsign="TEST1",
        baseline_sleep_hours=8.0,
        baseline_hrv_rmssd=55.0
    )
    res = register_astronaut(new_one, db=db_session)
    assert res.astronaut_id == "ASTRO-TEST-NEW"

    updated = list_astronauts(db=db_session)
    assert len(updated) == 5

def test_sleep_and_circadian_endpoints(db_session):
    sleep_res = get_sleep_status(astronaut_id="ASTRO-01", mission_hour=48.0, db=db_session)
    assert sleep_res.astronaut_id == "ASTRO-01"
    assert sleep_res.data_source == "SIMULATED_MODULE5"
    assert sleep_res.total_sleep_hours_last_24h > 0

    circ_res = get_circadian(astronaut_id="ASTRO-01", mission_hour=48.0, db=db_session)
    assert circ_res.astronaut_id == "ASTRO-01"
    assert len(circ_res.alertness_curve_24h) == 24
    assert 0.0 <= circ_res.circadian_alignment_index <= 1.0

def test_fatigue_stress_readiness_endpoints(db_session):
    fatigue_res = get_fatigue(astronaut_id="ASTRO-01", db=db_session)
    assert fatigue_res.fatigue_level in ["NORMAL", "ELEVATED", "HIGH"]
    assert fatigue_res.reliable_data is True

    stress_res = get_stress(astronaut_id="ASTRO-01", db=db_session)
    assert stress_res.data_available is True
    assert stress_res.current_stress_score is not None

    readiness_res = get_cognitive_readiness(astronaut_id="ASTRO-01", db=db_session)
    assert readiness_res.overall_readiness_score > 0
    assert readiness_res.rating in ["OPTIMAL_PERFORMANCE", "QUALIFIED_MONITORED", "DEGRADED_RESTRICTED", "IMPAIRED"]
    assert readiness_res.data_completeness > 0

def test_pvt_submission_and_history_endpoints(db_session):
    pvt_req = PVTSessionSubmitRequest(
        astronaut_id="ASTRO-01",
        trials=[
            PVTTrialCreate(trial_number=1, stimulus_delay_ms=2500, reaction_time_ms=240),
            PVTTrialCreate(trial_number=2, stimulus_delay_ms=3200, reaction_time_ms=255),
            PVTTrialCreate(trial_number=3, stimulus_delay_ms=2100, reaction_time_ms=230),
            PVTTrialCreate(trial_number=4, stimulus_delay_ms=4100, reaction_time_ms=260),
            PVTTrialCreate(trial_number=5, stimulus_delay_ms=2900, reaction_time_ms=245),
        ]
    )
    pvt_res = submit_pvt(pvt_req, db=db_session)
    assert pvt_res.performance_rating == "OPTIMAL"
    assert pvt_res.lapses_count == 0

    hist_res = get_astronaut_pvt_history("ASTRO-01", db=db_session)
    assert hist_res.total_sessions_completed == 1
    assert len(hist_res.sessions) == 1
