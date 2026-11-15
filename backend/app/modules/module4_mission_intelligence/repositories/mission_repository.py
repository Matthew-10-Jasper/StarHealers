import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.modules.module4_mission_intelligence.models.entities import (
    MissionStateEntity,
    EnvironmentalObservationEntity,
    MissionDeviationEntity,
    StateTransitionEntity,
    AuditLogEntity,
    QueuedReportEntity
)
from app.modules.module4_mission_intelligence.schemas.enums import OperationalState, ReportDeliveryStatus

class MissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_mission(self) -> Optional[MissionStateEntity]:
        return self.db.query(MissionStateEntity).filter(MissionStateEntity.is_active == True).order_by(desc(MissionStateEntity.id)).first()

    def get_mission_by_id(self, mission_id: str) -> Optional[MissionStateEntity]:
        return self.db.query(MissionStateEntity).filter(MissionStateEntity.mission_id == mission_id).order_by(desc(MissionStateEntity.id)).first()

    def save_mission_state(self, entity: MissionStateEntity) -> MissionStateEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def set_active_mission(self, mission_id: str, new_entity: MissionStateEntity) -> MissionStateEntity:
        try:
            # Deactivate any previous active mission state
            active_entities = self.db.query(MissionStateEntity).filter(MissionStateEntity.is_active == True).all()
            for entity in active_entities:
                entity.is_active = False
            self.db.add(new_entity)
            self.db.commit()
            self.db.refresh(new_entity)
            return new_entity
        except Exception:
            self.db.rollback()
            raise

    def save_observation(self, entity: EnvironmentalObservationEntity) -> EnvironmentalObservationEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def save_observations_batch(self, entities: List[EnvironmentalObservationEntity]) -> List[EnvironmentalObservationEntity]:
        try:
            self.db.add_all(entities)
            self.db.commit()
            for e in entities:
                self.db.refresh(e)
            return entities
        except Exception:
            self.db.rollback()
            raise

    def get_recent_observations(self, mission_id: str, limit: int = 50) -> List[EnvironmentalObservationEntity]:
        return self.db.query(EnvironmentalObservationEntity)\
            .filter(EnvironmentalObservationEntity.mission_id == mission_id)\
            .order_by(desc(EnvironmentalObservationEntity.timestamp))\
            .limit(limit)\
            .all()

    def get_observation_by_idempotency_key(self, mission_id: str, idempotency_key: str) -> Optional[EnvironmentalObservationEntity]:
        if not idempotency_key:
            return None
        return self.db.query(EnvironmentalObservationEntity)\
            .filter(
                EnvironmentalObservationEntity.mission_id == mission_id,
                EnvironmentalObservationEntity.idempotency_key == idempotency_key
            )\
            .first()

    def get_observations_for_parameter(self, mission_id: str, parameter: str, limit: int = 20) -> List[EnvironmentalObservationEntity]:
        return self.db.query(EnvironmentalObservationEntity)\
            .filter(EnvironmentalObservationEntity.mission_id == mission_id, EnvironmentalObservationEntity.parameter == parameter)\
            .order_by(desc(EnvironmentalObservationEntity.timestamp))\
            .limit(limit)\
            .all()

    def save_deviation(self, entity: MissionDeviationEntity) -> MissionDeviationEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def get_active_deviations(self, mission_id: str) -> List[MissionDeviationEntity]:
        return self.db.query(MissionDeviationEntity)\
            .filter(MissionDeviationEntity.mission_id == mission_id, MissionDeviationEntity.resolved == False)\
            .order_by(desc(MissionDeviationEntity.timestamp))\
            .all()

    def resolve_deviation(self, deviation_id: str, notes: str) -> Optional[MissionDeviationEntity]:
        try:
            dev = self.db.query(MissionDeviationEntity).filter(MissionDeviationEntity.deviation_id == deviation_id).first()
            if dev:
                dev.resolved = True
                dev.resolution_notes = notes
                self.db.commit()
                self.db.refresh(dev)
            return dev
        except Exception:
            self.db.rollback()
            raise

    def update_deviation_evidence(self, deviation_id: str, actual_condition: str, evidence: dict) -> Optional[MissionDeviationEntity]:
        try:
            dev = self.db.query(MissionDeviationEntity).filter(MissionDeviationEntity.deviation_id == deviation_id).first()
            if dev:
                dev.actual_condition = actual_condition
                dev.evidence_json = json.dumps(evidence)
                self.db.commit()
                self.db.refresh(dev)
            return dev
        except Exception:
            self.db.rollback()
            raise

    def record_state_transition(self, entity: StateTransitionEntity) -> StateTransitionEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def get_state_transitions(self, mission_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[StateTransitionEntity]:
        q = self.db.query(StateTransitionEntity)
        if mission_id:
            q = q.filter(StateTransitionEntity.mission_id == mission_id)
        return q.order_by(desc(StateTransitionEntity.timestamp)).offset(offset).limit(limit).all()

    def record_audit_event(self, entity: AuditLogEntity) -> AuditLogEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def get_audit_events(self, mission_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[AuditLogEntity]:
        q = self.db.query(AuditLogEntity)
        if mission_id:
            q = q.filter(AuditLogEntity.mission_id == mission_id)
        return q.order_by(desc(AuditLogEntity.timestamp)).offset(offset).limit(limit).all()

    def queue_report(self, entity: QueuedReportEntity) -> QueuedReportEntity:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception:
            self.db.rollback()
            raise

    def get_queued_reports(self, mission_id: str) -> List[QueuedReportEntity]:
        return self.db.query(QueuedReportEntity)\
            .filter(QueuedReportEntity.mission_id == mission_id)\
            .order_by(desc(QueuedReportEntity.created_at))\
            .all()

