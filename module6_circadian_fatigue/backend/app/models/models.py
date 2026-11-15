from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class AstronautModel(Base):
    __tablename__ = "astronauts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    astronaut_id = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)
    callsign = Column(String(32), nullable=True)
    baseline_sleep_hours = Column(Float, default=8.0, nullable=False)
    baseline_hrv_rmssd = Column(Float, default=52.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    pvt_sessions = relationship("PVTSessionModel", back_populates="astronaut", cascade="all, delete-orphan")
    readiness_records = relationship("ReadinessRecordModel", back_populates="astronaut", cascade="all, delete-orphan")

class PVTSessionModel(Base):
    __tablename__ = "pvt_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    astronaut_id = Column(String(32), ForeignKey("astronauts.astronaut_id", ondelete="CASCADE"), index=True, nullable=False)
    trials_count = Column(Integer, default=5, nullable=False)
    avg_reaction_time_ms = Column(Float, nullable=False)
    median_reaction_time_ms = Column(Float, nullable=False)
    lapses_count = Column(Integer, default=0, nullable=False)
    false_starts_count = Column(Integer, default=0, nullable=False)
    slowest_reaction_ms = Column(Float, nullable=True)
    fastest_reaction_ms = Column(Float, nullable=True)
    performance_rating = Column(String(32), default="NORMAL", nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    astronaut = relationship("AstronautModel", back_populates="pvt_sessions")
    trials = relationship("PVTTrialModel", back_populates="session", cascade="all, delete-orphan")

class PVTTrialModel(Base):
    __tablename__ = "pvt_trials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("pvt_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    trial_number = Column(Integer, nullable=False)
    stimulus_delay_ms = Column(Float, nullable=False)
    reaction_time_ms = Column(Float, nullable=False)
    is_lapse = Column(Boolean, default=False, nullable=False)
    is_false_start = Column(Boolean, default=False, nullable=False)

    session = relationship("PVTSessionModel", back_populates="trials")

class ReadinessRecordModel(Base):
    __tablename__ = "readiness_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(String(64), unique=True, index=True, nullable=False)
    astronaut_id = Column(String(32), ForeignKey("astronauts.astronaut_id", ondelete="CASCADE"), index=True, nullable=False)
    score = Column(Float, nullable=False)
    rating = Column(String(32), nullable=False)
    sleep_component = Column(Float, nullable=False)
    circadian_component = Column(Float, nullable=False)
    fatigue_component = Column(Float, nullable=False)
    stress_component = Column(Float, nullable=False)
    pvt_component = Column(Float, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    explanation_json = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    astronaut = relationship("AstronautModel", back_populates="readiness_records")

class StressRecordModel(Base):
    __tablename__ = "stress_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(String(64), unique=True, index=True, nullable=False)
    astronaut_id = Column(String(32), index=True, nullable=False)
    stress_score = Column(Float, nullable=False)
    hrv_rmssd = Column(Float, nullable=True)
    heart_rate_bpm = Column(Float, nullable=True)
    sleep_debt_hours = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

