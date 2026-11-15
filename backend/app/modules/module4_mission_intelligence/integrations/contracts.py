from datetime import datetime, timezone
from typing import Dict, Any, List
from app.modules.module4_mission_intelligence.schemas.context import MissionContextResponse

def generate_standard_context_contract(context: MissionContextResponse) -> Dict[str, Any]:
    """Generates the standardized, versioned JSON distribution payload
    specified in STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT.
    """
    return {
        "$schema": "./mission_context_v1_schema.json",
        "contract_name": "STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT",
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context_id": context.context_id,
        "context_version": context.context_version,
        "mission_id": context.mission_id,
        "planned_profile": context.planned_profile,
        "actual_mission_phase": context.actual_mission_phase,
        "operational_state": context.operational_state.value,
        "gravity_environment": context.gravity_environment.value,
        "gravity_value_g": context.gravity_value_g,
        "communication": {
            "status": context.communication.status.value,
            "expected_delay_seconds": context.communication.expected_delay_seconds,
            "bandwidth_mbps": context.communication.bandwidth_mbps,
            "earth_reachable": context.communication.earth_reachable,
            "queued_reports_count": context.communication.queued_reports_count,
            "last_contact_timestamp": context.communication.last_contact_timestamp.isoformat() if context.communication.last_contact_timestamp else None,
            "last_acknowledged_timestamp": context.communication.last_acknowledged_timestamp.isoformat() if context.communication.last_acknowledged_timestamp else None
        },
        "environment": {
            "radiation_status": context.environment.radiation_status,
            "cabin_pressure_status": context.environment.cabin_pressure_status,
            "co2_status": context.environment.co2_status,
            "life_support_status": context.environment.life_support_status,
            "habitat_status": context.environment.habitat_status,
            "observed_parameters": context.environment.observed_parameters
        },
        "data_quality": {
            "overall_status": context.data_quality.overall_status.value,
            "unknown_parameters": context.data_quality.unknown_parameters,
            "stale_parameters": context.data_quality.stale_parameters,
            "contradictory_parameters": context.data_quality.contradictory_parameters,
            "last_telemetry_timestamp": context.data_quality.last_telemetry_timestamp.isoformat() if context.data_quality.last_telemetry_timestamp else None
        },
        "active_deviations_count": len(context.active_deviations),
        "deviations_summary": [
            {
                "deviation_id": d.deviation_id,
                "deviation_name": d.deviation_name,
                "category": d.category,
                "severity": d.severity.value,
                "expected": d.expected_condition,
                "actual": d.actual_condition
            }
            for d in context.active_deviations
        ],
        "data_source": context.data_source.value,
        "consumer_targets": [
            "MODULE_1_ASTRONAUT_HEALTH_MONITORING",
            "MODULE_2_HUMAN_BODY_MAP_INTERFACE",
            "MODULE_3_CLINICAL_TRIAGE_ENGINE",
            "MODULE_5_RADIATION_CO2_SLEEP_SIMULATOR",
            "MODULE_6_MISSION_DURATION_CONTEXT",
            "MODULE_7_ENVIRONMENT_ANALYTICS"
        ]
    }

