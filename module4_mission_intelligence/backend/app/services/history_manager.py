import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.repositories.mission_repository import MissionRepository
from app.models.entities import (
    MissionStateEntity,
    EnvironmentalObservationEntity,
    MissionDeviationEntity,
    StateTransitionEntity,
    AuditLogEntity,
    QueuedReportEntity
)
from app.schemas.context import MissionContextResponse
from app.schemas.observation import EnvironmentalObservation
from app.schemas.deviation import MissionDeviation
from app.schemas.history import AuditEvent, StateTransitionRecord, QueuedReport

logger = logging.getLogger("ContextHistoryManager")

class ContextHistoryManager:
    """Component G: Context History and Audit Manager.
    Persists immutable audit trails of all mission state versions, transitions,
    environmental observations, deviations, and operator interventions.
    Guarantees persistence across restarts and retains complete history when switching profiles.
    """
    def __init__(self, db: Session):
        self.repo = MissionRepository(db)

    def persist_mission_context(self, context: MissionContextResponse, planned_profile_id: str) -> MissionStateEntity:
        entity = MissionStateEntity(
            mission_id=context.mission_id,
            context_id=context.context_id,
            context_version=context.context_version,
            planned_profile_id=planned_profile_id,
            actual_mission_phase=context.actual_mission_phase,
            operational_state=context.operational_state.value,
            gravity_environment=context.gravity_environment.value,
            gravity_value_g=context.gravity_value_g,
            communication_json=context.communication.model_dump_json(),
            environment_json=context.environment.model_dump_json(),
            data_quality_json=context.data_quality.model_dump_json(),
            planned_context_json=json.dumps({"planned_profile_id": planned_profile_id}),
            data_source=context.data_source.value,
            is_active=True
        )
        return self.repo.set_active_mission(context.mission_id, entity)

    def record_observation(self, mission_id: str, obs: EnvironmentalObservation) -> EnvironmentalObservationEntity:
        entity = EnvironmentalObservationEntity(
            observation_id=obs.observation_id,
            mission_id=mission_id,
            parameter=obs.parameter,
            value_raw=str(obs.raw_value if obs.raw_value is not None else obs.value),
            unit=obs.raw_unit if obs.raw_unit is not None else obs.unit,
            canonical_value=obs.canonical_value if isinstance(obs.canonical_value, (int, float)) else (obs.value if isinstance(obs.value, (int, float)) else None),
            canonical_unit=obs.canonical_unit or obs.unit,
            idempotency_key=obs.idempotency_key,
            timestamp=obs.timestamp,
            source=obs.source.value,
            quality_status=obs.quality_status.value,
            validation_status=obs.validation_status,
            metadata_json=json.dumps(obs.metadata)
        )
        return self.repo.save_observation(entity)

    def record_deviation(self, mission_id: str, dev: MissionDeviation) -> MissionDeviationEntity:
        entity = MissionDeviationEntity(
            deviation_id=dev.deviation_id,
            mission_id=mission_id,
            deviation_name=dev.deviation_name,
            category=dev.category,
            expected_condition=dev.expected_condition,
            actual_condition=dev.actual_condition,
            severity=dev.severity.value,
            evidence_json=json.dumps(dev.evidence),
            timestamp=dev.timestamp,
            source=dev.source.value,
            confirmation_status=dev.confirmation_status,
            resolved=dev.resolved,
            resolution_notes=dev.resolution_notes
        )
        return self.repo.save_deviation(entity)

    def resolve_deviation(self, mission_id: str, deviation_id: str, reason: str, context_version: int = 1) -> Optional[MissionDeviationEntity]:
        dev = self.repo.resolve_deviation(deviation_id, reason)
        if dev:
            self.record_audit(
                mission_id,
                AuditEvent(
                    event_type="DEVIATION_RESOLVED",
                    description=f"Resolved deviation {dev.deviation_name} ({deviation_id}): {reason}",
                    evidence={"deviation_id": deviation_id, "deviation_name": dev.deviation_name, "resolution_notes": reason},
                    context_version=context_version
                )
            )
        return dev

    def record_state_transition(self, mission_id: str, record: StateTransitionRecord) -> StateTransitionEntity:
        entity = StateTransitionEntity(
            transition_id=record.transition_id,
            mission_id=mission_id,
            from_state=record.from_state.value,
            to_state=record.to_state.value,
            reason=record.reason,
            evidence_json=json.dumps(record.evidence),
            operator_id=record.operator_id,
            is_valid=record.is_valid,
            context_version=record.context_version,
            timestamp=record.timestamp
        )
        return self.repo.record_state_transition(entity)

    def record_audit(self, mission_id: str, audit: AuditEvent) -> AuditLogEntity:
        entity = AuditLogEntity(
            event_id=audit.event_id,
            mission_id=mission_id,
            event_type=audit.event_type,
            description=audit.description,
            evidence_json=json.dumps(audit.evidence),
            operator_id=audit.operator_id,
            context_version=audit.context_version,
            timestamp=audit.timestamp
        )
        return self.repo.record_audit_event(entity)

    def get_history(self, mission_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Gathers unified timeline of audits, transitions, and observations with pagination."""
        audits = self.repo.get_audit_events(mission_id=mission_id, limit=limit, offset=offset)
        transitions = self.repo.get_state_transitions(mission_id=mission_id, limit=limit, offset=offset)
        return {
            "limit": limit,
            "offset": offset,
            "audit_events": [
                {
                    "event_id": a.event_id,
                    "event_type": a.event_type,
                    "description": a.description,
                    "evidence": json.loads(a.evidence_json or "{}"),
                    "operator_id": a.operator_id,
                    "context_version": a.context_version,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in audits
            ],
            "state_transitions": [
                {
                    "transition_id": t.transition_id,
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "reason": t.reason,
                    "evidence": json.loads(t.evidence_json or "{}"),
                    "operator_id": t.operator_id,
                    "is_valid": t.is_valid,
                    "context_version": t.context_version,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in transitions
            ]
        }

