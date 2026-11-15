"""
Regression and verification test suite for Observation Status Mapping Audit.
Tests canonical parameter normalization, profile-aware nominal bound comparisons,
individual status isolation, invalid/missing observation handling, and idempotency.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.core.units import PARAMETER_ALIASES, validate_and_convert_observation
from app.schemas.enums import OperationalState, DataSource, QualityStatus, GravityEnvironment, DeviationSeverity
from app.schemas.mission_profile import MissionSelectRequest
from app.schemas.observation import ObservationBatchCreate, ObservationCreate
from app.schemas.context import EnvironmentStatus, DataQualityContext
from app.services.profile_manager import MissionProfileManager
from app.services.environment_manager import ActualEnvironmentManager
from app.services.deviation_engine import MissionDeviationEngine
from app.repositories.mission_repository import MissionRepository
from app.api.endpoints import (
    select_mission_profile, ingest_observations, get_current_mission_context
)

@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_canonical_parameter_aliases():
    """Verify alias mapping canonicalizes parameter names."""
    assert PARAMETER_ALIASES.get("CABIN_PRESSURE_KPA") == "CABIN_PRESSURE"
    assert PARAMETER_ALIASES.get("PRESSURE") == "CABIN_PRESSURE"
    assert PARAMETER_ALIASES.get("CO2_PPM") == "CO2_CONCENTRATION"
    assert PARAMETER_ALIASES.get("CO2_PARTIAL_PRESSURE_MMHG") == "CO2_CONCENTRATION"
    assert PARAMETER_ALIASES.get("RADIATION_MSV_PER_DAY") == "RADIATION"
    assert PARAMETER_ALIASES.get("ECLSS") == "LIFE_SUPPORT"
    assert PARAMETER_ALIASES.get("HABITAT") == "HABITAT_INTEGRITY"

def test_verified_cabin_pressure_in_range_updates_only_cabin_pressure(memory_db):
    """
    Core Bug Audit Test:
    A verified cabin pressure observation of 70.3 kPa on ARES_VOYAGER_MARS (bounds 68.0 - 72.0 kPa)
    MUST update cabin_pressure_status = NOMINAL.
    It MUST NOT infer CO2, radiation, life support, or habitat status (they remain UNKNOWN).
    """
    # 1. Select ARES_VOYAGER_MARS
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    # 2. Ingest cabin_pressure_kpa = 70.3 kPa
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=70.3,
                unit="kPa",
                source=DataSource.SIMULATED
            )
        ]
    )
    result = ingest_observations(batch=batch, db=memory_db)
    assert result["processed_count"] == 1

    # 3. Retrieve active context
    ctx = get_current_mission_context(db=memory_db)
    assert ctx.environment.cabin_pressure_status == "NOMINAL"
    assert ctx.environment.observed_parameters.get("CABIN_PRESSURE") == 70.3

    # 4. Strict isolation: Other parameters must remain UNKNOWN
    assert ctx.environment.co2_status == "UNKNOWN"
    assert ctx.environment.radiation_status == "UNKNOWN"
    assert ctx.environment.life_support_status == "UNKNOWN"
    assert ctx.environment.habitat_status == "UNKNOWN"

    # 5. Data quality unknown parameters list must retain remaining unmeasured fields
    assert "co2_concentration_status" in ctx.data_quality.unknown_parameters
    assert "radiation_status" in ctx.data_quality.unknown_parameters
    assert "life_support_status" in ctx.data_quality.unknown_parameters
    assert "habitat_integrity_status" in ctx.data_quality.unknown_parameters
    assert "cabin_pressure_status" not in ctx.data_quality.unknown_parameters

def test_cabin_pressure_profile_bounds_sensitivity(memory_db):
    """
    Profile Sensitivity Test:
    70.3 kPa is NOMINAL for Mars (bounds: 68-72 kPa),
    but the exact same 70.3 kPa is DEGRADED_LOW for ISS (bounds: 97.9 - 102.7 kPa).
    """
    # Select ISS profile
    select_mission_profile(MissionSelectRequest(mission_id="ISS_EXPEDITION_LEO"), db=memory_db)

    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=70.3,
                unit="kPa",
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    ctx = get_current_mission_context(db=memory_db)
    # Under ISS bounds, 70.3 kPa is far below minimum of 97.9 kPa
    assert ctx.environment.cabin_pressure_status in ("DEGRADED_LOW", "CRITICAL_LOW")
    # Deviations must report cabin pressure deviation
    dev_names = [d.deviation_name for d in ctx.active_deviations]
    assert any("CABIN_PRESSURE" in name for name in dev_names)

def test_out_of_range_low_cabin_pressure_deviation(memory_db):
    """60.0 kPa on ARES_VOYAGER_MARS is below min 68.0 kPa -> DEGRADED_LOW."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=60.0,
                unit="kPa",
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    ctx = get_current_mission_context(db=memory_db)
    assert ctx.environment.cabin_pressure_status == "DEGRADED_LOW"
    dev_names = [d.deviation_name for d in ctx.active_deviations]
    assert "CABIN_PRESSURE_DEVIATION" in dev_names

