import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.schemas.schemas import AlertAcknowledgeRequest
from app.api.endpoints import (
    health_check,
    get_environmental_overview,
    get_radiation,
    get_co2,
    get_cabin,
    get_alerts,
    acknowledge_alert
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

def test_health_endpoint():
    h = health_check()
    assert h["status"] == "healthy"
    assert h["port"] == 8007
    assert "radiation_exposure_tracking" in h["capabilities"]

def test_environmental_overview(db_session):
    ov = get_environmental_overview(db=db_session)
    assert 0.0 <= ov.overall_risk_index <= 100.0
    assert ov.operational_risk_level in ["NOMINAL", "MONITORING_REQUIRED", "CONTINGENCY", "EMERGENCY"]
    assert ov.radiation_risk_score >= 0.0
    assert ov.co2_risk_score >= 0.0

def test_radiation_and_co2_endpoints():
    rad = get_radiation(mission_hours=48.0, has_active_spe=True)
    assert rad.cumulative_dose_msv > 0
    assert len(rad.time_series) == 25

    co2 = get_co2(mission_hours=48.0, scrubber_degraded=True)
    assert co2.ppco2_mmhg > 0
    assert len(co2.time_series) == 25

def test_cabin_endpoint():
    cab = get_cabin()
    assert cab.cabin_pressure_kpa == 70.3
    assert cab.mission_id == "ARES_VOYAGER_MARS"

def test_alerts_api(db_session):
    alerts = get_alerts(acknowledged=None, db=db_session)
    assert len(alerts) >= 3

    first_id = alerts[0].alert_id
    ack_res = acknowledge_alert(
        alert_id=first_id,
        payload=AlertAcknowledgeRequest(acknowledged_by="Flight Director", notes="Confirmed"),
        db=db_session
    )
    assert ack_res.acknowledged is True
    assert ack_res.acknowledged_by == "Flight Director"

