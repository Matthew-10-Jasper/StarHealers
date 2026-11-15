import logging
from typing import Tuple, Optional, Dict, Any, List
from app.schemas.enums import OperationalState
from app.schemas.history import StateTransitionRecord

logger = logging.getLogger("ContingencyStateManager")

# Graph of allowed transitions:
# key: from_state -> set of valid target states
VALID_STATE_TRANSITIONS = {
    OperationalState.NOMINAL: {
        OperationalState.DEGRADED,
        OperationalState.CONTINGENCY,
        OperationalState.UNKNOWN
    },
    OperationalState.DEGRADED: {
        OperationalState.NOMINAL,      # Requires verified evidence that degraded condition cleared
        OperationalState.CONTINGENCY,
        OperationalState.RECOVERY,
        OperationalState.UNKNOWN
    },
    OperationalState.CONTINGENCY: {
        OperationalState.RECOVERY,     # Standard operational path
        OperationalState.DEGRADED,     # If hazard downgraded under emergency protocol
        OperationalState.UNKNOWN
    },
    OperationalState.RECOVERY: {
        OperationalState.NOMINAL,      # Requires verified evidence that all systems are stable
        OperationalState.DEGRADED,     # Partial restoration
        OperationalState.CONTINGENCY,  # Relapse into emergency
        OperationalState.UNKNOWN
    },
    OperationalState.UNKNOWN: {
        OperationalState.NOMINAL,
        OperationalState.DEGRADED,
        OperationalState.CONTINGENCY,
        OperationalState.RECOVERY
    }
}

class ContingencyStateManager:
    """Component D: Contingency State Manager.
    Enforces a strict deterministic state transition graph across 5 operational states.
    Validates state transitions and rejects unauthorized or unsafe transitions.
    Requires verified telemetry evidence to return to NOMINAL.
    """
    def __init__(self):
        pass

    def validate_transition(
        self,
        current_state: OperationalState,
        target_state: OperationalState,
        reason: str,
        evidence: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Validates whether a requested operational state transition is allowed."""
        if current_state == target_state:
            return True, f"System already in state {target_state.value}"

        allowed_targets = VALID_STATE_TRANSITIONS.get(current_state, set())
        if target_state not in allowed_targets:
            return False, f"Illegal state transition from {current_state.value} to {target_state.value}. Allowed: {[s.value for s in allowed_targets]}"

        # Transition to NOMINAL requires verified evidence
        if target_state == OperationalState.NOMINAL:
            if not evidence:
                return False, "Transition to NOMINAL requires verified evidence payload proving system normalization."
            # Check for unresolved critical flags in evidence
            if evidence.get("has_active_critical_deviations", False):
                return False, "Cannot transition to NOMINAL while active critical mission deviations remain."

        # Transition to CONTINGENCY requires reason
        if target_state == OperationalState.CONTINGENCY:
            if not reason or len(reason.strip()) < 5:
                return False, "Transition to CONTINGENCY requires an explicit documented reason."

        return True, "Transition validated successfully."

    def determine_automatic_state_suggestion(
        self,
        current_state: OperationalState,
        active_critical_count: int,
        active_warning_count: int,
        is_unknown_telemetry: bool
    ) -> OperationalState:
        """Suggests operational state based on verified mission deviations and telemetry health."""
        if is_unknown_telemetry:
            return OperationalState.UNKNOWN
        if active_critical_count > 0:
            return OperationalState.CONTINGENCY
        if active_warning_count > 0:
            if current_state == OperationalState.CONTINGENCY:
                return OperationalState.RECOVERY
            return OperationalState.DEGRADED
        if current_state in [OperationalState.CONTINGENCY, OperationalState.RECOVERY]:
            return OperationalState.RECOVERY
        return OperationalState.NOMINAL

