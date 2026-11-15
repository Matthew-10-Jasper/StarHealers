import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.modules.module4_mission_intelligence.core.config import settings
from app.modules.module4_mission_intelligence.core.units import PARAMETER_ALIASES
from app.modules.module4_mission_intelligence.core.events import connection_manager
from app.modules.module4_mission_intelligence.database.session import get_db, engine, Base
from app.modules.module4_mission_intelligence.models.entities import MissionStateEntity
from app.modules.module4_mission_intelligence.repositories.mission_repository import MissionRepository
from app.modules.module4_mission_intelligence.schemas.enums import (
    OperationalState, DataSource, GravityEnvironment, DeviationSeverity, QualityStatus, CommStatus
)
from app.modules.module4_mission_intelligence.schemas.mission_profile import MissionProfile, MissionSelectRequest
from app.modules.module4_mission_intelligence.schemas.observation import EnvironmentalObservation, ObservationCreate, ObservationBatchCreate
from app.modules.module4_mission_intelligence.schemas.deviation import MissionDeviation
from app.modules.module4_mission_intelligence.schemas.context import (
    MissionContextResponse, PlannedMissionContext, ActualMissionContext,
    CommunicationContext, EnvironmentStatus, DataQualityContext,
    ContextTransitionRequest, ContextUpdateRequest
)
from app.modules.module4_mission_intelligence.schemas.history import AuditEvent, StateTransitionRecord
from app.modules.module4_mission_intelligence.services.profile_manager import MissionProfileManager
from app.modules.module4_mission_intelligence.services.environment_manager import ActualEnvironmentManager
from app.modules.module4_mission_intelligence.services.deviation_engine import MissionDeviationEngine
from app.modules.module4_mission_intelligence.services.contingency_manager import ContingencyStateManager
from app.modules.module4_mission_intelligence.services.reconfiguration_engine import ContextReconfigurationEngine
from app.modules.module4_mission_intelligence.services.constraints_manager import MissionConstraintsManager
from app.modules.module4_mission_intelligence.services.history_manager import ContextHistoryManager
from app.modules.module4_mission_intelligence.services.simulator import MissionTelemetrySimulator
from app.modules.module4_mission_intelligence.services.anomaly_detector import LayeredAnomalyDetector, LayeredAnomalyReport
from app.modules.module4_mission_intelligence.integrations.contracts import generate_standard_context_contract
from app.modules.module4_mission_intelligence.integrations.mock_consumers import (
    MockModule1HealthAdapter, MockModule3TriageAdapter, MockModule5SimulationAdapter
)

logger = logging.getLogger("MissionIntelligenceAPI")
router = APIRouter()

# Singletons for services
profile_mgr = MissionProfileManager()
env_mgr = ActualEnvironmentManager()
deviation_engine = MissionDeviationEngine()
contingency_mgr = ContingencyStateManager()
reconfig_engine = ContextReconfigurationEngine()
constraints_mgr = MissionConstraintsManager()
simulator = MissionTelemetrySimulator()
anomaly_detector = LayeredAnomalyDetector()

# Mock adapter registry
mock_adapters = {
    "MODULE_1_ASTRONAUT_HEALTH_MONITORING": MockModule1HealthAdapter(),
    "MODULE_3_CLINICAL_TRIAGE_ENGINE": MockModule3TriageAdapter(),
    "MODULE_5_RADIATION_CO2_SLEEP_SIMULATOR": MockModule5SimulationAdapter()
}

