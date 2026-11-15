import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.schemas.schemas import AlertAcknowledgeRequest
from app.services.alert_service import (
    seed_alerts_if_empty,
    list_hazard_alerts,
    acknowledge_hazard_alert
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

def test_alerts_lifecycle(db_session):
    # Initial list seeds defaults
    alerts = list_hazard_alerts(db_session)
    assert len(alerts) >= 3
    
    # Filter unacknowledged
    unacked = list_hazard_alerts(db_session, acknowledged=False)
    assert len(unacked) == len(alerts)

    # Acknowledge one
    target_id = unacked[0].alert_id
    acked = acknowledge_hazard_alert(
        db_session,
        target_id,
        AlertAcknowledgeRequest(acknowledged_by="Cmdr. Vance", notes="EVA delay ordered")
    )
    assert acked is not None
    assert acked.acknowledged is True
    assert acked.acknowledged_by == "Cmdr. Vance"
    assert "EVA delay ordered" in acked.message

    # Re-check unacknowledged count
    rem_unacked = list_hazard_alerts(db_session, acknowledged=False)
    assert len(rem_unacked) == len(alerts) - 1