def test_critical_low_cabin_pressure_deviation(memory_db):
    """40.0 kPa on ARES_VOYAGER_MARS is severe hypobaric -> CRITICAL_LOW."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=40.0,
                unit="kPa",
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    ctx = get_current_mission_context(db=memory_db)
    assert ctx.environment.cabin_pressure_status == "CRITICAL_LOW"
    dev_names = [d.deviation_name for d in ctx.active_deviations]
    assert "CABIN_PRESSURE_CRITICAL" in dev_names

def test_out_of_range_high_cabin_pressure_deviation(memory_db):
    """80.0 kPa on ARES_VOYAGER_MARS exceeds max 72.0 kPa -> DEGRADED_HIGH."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=80.0,
                unit="kPa",
                source=DataSource.SIMULATED
            )
        ]
    )
    ingest_observations(batch=batch, db=memory_db)

    ctx = get_current_mission_context(db=memory_db)
    assert ctx.environment.cabin_pressure_status == "DEGRADED_HIGH"
    dev_names = [d.deviation_name for d in ctx.active_deviations]
    assert "CABIN_PRESSURE_DEVIATION" in dev_names

def test_invalid_unit_observation_leaves_status_unknown(memory_db):
    """Invalid unit observation must be rejected and leave cabin_pressure_status as UNKNOWN."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)

    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=70.3,
                unit="invalid_dimension_xyz",
                source=DataSource.SIMULATED
            )
        ]
    )
    res = ingest_observations(batch=batch, db=memory_db)
    obs = res["observations"][0]
    assert obs["validation_status"] is False
    assert obs["quality_status"] == QualityStatus.INVALID_UNIT.value

    ctx = get_current_mission_context(db=memory_db)
    assert ctx.environment.cabin_pressure_status == "UNKNOWN"

def test_idempotent_resubmission_creates_no_duplicates(memory_db):
    """Submitting observation with same idempotency key must not create duplicate DB rows."""
    select_mission_profile(MissionSelectRequest(mission_id="ARES_VOYAGER_MARS"), db=memory_db)
    repo = MissionRepository(memory_db)

    idemp_key = "IDEMP-TEST-KEY-42"
    batch = ObservationBatchCreate(
        observations=[
            ObservationCreate(
                parameter="cabin_pressure_kpa",
                value=70.3,
                unit="kPa",
                idempotency_key=idemp_key,
                source=DataSource.SIMULATED
            )
        ]
    )

    # First submission
    res1 = ingest_observations(batch=batch, db=memory_db)
    assert res1["processed_count"] == 1
    obs1 = res1["observations"][0]
    assert obs1["validation_status"] is True

    # Check DB record count
    initial_count = len(repo.get_recent_observations("ARES_VOYAGER_MARS", limit=100))
    assert initial_count == 1

    # Second submission with identical idempotency key
    res2 = ingest_observations(batch=batch, db=memory_db)
    assert res2["processed_count"] == 1
    obs2 = res2["observations"][0]
    assert obs2["metadata"].get("idempotent_duplicate") is True

    # Verify no duplicate entity created in database
    post_count = len(repo.get_recent_observations("ARES_VOYAGER_MARS", limit=100))
    assert post_count == initial_count, f"Expected {initial_count} observations in DB, found {post_count}"