def get_current_context_object(db: Session) -> MissionContextResponse:
    """Helper to reconstruct the active MissionContextResponse from SQLite database,
    or initialize default profile if first boot.
    """
    repo = MissionRepository(db)
    active = repo.get_active_mission()

    if not active:
        # Initialize default profile
        default_profile = profile_mgr.get_profile(settings.DEFAULT_MISSION_ID)
        if not default_profile:
            profiles = profile_mgr.list_profiles()
            if not profiles:
                raise HTTPException(status_code=500, detail="No mission profiles found in configuration.")
            default_profile = profiles[0]

        active = MissionStateEntity(
            mission_id=default_profile.mission_id,
            context_id=f"CTX-INIT-001",
            context_version=1,
            planned_profile_id=default_profile.mission_id,
            actual_mission_phase=default_profile.mission_phase,
            operational_state=OperationalState.NOMINAL.value,
            gravity_environment=default_profile.gravity_environment.value,
            gravity_value_g=default_profile.gravity_value_g,
            communication_json=CommunicationContext(
                status=CommStatus.NOMINAL,
                expected_delay_seconds=default_profile.communication_characteristics.expected_delay_seconds,
                bandwidth_mbps=default_profile.communication_characteristics.bandwidth_mbps,
                earth_reachable=True
            ).model_dump_json(),
            environment_json=EnvironmentStatus().model_dump_json(),
            data_quality_json=DataQualityContext().model_dump_json(),
            planned_context_json=json.dumps({"planned_profile_id": default_profile.mission_id}),
            data_source=DataSource.SIMULATED.value,
            is_active=True
        )
        active = repo.set_active_mission(default_profile.mission_id, active)

        # Audit initial creation
        history_mgr = ContextHistoryManager(db)
        history_mgr.record_audit(
            active.mission_id,
            AuditEvent(
                event_type="INITIALIZE_MISSION_CONTEXT",
                description=f"Initialized default mission profile {active.mission_id}",
                evidence={"profile": default_profile.model_dump(mode="json")},
                context_version=1
            )
        )

    # Reconstruct schemas
    comm_data = json.loads(active.communication_json or "{}")
    comm = CommunicationContext(**comm_data)

    env_data = json.loads(active.environment_json or "{}")
    env = EnvironmentStatus(**env_data)

    # Ensure canonical reconciliation of observed_parameters and parameter_timestamps on load
    reconciled_params = {}
    reconciled_timestamps = {}
    for raw_k, ts in env.parameter_timestamps.items():
        canon_k = PARAMETER_ALIASES.get(raw_k.strip().upper(), raw_k.strip().upper())
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if canon_k not in reconciled_timestamps or ts > reconciled_timestamps[canon_k]:
            reconciled_timestamps[canon_k] = ts

    for raw_k, val in env.observed_parameters.items():
        canon_k = PARAMETER_ALIASES.get(raw_k.strip().upper(), raw_k.strip().upper())
        ts = env.parameter_timestamps.get(raw_k)
        if ts and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if canon_k not in reconciled_params or (ts and ts == reconciled_timestamps.get(canon_k)):
            reconciled_params[canon_k] = val

    env_needs_save = False
    if env.observed_parameters != reconciled_params or env.parameter_timestamps != reconciled_timestamps:
        env.observed_parameters = reconciled_params
        env.parameter_timestamps = reconciled_timestamps
        active.environment_json = env.model_dump_json()
        env_needs_save = True

    dq_data = json.loads(active.data_quality_json or "{}")
    dq = DataQualityContext(**dq_data)

    # Reconcile unknown_parameters directly with environment parameter statuses
    expected_unknown = []
    if env.cabin_pressure_status == "UNKNOWN":
        expected_unknown.append("cabin_pressure_status")
    if env.co2_status == "UNKNOWN":
        expected_unknown.append("co2_concentration_status")
    if env.radiation_status == "UNKNOWN":
        expected_unknown.append("radiation_status")
    if env.life_support_status == "UNKNOWN":
        expected_unknown.append("life_support_status")
    if env.habitat_status == "UNKNOWN":
        expected_unknown.append("habitat_integrity_status")

    if set(dq.unknown_parameters) != set(expected_unknown):
        dq.unknown_parameters = expected_unknown
        env_needs_save = True

    # Reconcile stale_parameters against canonical timestamps
    now = datetime.now(timezone.utc)
    reconciled_stale = [
        canon_k for canon_k, ts in env.parameter_timestamps.items()
        if (now - (ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc))).total_seconds() > settings.TELEMETRY_STALE_THRESHOLD_SECONDS
    ]
    # Reconcile completeness, freshness, and quality indicators
    required_params_count = 5
    if len(dq.unknown_parameters) == required_params_count:
        dq.telemetry_completeness = "NONE"
    elif len(dq.unknown_parameters) > 0:
        dq.telemetry_completeness = "PARTIAL"
    else:
        dq.telemetry_completeness = "COMPLETE"

    if not env.parameter_timestamps:
        dq.telemetry_freshness = "UNKNOWN"
    elif dq.stale_parameters:
        dq.telemetry_freshness = "STALE"
    else:
        dq.telemetry_freshness = "FRESH"

    if not env.observed_parameters:
        dq.validation_quality = QualityStatus.UNKNOWN
        dq.overall_status = QualityStatus.UNKNOWN
    elif dq.stale_parameters:
        dq.validation_quality = QualityStatus.VERIFIED
        dq.overall_status = QualityStatus.STALE
    elif dq.telemetry_completeness == "PARTIAL":
        dq.validation_quality = QualityStatus.VERIFIED
        dq.overall_status = QualityStatus.PARTIAL
    else:
        dq.validation_quality = QualityStatus.VERIFIED
        dq.overall_status = QualityStatus.VERIFIED

    if env_needs_save:
        active.data_quality_json = dq.model_dump_json()
        repo.save_mission_state(active)

    # Get active deviations and reconcile evidence with live context non-destructively
    active_deviations_entities = repo.get_active_deviations(active.mission_id)
    active_deviations = []
    for d in active_deviations_entities:
        ev = json.loads(d.evidence_json or "{}")
        if d.deviation_name in ("ENVIRONMENTAL_TELEMETRY_UNKNOWN", "ENVIRONMENTAL_TELEMETRY_STALE") or d.category == "DATA_QUALITY":
            stale_ev_unknown = ev.get("unknown_parameters")
            if stale_ev_unknown is not None and set(stale_ev_unknown) != set(dq.unknown_parameters):
                ev["unknown_parameters"] = dq.unknown_parameters
                ev["stale_parameters"] = dq.stale_parameters
                cond = (
                    f"Environmental parameters cannot be verified from active telemetry: {', '.join(dq.unknown_parameters)}"
                    if dq.unknown_parameters else f"Stale parameters: {', '.join(dq.stale_parameters)}"
                )
                repo.update_deviation_evidence(d.deviation_id, cond, ev)
                d.actual_condition = cond

            # If all parameters are known and fresh, deviation is resolved
            if len(dq.unknown_parameters) == 0 and len(dq.stale_parameters) == 0:
                repo.resolve_deviation(d.deviation_id, "All core environmental parameters verified and fresh. Telemetry stream normalized.")
                continue

        active_deviations.append(
            MissionDeviation(
                deviation_id=d.deviation_id,
                deviation_name=d.deviation_name,
                category=d.category,
                expected_condition=d.expected_condition,
                actual_condition=d.actual_condition,
                evidence=ev,
                severity=DeviationSeverity(d.severity),
                timestamp=d.timestamp,
                source=DataSource(d.source),
                confirmation_status=d.confirmation_status,
                resolved=d.resolved,
                resolution_notes=d.resolution_notes
            )
        )

    return MissionContextResponse(
        context_id=active.context_id,
        context_version=active.context_version,
        mission_id=active.mission_id,
        planned_profile=active.planned_profile_id,
        actual_mission_phase=active.actual_mission_phase,
        operational_state=OperationalState(active.operational_state),
        gravity_environment=GravityEnvironment(active.gravity_environment),
        gravity_value_g=active.gravity_value_g,
        communication=comm,
        environment=env,
        data_quality=dq,
        active_deviations=active_deviations,
        data_source=DataSource(active.data_source),
        last_updated=active.updated_at or datetime.now(timezone.utc)
    )

