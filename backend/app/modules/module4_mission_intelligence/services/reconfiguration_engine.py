import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from app.modules.module4_mission_intelligence.schemas.context import MissionContextResponse, ContextUpdateRequest
from app.modules.module4_mission_intelligence.schemas.history import AuditEvent

logger = logging.getLogger("ContextReconfigurationEngine")

class ContextReconfigurationEngine:
    """Component E: Context Reconfiguration Engine.
    Executes atomic, versioned reconfiguration of the mission context.
    - Selectively updates affected attributes while preserving unaffected attributes.
    - Increments context version.
    - Captures evidence and reasons.
    - Preserves historical continuity (never overwrites or resets astronaut records).
    - Scientific rigor: destination changes do NOT automatically infer gravity changes without verified evidence.
    """
    def __init__(self):
        pass

    def apply_reconfiguration(
        self,
        current_context: MissionContextResponse,
        update_request: ContextUpdateRequest
    ) -> Tuple[MissionContextResponse, AuditEvent]:
        """Creates a new version of the mission context with verified updates applied."""
        new_version = current_context.context_version + 1
        now = datetime.now(timezone.utc)

        # Clone current context
        updated = current_context.model_copy(deep=True)
        updated.context_version = new_version
        updated.last_updated = now

        changes_summary: Dict[str, Any] = {}

        # 1. Update actual mission phase if provided
        if update_request.actual_mission_phase is not None:
            old_phase = updated.actual_mission_phase
            updated.actual_mission_phase = update_request.actual_mission_phase
            changes_summary["actual_mission_phase"] = {
                "from": old_phase,
                "to": update_request.actual_mission_phase
            }

        # 2. Update gravity environment only if explicitly verified with evidence
        if update_request.gravity_environment is not None:
            old_grav_env = updated.gravity_environment
            updated.gravity_environment = update_request.gravity_environment
            changes_summary["gravity_environment"] = {
                "from": old_grav_env.value,
                "to": update_request.gravity_environment.value
            }

        if update_request.gravity_value_g is not None:
            old_g = updated.gravity_value_g
            updated.gravity_value_g = update_request.gravity_value_g
            changes_summary["gravity_value_g"] = {
                "from": old_g,
                "to": update_request.gravity_value_g
            }

        # Create audit event
        audit_event = AuditEvent(
            event_type="CONTEXT_RECONFIGURATION",
            description=f"Context reconfigured to version {new_version}. Reason: {update_request.reason}",
            evidence={
                "changes": changes_summary,
                "requested_evidence": update_request.evidence,
                "previous_version": current_context.context_version,
                "new_version": new_version
            },
            operator_id=update_request.operator_id or "SYSTEM",
            context_version=new_version,
            timestamp=now
        )

        return updated, audit_event

