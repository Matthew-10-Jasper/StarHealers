from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class SimulationSessionModel(Base):
    __tablename__ = "simulation_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    scenario_id = Column(String(64), index=True, nullable=False)
    scenario_name = Column(String(128), nullable=False)
    engine_type = Column(String(32), default="COMBINED", nullable=False)
    status = Column(String(32), default="IDLE", nullable=False)
    current_time_hours = Column(Float, default=0.0, nullable=False)
    total_duration_hours = Column(Float, default=168.0, nullable=False)
    timestep_hours = Column(Float, default=1.0, nullable=False)
    provenance = Column(String(32), default="SIMULATED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    readings = relationship("SimulationReadingModel", back_populates="session", cascade="all, delete-orphan")
    events = relationship("SimulationEventModel", back_populates="session", cascade="all, delete-orphan")
    configurations = relationship("SimulationConfigurationModel", back_populates="session", cascade="all, delete-orphan")

class SimulationScenarioModel(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scenario_id = Column(String(64), unique=True, index=True, nullable=False)
    scenario_name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    mission_duration_hours = Column(Float, default=168.0, nullable=False)
    timestep_hours = Column(Float, default=1.0, nullable=False)
    radiation_params_json = Column(Text, nullable=False)
    co2_params_json = Column(Text, nullable=False)
    sleep_params_json = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class SimulationReadingModel(Base):
    __tablename__ = "simulation_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("simulation_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    step_index = Column(Integer, nullable=False)
    simulation_time_hours = Column(Float, nullable=False)
    mission_day = Column(Float, nullable=False)
    
    # Radiation fields
    radiation_incident_msv_day = Column(Float, nullable=True)
    radiation_absorbed_msv_day = Column(Float, nullable=True)
    radiation_cumulative_msv = Column(Float, nullable=True)
    radiation_severity = Column(String(32), nullable=True)
    
    # CO2 fields
    co2_partial_pressure_mmhg = Column(Float, nullable=True)
    co2_ppm = Column(Float, nullable=True)
    co2_generation_l_h = Column(Float, nullable=True)
    co2_removal_l_h = Column(Float, nullable=True)
    co2_efficiency = Column(Float, nullable=True)
    co2_severity = Column(String(32), nullable=True)
    
    # Sleep debt fields
    sleep_required_hours = Column(Float, nullable=True)
    sleep_actual_hours = Column(Float, nullable=True)
    sleep_daily_deficit_hours = Column(Float, nullable=True)
    sleep_daily_recovery_hours = Column(Float, nullable=True)
    sleep_cumulative_debt_hours = Column(Float, nullable=True)
    sleep_severity = Column(String(32), nullable=True)
    
    overall_hazard_level = Column(String(32), default="NOMINAL", nullable=False)
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("SimulationSessionModel", back_populates="readings")

class SimulationEventModel(Base):
    __tablename__ = "simulation_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("simulation_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp_hour = Column(Float, nullable=False)
    event_type = Column(String(64), nullable=False)
    engine = Column(String(32), nullable=False)
    severity = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)
    data_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("SimulationSessionModel", back_populates="events")

class SimulationConfigurationModel(Base):
    __tablename__ = "simulation_configurations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("simulation_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False)
    config_key = Column(String(64), nullable=False)
    config_value_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("SimulationSessionModel", back_populates="configurations")