# ----------------- ENDPOINTS -----------------

@router.get("/health", tags=["System Health"])
def get_health():
    """Health check endpoint confirming Module 4 operational readiness."""
    return {
        "status": "HEALTHY",
        "service": settings.MODULE_NAME,
        "version": settings.VERSION,
        "database": "CONNECTED",
        "mode": "STANDALONE_INDEPENDENT",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/missions", response_model=List[MissionProfile], tags=["Mission Profiles"])
def list_missions():
    """Lists all registered mission profiles (ISS, Moon, Mars, etc.)."""
    return profile_mgr.list_profiles()

@router.get("/missions/current", response_model=MissionContextResponse, tags=["Current Mission Context"])
def get_current_mission_context(db: Session = Depends(get_db)):
    """Returns the comprehensive active planned and actual mission context."""
    return get_current_context_object(db)

@router.get("/missions/history", tags=["History & Audit"])
def get_mission_history(
    mission_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Returns complete historical audit trail and state transitions with pagination that survives restarts."""
    lim = int(limit.default if hasattr(limit, "default") else limit)
    off = int(offset.default if hasattr(offset, "default") else offset)
    history_mgr = ContextHistoryManager(db)
    return history_mgr.get_history(mission_id=mission_id, limit=lim, offset=off)

@router.post("/missions/select", response_model=MissionContextResponse, tags=["Mission Profiles"])
def select_mission_profile(req: MissionSelectRequest, db: Session = Depends(get_db)):
    """Switches the active mission profile while preserving historical audit records and continuity."""
    target_profile = profile_mgr.get_profile(req.mission_id)
    if not target_profile:
        raise HTTPException(status_code=404, detail=f"Mission profile '{req.mission_id}' not found.")

    repo = MissionRepository(db)
    history_mgr = ContextHistoryManager(db)

    # Create new active state entity from the chosen profile
    new_state = MissionStateEntity(
        mission_id=target_profile.mission_id,
        context_id=f"CTX-{target_profile.mission_id[:4]}-001",
        context_version=1,
        planned_profile_id=target_profile.mission_id,
        actual_mission_phase=target_profile.mission_phase,
        operational_state=OperationalState.NOMINAL.value,
        gravity_environment=target_profile.gravity_environment.value,
        gravity_value_g=target_profile.gravity_value_g,
        communication_json=CommunicationContext(
            status=CommStatus.NOMINAL,
            expected_delay_seconds=target_profile.communication_characteristics.expected_delay_seconds,
            bandwidth_mbps=target_profile.communication_characteristics.bandwidth_mbps,
            earth_reachable=True
        ).model_dump_json(),
        environment_json=EnvironmentStatus().model_dump_json(),
        data_quality_json=DataQualityContext().model_dump_json(),
        planned_context_json=json.dumps({"planned_profile_id": target_profile.mission_id}),
        data_source=DataSource.SIMULATED.value,
        is_active=True
    )
    repo.set_active_mission(target_profile.mission_id, new_state)

    # Record audit event
    history_mgr.record_audit(
        target_profile.mission_id,
        AuditEvent(
            event_type="MISSION_PROFILE_SELECTED",
            description=f"Switched active mission profile to {target_profile.mission_name}",
            evidence={"profile": target_profile.model_dump(mode="json")},
            operator_id=req.operator_id or "OPERATOR",
            context_version=1
        )
    )

    ctx = get_current_context_object(db)
    connection_manager.broadcast_sync({"event": "MISSION_SELECTED", "context": ctx.model_dump(mode="json")})
    return ctx

@router.get("/missions/current/deviations", response_model=List[MissionDeviation], tags=["Deviations"])
def get_current_deviations(db: Session = Depends(get_db)):
    """Returns all currently active detected discrepancies between planned and verified actual environment."""
    ctx = get_current_context_object(db)
    return ctx.active_deviations

@router.post("/missions/observations", response_model=Dict[str, Any], tags=["Environmental Observations"])
def ingest_observations(batch: ObservationBatchCreate, db: Session = Depends(get_db)):
    """Ingests incoming sensor observations, performs unit and staleness validation,
    detects contradictory readings, updates environmental state, and triggers deviation evaluation.
    """
    ctx = get_current_context_object(db)
    repo = MissionRepository(db)
    history_mgr = ContextHistoryManager(db)
    planned = profile_mgr.get_profile(ctx.planned_profile)

    if not planned:
        raise HTTPException(status_code=500, detail="Active planned profile could not be retrieved.")

    processed_observations: List[EnvironmentalObservation] = []
    recent_db_obs = repo.get_recent_observations(ctx.mission_id, limit=20)
    recent_history = [
        EnvironmentalObservation(
            observation_id=r.observation_id,
            parameter=r.parameter,
            value=r.canonical_value if r.canonical_value is not None else r.value_raw,
            unit=r.canonical_unit or r.unit,
            canonical_value=r.canonical_value,
            canonical_unit=r.canonical_unit,
            raw_value=r.value_raw,
            raw_unit=r.unit,
            idempotency_key=r.idempotency_key,
            timestamp=r.timestamp.replace(tzinfo=timezone.utc),
            source=DataSource(r.source),
            quality_status=QualityStatus(r.quality_status),
            validation_status=r.validation_status
        )
        for r in recent_db_obs
    ]

    for obs_in in batch.observations:
        # Check idempotency: If observation with same idempotency key exists, return it without creating duplicate records or audit events
        if obs_in.idempotency_key:
            existing_db = repo.get_observation_by_idempotency_key(ctx.mission_id, obs_in.idempotency_key)
            if existing_db:
                dup_obs = EnvironmentalObservation(
                    observation_id=existing_db.observation_id,
                    parameter=existing_db.parameter,
                    value=existing_db.canonical_value if existing_db.canonical_value is not None else existing_db.value_raw,
                    unit=existing_db.canonical_unit or existing_db.unit,
                    canonical_value=existing_db.canonical_value,
                    canonical_unit=existing_db.canonical_unit,
                    raw_value=existing_db.value_raw,
                    raw_unit=existing_db.unit,
                    idempotency_key=existing_db.idempotency_key,
                    timestamp=existing_db.timestamp.replace(tzinfo=timezone.utc),
                    source=DataSource(existing_db.source),
                    quality_status=QualityStatus(existing_db.quality_status),
                    validation_status=existing_db.validation_status,
                    metadata={"idempotent_duplicate": True, "note": "Duplicate rejected; existing record returned"}
                )
                processed_observations.append(dup_obs)
                continue

        validated_obs = env_mgr.validate_observation(obs_in, recent_history=recent_history)
        if not validated_obs.metadata.get("idempotent_duplicate"):
            history_mgr.record_observation(ctx.mission_id, validated_obs)
        processed_observations.append(validated_obs)

    # Synthesize updated actual environment
    verified_obs = [o for o in processed_observations if o.validation_status]
    new_env, new_dq = env_mgr.evaluate_environment_state(ctx.environment, verified_obs, planned_profile=planned)

    # Check for comm status observation
    comm = ctx.communication.model_copy(deep=True)
    for o in verified_obs:
        if o.parameter == "COMMUNICATION":
            try:
                comm.status = CommStatus(str(o.value).upper())
                comm.earth_reachable = comm.status not in [CommStatus.BLACKOUT, CommStatus.UNKNOWN]
            except Exception:
                pass

    # Build updated actual context
    actual_context = ActualMissionContext(
        actual_mission_phase=ctx.actual_mission_phase,
        gravity_environment=ctx.gravity_environment,
        gravity_value_g=ctx.gravity_value_g,
        habitat_status=new_env.habitat_status,
        life_support_status=new_env.life_support_status,
        mission_elapsed_seconds=0.0,
        communication=comm,
        environment=new_env,
        data_quality=new_dq
    )

    # Evaluate deviations
    detected_deviations = deviation_engine.evaluate_deviations(planned, actual_context)

    # Reconcile active deviations in database: resolve normalized deviations, update evidence, preserve genuine issues
    active_dev_entities = repo.get_active_deviations(ctx.mission_id)
    for active_dev in active_dev_entities:
        dev_name = active_dev.deviation_name
        dev_cat = active_dev.category

        # 1. Reconcile DATA_QUALITY deviations (e.g. ENVIRONMENTAL_TELEMETRY_UNKNOWN / STALE)
        if dev_cat == "DATA_QUALITY" or dev_name in ("ENVIRONMENTAL_TELEMETRY_UNKNOWN", "ENVIRONMENTAL_TELEMETRY_STALE"):
            if len(new_dq.unknown_parameters) == 0 and len(new_dq.stale_parameters) == 0:
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="All core environmental parameters verified and fresh. Telemetry stream normalized.",
                    context_version=ctx.context_version
                )
            else:
                # Parameters remain unknown or stale -> update evidence to reflect current reality (excluding normalized params)
                current_unknown = new_dq.unknown_parameters
                current_stale = new_dq.stale_parameters
                updated_evidence = {"unknown_parameters": current_unknown, "stale_parameters": current_stale}
                updated_condition = (
                    f"Environmental parameters cannot be verified from active telemetry: {', '.join(current_unknown)}"
                    if current_unknown else f"Stale parameters: {', '.join(current_stale)}"
                )
                repo.update_deviation_evidence(active_dev.deviation_id, updated_condition, updated_evidence)

        # 2. Reconcile physical deviations ONLY when their specific parameter is verified nominal
        elif dev_name in ("CABIN_PRESSURE_DEVIATION", "CABIN_PRESSURE_CRITICAL"):
            if new_env.cabin_pressure_status == "NOMINAL":
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason=f"Cabin pressure normalized within nominal bounds ({new_env.observed_parameters.get('CABIN_PRESSURE')} kPa).",
                    context_version=ctx.context_version
                )
        elif dev_name == "CO2_CONCENTRATION_HAZARD":
            if new_env.co2_status == "NOMINAL":
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="CO2 concentration normalized within nominal threshold.",
                    context_version=ctx.context_version
                )
        elif dev_name in ("SEVERE_RADIATION_SPIKE", "ELEVATED_RADIATION_WARNING"):
            if new_env.radiation_status == "NOMINAL":
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="Radiation dose rate returned to nominal background levels.",
                    context_version=ctx.context_version
                )
        elif dev_name in ("LIFE_SUPPORT_CRITICAL_FAILURE", "LIFE_SUPPORT_DEGRADATION"):
            if new_env.life_support_status == "NOMINAL":
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="Life-support system status returned to nominal operational state.",
                    context_version=ctx.context_version
                )
        elif dev_name in ("HABITAT_STRUCTURAL_COMPROMISE", "HABITAT_INTEGRITY_DEGRADATION"):
            if new_env.habitat_status == "NOMINAL":
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="Habitat integrity verified nominal.",
                    context_version=ctx.context_version
                )
        elif dev_name in ("COMMUNICATION_BLACKOUT", "COMMUNICATION_DEGRADATION"):
            if comm.status in (CommStatus.NOMINAL, CommStatus.OPTIMAL):
                history_mgr.resolve_deviation(
                    ctx.mission_id,
                    active_dev.deviation_id,
                    reason="Communication link restored to nominal availability.",
                    context_version=ctx.context_version
                )

    # 3. Record newly detected deviations that do not currently have an active entry
    current_active_names = {d.deviation_name for d in repo.get_active_deviations(ctx.mission_id)}
    for dev in detected_deviations:
        if dev.deviation_name not in current_active_names:
            history_mgr.record_deviation(ctx.mission_id, dev)

    # Re-evaluate automatic operational state suggestion
    active_critical = len([d for d in detected_deviations if d.severity == DeviationSeverity.CRITICAL])
    active_warning = len([d for d in detected_deviations if d.severity == DeviationSeverity.WARNING])
    is_unknown = len(new_dq.unknown_parameters) == 5 or new_dq.overall_status == QualityStatus.UNKNOWN
    suggested_state = contingency_mgr.determine_automatic_state_suggestion(
        ctx.operational_state, active_critical, active_warning, is_unknown
    )

    # Save updated state to active mission entity
    active_entity = repo.get_active_mission()
    if active_entity:
        active_entity.communication_json = comm.model_dump_json()
        active_entity.environment_json = new_env.model_dump_json()
        active_entity.data_quality_json = new_dq.model_dump_json()
        # Autonomous safety escalation: Only critical hazards automatically transition operational state to CONTINGENCY
        if suggested_state == OperationalState.CONTINGENCY and ctx.operational_state != OperationalState.CONTINGENCY:
            old_state = ctx.operational_state
            active_entity.operational_state = OperationalState.CONTINGENCY.value
            history_mgr.record_state_transition(
                ctx.mission_id,
                StateTransitionRecord(
                    from_state=old_state,
                    to_state=OperationalState.CONTINGENCY,
                    reason=f"Automatic emergency escalation triggered by {active_critical} critical deviations.",
                    evidence={"critical_count": active_critical, "warning_count": active_warning},
                    operator_id="AUTONOMOUS_CONTINGENCY_ENGINE",
                    context_version=ctx.context_version
                )
            )
        repo.save_mission_state(active_entity)

    refreshed_ctx = get_current_context_object(db)
    connection_manager.broadcast_sync({"event": "TELEMETRY_UPDATED", "context": refreshed_ctx.model_dump(mode="json")})

    return {
        "processed_count": len(processed_observations),
        "verified_count": len(verified_obs),
        "detected_deviations_count": len(detected_deviations),
        "suggested_operational_state": suggested_state.value,
        "operational_state": refreshed_ctx.operational_state.value,
        "observations": [o.model_dump(mode="json") for o in processed_observations]
    }

@router.post("/missions/transition", response_model=MissionContextResponse, tags=["Contingency Manager"])
def request_state_transition(req: ContextTransitionRequest, db: Session = Depends(get_db)):
    """Executes a controlled, validated state transition between operational states."""
    ctx = get_current_context_object(db)
    repo = MissionRepository(db)
    history_mgr = ContextHistoryManager(db)

    # Check for active critical deviations when attempting transition to NOMINAL
    evidence = dict(req.evidence)
    has_critical = any(d.severity == DeviationSeverity.CRITICAL for d in ctx.active_deviations)
    evidence["has_active_critical_deviations"] = has_critical

    is_valid, validation_msg = contingency_mgr.validate_transition(
        current_state=ctx.operational_state,
        target_state=req.target_state,
        reason=req.reason,
        evidence=evidence
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid operational state transition: {validation_msg}")

    # Record transition
    trans_record = StateTransitionRecord(
        from_state=ctx.operational_state,
        to_state=req.target_state,
        reason=req.reason,
        evidence=evidence,
        operator_id=req.operator_id or "MISSION_CONTROLLER",
        is_valid=True,
        context_version=ctx.context_version
    )
    history_mgr.record_state_transition(ctx.mission_id, trans_record)

    # If transitioning to NOMINAL, resolve non-active deviations
    if req.target_state == OperationalState.NOMINAL:
        for d in ctx.active_deviations:
            repo.resolve_deviation(d.deviation_id, f"Resolved via operator transition to NOMINAL: {req.reason}")

    active_entity = repo.get_active_mission()
    if active_entity:
        active_entity.operational_state = req.target_state.value
        repo.save_mission_state(active_entity)

    updated_ctx = get_current_context_object(db)
    connection_manager.broadcast_sync({"event": "STATE_TRANSITION", "context": updated_ctx.model_dump(mode="json")})
    return updated_ctx

@router.post("/missions/context/update", response_model=MissionContextResponse, tags=["Context Reconfiguration"])
def update_mission_context(req: ContextUpdateRequest, db: Session = Depends(get_db)):
    """Atomic reconfiguration of actual mission context attributes (phase, gravity, etc.).
    Preserves historical records and unaffected fields; increments context version.
    """
    ctx = get_current_context_object(db)
    repo = MissionRepository(db)
    history_mgr = ContextHistoryManager(db)

    updated_context, audit = reconfig_engine.apply_reconfiguration(ctx, req)
    history_mgr.record_audit(ctx.mission_id, audit)

    active_entity = repo.get_active_mission()
    if active_entity:
        active_entity.context_version = updated_context.context_version
        active_entity.actual_mission_phase = updated_context.actual_mission_phase
        active_entity.gravity_environment = updated_context.gravity_environment.value
        active_entity.gravity_value_g = updated_context.gravity_value_g
        repo.save_mission_state(active_entity)

    # Re-evaluate deviations under new actual context
    planned = profile_mgr.get_profile(ctx.planned_profile)
    if planned:
        actual_ctx = ActualMissionContext(
            actual_mission_phase=updated_context.actual_mission_phase,
            gravity_environment=updated_context.gravity_environment,
            gravity_value_g=updated_context.gravity_value_g,
            communication=updated_context.communication,
            environment=updated_context.environment,
            data_quality=updated_context.data_quality
        )
        deviations = deviation_engine.evaluate_deviations(planned, actual_ctx)
        for dev in deviations:
            history_mgr.record_deviation(ctx.mission_id, dev)

    refreshed_ctx = get_current_context_object(db)
    connection_manager.broadcast_sync({"event": "CONTEXT_RECONFIGURED", "context": refreshed_ctx.model_dump(mode="json")})
    return refreshed_ctx

@router.get("/missions/anomalies/detect", response_model=LayeredAnomalyReport, tags=["Mission Environment Intelligence"])
def detect_mission_anomalies(db: Session = Depends(get_db)):
    """Executes multi-layered anomaly detection across current spacecraft observations,
    combining physics limits, statistical Z-scores (SciPy), and explainable Isolation Forest ML.
    """
    ctx = get_current_context_object(db)
    repo = MissionRepository(db)
    recent_db_obs = repo.get_recent_observations(ctx.mission_id, limit=30)
    current_obs = [
        EnvironmentalObservation(
            observation_id=r.observation_id,
            parameter=r.parameter,
            value=r.canonical_value if r.canonical_value is not None else r.value_raw,
            unit=r.canonical_unit or r.unit,
            canonical_value=r.canonical_value,
            canonical_unit=r.canonical_unit,
            raw_value=r.value_raw,
            raw_unit=r.unit,
            timestamp=r.timestamp.replace(tzinfo=timezone.utc),
            source=DataSource(r.source),
            quality_status=QualityStatus(r.quality_status),
            validation_status=r.validation_status
        )
        for r in recent_db_obs[:6]
    ]
    historical_obs = [
        EnvironmentalObservation(
            observation_id=r.observation_id,
            parameter=r.parameter,
            value=r.canonical_value if r.canonical_value is not None else r.value_raw,
            unit=r.canonical_unit or r.unit,
            canonical_value=r.canonical_value,
            canonical_unit=r.canonical_unit,
            raw_value=r.value_raw,
            raw_unit=r.unit,
            timestamp=r.timestamp.replace(tzinfo=timezone.utc),
            source=DataSource(r.source),
            quality_status=QualityStatus(r.quality_status),
            validation_status=r.validation_status
        )
        for r in recent_db_obs[6:]
    ]
    report = anomaly_detector.analyze(current_obs, historical_obs)
    report.metadata["mission_id"] = ctx.mission_id
    report.metadata["context_version"] = ctx.context_version
    return report

@router.get("/missions/{mission_id}", response_model=MissionProfile, tags=["Mission Profiles"])
def get_mission_by_id(mission_id: str):
    """Retrieves a specific mission profile configuration by ID."""
    profile = profile_mgr.get_profile(mission_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Mission profile '{mission_id}' not found.")
    return profile

@router.get("/missions/{mission_id}/hazards", tags=["Mission Hazards"])
def get_mission_hazards(mission_id: str, db: Session = Depends(get_db)):
    """Returns all environmental hazards, active deviations, and nominal bounds for a mission."""
    profile = profile_mgr.get_profile(mission_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Mission profile '{mission_id}' not found.")
    repo = MissionRepository(db)
    active_deviations = repo.get_active_deviations(mission_id)

    return {
        "mission_id": mission_id,
        "destination": profile.destination,
        "habitat_type": profile.habitat_type,
        "nominal_bounds": profile.nominal_bounds,
        "environmental_categories": profile.environmental_monitoring_categories,
        "active_deviations_count": len(active_deviations),
        "active_deviations": [
            {
                "deviation_id": d.deviation_id,
                "name": d.deviation_name,
                "category": d.category,
                "severity": d.severity,
                "expected": d.expected_condition,
                "actual": d.actual_condition,
                "timestamp": d.timestamp.isoformat()
            }
            for d in active_deviations
        ]
    }

# ----------------- INTEGRATION & SIMULATOR ENDPOINTS -----------------

@router.get("/integrations/contract", tags=["Integration Contracts"])
def get_context_integration_contract(db: Session = Depends(get_db)):
    """Produces the standardized, versioned JSON distribution contract for Modules 1, 2, 3, 5, 6, 7."""
    ctx = get_current_context_object(db)
    return generate_standard_context_contract(ctx)

@router.post("/integrations/deliver/{target_module}", tags=["Integration Contracts"])
def deliver_context_to_mock_consumer(target_module: str, db: Session = Depends(get_db)):
    """Simulates delivery of Module 4 context to downstream teammate module adapters."""
    adapter = mock_adapters.get(target_module.upper())
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Adapter for '{target_module}' not found. Available: {list(mock_adapters.keys())}")
    ctx = get_current_context_object(db)
    contract = generate_standard_context_contract(ctx)
    result = adapter.deliver_mission_context(contract)
    return {
        "status": "DELIVERED",
        "mock_adapter_response": result,
        "dispatched_version": ctx.context_version
    }

@router.post("/simulator/scenario", tags=["Development Simulator"])
def run_simulator_scenario(
    scenario: str = Query(..., description="COMM_LOSS, LIFE_SUPPORT, CABIN_DEPRESSURIZATION, RADIATION_SPIKE, RESTORE_NOMINAL"),
    db: Session = Depends(get_db)
):
    """Triggers realistic simulated mission events and sensor streams clearly labeled SIMULATED."""
    ctx = get_current_context_object(db)
    telemetry = simulator.generate_scenario_telemetry(scenario)
    if not telemetry:
        raise HTTPException(status_code=400, detail=f"Unknown simulation scenario '{scenario}'.")

    # Ingest the generated scenario telemetry
    batch = ObservationBatchCreate(observations=telemetry)
    result = ingest_observations(batch, db)
    return {
        "scenario": scenario,
        "data_source": "SIMULATED",
        "notice": "SYNTHETIC DEVELOPMENT DATA ONLY - NOT A REAL SPACECRAFT",
        "ingestion_result": result
    }

@router.post("/simulator/generate-stream", tags=["Development Simulator"])
def generate_simulated_stream(db: Session = Depends(get_db)):
    """Generates a nominal synthetic sensor stream for the active destination."""
    ctx = get_current_context_object(db)
    planned = profile_mgr.get_profile(ctx.planned_profile)
    dest = planned.destination if planned else "MARS"
    telemetry = simulator.generate_nominal_telemetry_stream(dest)
    batch = ObservationBatchCreate(observations=telemetry)
    return ingest_observations(batch, db)

# ----------------- WEBSOCKET FOR REAL-TIME TELEMETRY -----------------

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Real-time bi-directional WebSocket connection for streaming mission telemetry and state changes."""
    await connection_manager.connect(websocket)
    try:
        # Send initial context
        db = next(get_db())
        ctx = get_current_context_object(db)
        await websocket.send_text(json.dumps({"event": "INITIAL_STATE", "context": ctx.model_dump(mode="json")}))
        
        while True:
            data = await websocket.receive_text()
            # Echo or process client ping
            await websocket.send_text(json.dumps({"event": "PONG", "timestamp": datetime.now(timezone.utc).isoformat()}))
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await connection_manager.disconnect(websocket)
