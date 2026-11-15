import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.schemas.schemas import PVTTrialCreate, PVTSessionSubmitRequest
from app.services.pvt_service import evaluate_and_record_pvt_session, get_pvt_history

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

def test_pvt_evaluation_optimal(db_session):
    req = PVTSessionSubmitRequest(
        astronaut_id="ASTRO-TEST-1",
        trials=[
            PVTTrialCreate(trial_number=1, stimulus_delay_ms=2500, reaction_time_ms=230),
            PVTTrialCreate(trial_number=2, stimulus_delay_ms=3100, reaction_time_ms=245),
            PVTTrialCreate(trial_number=3, stimulus_delay_ms=2100, reaction_time_ms=220),
            PVTTrialCreate(trial_number=4, stimulus_delay_ms=4000, reaction_time_ms=250),
            PVTTrialCreate(trial_number=5, stimulus_delay_ms=2800, reaction_time_ms=235),
        ]
    )
    result = evaluate_and_record_pvt_session(db_session, req)
    assert result.astronaut_id == "ASTRO-TEST-1"
    assert result.trials_count == 5
    assert result.lapses_count == 0
    assert result.false_starts_count == 0
    assert result.performance_rating == "OPTIMAL"
    assert result.avg_reaction_time_ms < 250.0

def test_pvt_evaluation_lapses_and_false_start(db_session):
    req = PVTSessionSubmitRequest(
        astronaut_id="ASTRO-TEST-2",
        trials=[
            PVTTrialCreate(trial_number=1, stimulus_delay_ms=2500, reaction_time_ms=80),   # False start
            PVTTrialCreate(trial_number=2, stimulus_delay_ms=3100, reaction_time_ms=540),  # Lapse
            PVTTrialCreate(trial_number=3, stimulus_delay_ms=2100, reaction_time_ms=620),  # Lapse
            PVTTrialCreate(trial_number=4, stimulus_delay_ms=4000, reaction_time_ms=310),
            PVTTrialCreate(trial_number=5, stimulus_delay_ms=2800, reaction_time_ms=340),
        ]
    )
    result = evaluate_and_record_pvt_session(db_session, req)
    assert result.false_starts_count == 1
    assert result.lapses_count == 2
    assert result.performance_rating in ["DEGRADED", "IMPAIRED"]

    # Test history retrieval
    hist = get_pvt_history(db_session, "ASTRO-TEST-2")
    assert hist.total_sessions_completed == 1
    assert len(hist.sessions) == 1
    assert hist.sessions[0].lapses_count == 2

