import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.schemas.enums import CommStatus, ReportDeliveryStatus
from app.schemas.context import CommunicationContext
from app.schemas.history import QueuedReport

logger = logging.getLogger("MissionConstraintsManager")

class MissionConstraintsManager:
    """Component F: Mission Constraints Manager.
    Enforces deep-space operational constraints and local-first autonomy:
    - Never assumes instantaneous ground control response.
    - Manages communication pipeline states: LOCALLY_GENERATED -> QUEUED -> TRANSMITTED -> ACKNOWLEDGED.
    - Strictly prevents claiming Earth delivery without explicit telemetry acknowledgement.
    - Does NOT override flight crew authority or issue unverified medical prescriptions.
    """
    def __init__(self):
        pass

    def evaluate_constraints(
        self,
        comm_context: CommunicationContext,
        operational_state: str,
        active_critical_deviations_count: int
    ) -> Dict[str, Any]:
        """Calculates current operational constraints and local operational restrictions."""
        delay = comm_context.expected_delay_seconds
        earth_reachable = comm_context.earth_reachable and comm_context.status not in [CommStatus.BLACKOUT, CommStatus.UNKNOWN]

        # Calculate round-trip time in seconds
        round_trip_delay_seconds = delay * 2.0
        autonomous_decision_window_seconds = max(round_trip_delay_seconds, 60.0)

        # Operational restrictions
        restrictions = []
        if comm_context.status == CommStatus.BLACKOUT:
            restrictions.append("STRICT_AUTONOMOUS_PROTOCOL_ACTIVE: Earth ground control unreachable")
        elif delay > 300.0: # > 5 min one-way
            restrictions.append("DELAY_TOLERANT_PROTOCOL_ACTIVE: Real-time ground intervention impossible")

        if active_critical_deviations_count > 0:
            restrictions.append("HAZARD_CONTAINMENT_PRIORITY: Non-essential operations suspended")

        return {
            "earth_reachable": earth_reachable,
            "one_way_delay_seconds": delay,
            "round_trip_delay_seconds": round_trip_delay_seconds,
            "autonomous_decision_window_seconds": autonomous_decision_window_seconds,
            "local_autonomy_required": delay > 60.0 or not earth_reachable,
            "operational_restrictions": restrictions,
            "queued_reports_count": comm_context.queued_reports_count
        }

    def generate_local_report(
        self,
        mission_id: str,
        report_type: str,
        payload: Dict[str, Any]
    ) -> QueuedReport:
        """Creates a locally generated mission/medical report stored locally first."""
        report = QueuedReport(
            report_id=f"REP-{uuid.uuid4().hex[:8].upper()}",
            report_type=report_type,
            payload=payload,
            delivery_status=ReportDeliveryStatus.LOCALLY_GENERATED,
            created_at=datetime.now(timezone.utc)
        )
        logger.info(f"Generated local report {report.report_id} of type {report_type}")
        return report

    def queue_report_for_uplink(self, report: QueuedReport) -> QueuedReport:
        """Marks report as queued in the vehicle high-gain / DSN transmission buffer."""
        report.delivery_status = ReportDeliveryStatus.QUEUED
        return report

    def transmit_report(self, report: QueuedReport, comm_context: CommunicationContext) -> QueuedReport:
        """Simulates report uplink transmission. Does NOT mark as acknowledged."""
        if not comm_context.earth_reachable or comm_context.status == CommStatus.BLACKOUT:
            logger.warning(f"Transmission failed for {report.report_id}: Earth unreachable")
            report.delivery_status = ReportDeliveryStatus.QUEUED
            return report

        report.delivery_status = ReportDeliveryStatus.TRANSMITTED
        report.transmitted_at = datetime.now(timezone.utc)
        logger.info(f"Transmitted report {report.report_id}. Waiting for Earth receipt acknowledgement.")
        return report

    def acknowledge_report(self, report: QueuedReport, ack_id: str) -> QueuedReport:
        """Records verified confirmation that Earth Ground Station received the transmission."""
        report.delivery_status = ReportDeliveryStatus.ACKNOWLEDGED
        report.acknowledged_at = datetime.now(timezone.utc)
        report.acknowledgement_id = ack_id
        logger.info(f"Report {report.report_id} verified acknowledged by Earth: {ack_id}")
        return report

