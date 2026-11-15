import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.modules.module4_mission_intelligence.schemas.enums import DeviationSeverity, DataSource, GravityEnvironment, CommStatus
from app.modules.module4_mission_intelligence.schemas.mission_profile import MissionProfile
from app.modules.module4_mission_intelligence.schemas.context import ActualMissionContext, EnvironmentStatus, CommunicationContext
from app.modules.module4_mission_intelligence.schemas.deviation import MissionDeviation

logger = logging.getLogger("MissionDeviationEngine")

class MissionDeviationEngine:
    """Component C: Mission Deviation Detection Engine.
    Compares planned mission profiles with verified actual spacecraft environments.
    Applies configurable detection rules to classify discrepancies into INFO, WARNING, CRITICAL, or UNKNOWN.
    Does not assume missing info is an emergency.
    """
    def __init__(self):
        pass

    def evaluate_deviations(
        self,
        planned_profile: MissionProfile,
        actual_context: ActualMissionContext
    ) -> List[MissionDeviation]:
        """Runs all detection rules against the current planned vs actual mission contexts."""
        deviations: List[MissionDeviation] = []

        # Rule 1: Mission Phase Mismatch
        phase_dev = self._check_mission_phase(planned_profile, actual_context)
        if phase_dev:
            deviations.append(phase_dev)

        # Rule 2: Gravity Environment Mismatch
        grav_dev = self._check_gravity_mismatch(planned_profile, actual_context)
        if grav_dev:
            deviations.append(grav_dev)

        # Rule 3: Communication Degradation / Blackout
        comm_dev = self._check_communication(planned_profile, actual_context.communication)
        if comm_dev:
            deviations.append(comm_dev)

        # Rule 4: Radiation Observations
        rad_dev = self._check_radiation(planned_profile, actual_context.environment)
        if rad_dev:
            deviations.append(rad_dev)

        # Rule 5: Life-Support System Health
        lss_dev = self._check_life_support(planned_profile, actual_context.environment)
        if lss_dev:
            deviations.append(lss_dev)

        # Rule 6: Cabin Pressure & Atmosphere Integrity
        press_dev = self._check_cabin_pressure(planned_profile, actual_context.environment)
        if press_dev:
            deviations.append(press_dev)

        # Rule 7: CO2 Concentration
        co2_dev = self._check_co2(planned_profile, actual_context.environment)
        if co2_dev:
            deviations.append(co2_dev)

        # Rule 8: Habitat Structural / Mechanical Integrity
        hab_dev = self._check_habitat(planned_profile, actual_context.environment)
        if hab_dev:
            deviations.append(hab_dev)

        # Rule 9: Mission Duration / Extension
        ext_dev = self._check_mission_extension(planned_profile, actual_context)
        if ext_dev:
            deviations.append(ext_dev)

        # Rule 10: Unknown Environmental Telemetry Conditions
        unk_dev = self._check_unknown_conditions(actual_context)
        if unk_dev:
            deviations.append(unk_dev)

        return deviations

    def _check_mission_phase(self, planned: MissionProfile, actual: ActualMissionContext) -> Optional[MissionDeviation]:
        if actual.actual_mission_phase and planned.mission_phase:
            if actual.actual_mission_phase.upper() != planned.mission_phase.upper():
                severity = DeviationSeverity.WARNING
                if "ABORT" in actual.actual_mission_phase.upper() or "EMERGENCY" in actual.actual_mission_phase.upper():
                    severity = DeviationSeverity.CRITICAL
                return MissionDeviation(
                    deviation_name="MISSION_PHASE_DEVIATION",
                    category="TRAJECTORY_AND_PHASE",
                    expected_condition=f"Planned Phase: {planned.mission_phase}",
                    actual_condition=f"Actual Phase: {actual.actual_mission_phase}",
                    evidence={"planned_phase": planned.mission_phase, "actual_phase": actual.actual_mission_phase},
                    severity=severity,
                    source=DataSource.TELEMETRY
                )
        return None

    def _check_gravity_mismatch(self, planned: MissionProfile, actual: ActualMissionContext) -> Optional[MissionDeviation]:
        # Notice scientific distinction: Lunar orbit vs Lunar surface, Mars transit vs Mars surface
        if actual.gravity_environment != GravityEnvironment.UNKNOWN:
            if actual.gravity_environment != planned.gravity_environment:
                severity = DeviationSeverity.WARNING
                # Large unexpected acceleration in planned microgravity
                if planned.gravity_environment == GravityEnvironment.MICROGRAVITY and actual.gravity_value_g > 0.1:
                    severity = DeviationSeverity.CRITICAL
                return MissionDeviation(
                    deviation_name="GRAVITY_ENVIRONMENT_MISMATCH",
                    category="GRAVITY",
                    expected_condition=f"{planned.gravity_environment.value} ({planned.gravity_value_g:.3f}g)",
                    actual_condition=f"{actual.gravity_environment.value} ({actual.gravity_value_g:.3f}g)",
                    evidence={
                        "planned_env": planned.gravity_environment.value,
                        "planned_g": planned.gravity_value_g,
                        "actual_env": actual.gravity_environment.value,
                        "actual_g": actual.gravity_value_g
                    },
                    severity=severity,
                    source=DataSource.TELEMETRY
                )
        return None

    def _check_communication(self, planned: MissionProfile, comm: CommunicationContext) -> Optional[MissionDeviation]:
        expected_delay = planned.communication_characteristics.expected_delay_seconds
        if comm.status == CommStatus.BLACKOUT:
            return MissionDeviation(
                deviation_name="COMMUNICATION_BLACKOUT",
                category="COMMUNICATION",
                expected_condition=f"Link active with expected latency ~{expected_delay:.1f}s",
                actual_condition="Complete communication blackout with Earth Mission Control",
                evidence={"comm_status": comm.status.value, "earth_reachable": comm.earth_reachable, "queued_reports": comm.queued_reports_count},
                severity=DeviationSeverity.CRITICAL,
                source=DataSource.TELEMETRY
            )
        elif comm.status in [CommStatus.DEGRADED, CommStatus.INTERMITTENT]:
            return MissionDeviation(
                deviation_name="COMMUNICATION_DEGRADATION",
                category="COMMUNICATION",
                expected_condition=f"Nominal link with latency ~{expected_delay:.1f}s",
                actual_condition=f"Link degraded: status={comm.status.value}, latency={comm.expected_delay_seconds:.1f}s",
                evidence={"comm_status": comm.status.value, "delay_s": comm.expected_delay_seconds, "bandwidth_mbps": comm.bandwidth_mbps},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_radiation(self, planned: MissionProfile, env: EnvironmentStatus) -> Optional[MissionDeviation]:
        rad_status = env.radiation_status.upper()
        if "CRITICAL" in rad_status or "SOLAR_PARTICLE_EVENT" in rad_status:
            return MissionDeviation(
                deviation_name="CRITICAL_RADIATION_EVENT",
                category="RADIATION",
                expected_condition="Nominal background cosmic radiation levels",
                actual_condition=f"Severe radiation spike detected: {env.radiation_status}",
                evidence={"radiation_status": env.radiation_status, "observed_parameters": env.observed_parameters.get("RADIATION")},
                severity=DeviationSeverity.CRITICAL,
                source=DataSource.TELEMETRY
            )
        elif "ELEVATED" in rad_status or "WARNING" in rad_status:
            return MissionDeviation(
                deviation_name="ELEVATED_RADIATION_WARNING",
                category="RADIATION",
                expected_condition="Nominal background cosmic radiation levels",
                actual_condition=f"Elevated radiation observation: {env.radiation_status}",
                evidence={"radiation_status": env.radiation_status, "observed_parameters": env.observed_parameters.get("RADIATION")},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_life_support(self, planned: MissionProfile, env: EnvironmentStatus) -> Optional[MissionDeviation]:
        lss = env.life_support_status.upper()
        if lss in ["CRITICAL", "FAILURE", "EMERGENCY", "OFFLINE"]:
            return MissionDeviation(
                deviation_name="LIFE_SUPPORT_CRITICAL_FAILURE",
                category="LIFE_SUPPORT",
                expected_condition="Primary and redundant ECLSS loops fully operational",
                actual_condition=f"ECLSS life-support status is {env.life_support_status}",
                evidence={"life_support_status": env.life_support_status},
                severity=DeviationSeverity.CRITICAL,
                source=DataSource.TELEMETRY
            )
        elif lss in ["DEGRADED", "WARNING", "PARTIAL_FAILURE"]:
            return MissionDeviation(
                deviation_name="LIFE_SUPPORT_DEGRADATION",
                category="LIFE_SUPPORT",
                expected_condition="Primary and redundant ECLSS loops fully operational",
                actual_condition=f"ECLSS life support operating in degraded backup loop: {env.life_support_status}",
                evidence={"life_support_status": env.life_support_status},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_cabin_pressure(self, planned: MissionProfile, env: EnvironmentStatus) -> Optional[MissionDeviation]:
        pressure_status = env.cabin_pressure_status.upper()
        if "CRITICAL" in pressure_status or "RAPID_DEPRESSURIZATION" in pressure_status:
            return MissionDeviation(
                deviation_name="CABIN_PRESSURE_CRITICAL",
                category="CABIN_ATMOSPHERE",
                expected_condition="Cabin pressure maintained at nominal atmospheric setpoint",
                actual_condition=f"Cabin pressure critical: {env.cabin_pressure_status}",
                evidence={"pressure_status": env.cabin_pressure_status, "observed_pressure": env.observed_parameters.get("CABIN_PRESSURE")},
                severity=DeviationSeverity.CRITICAL,
                source=DataSource.TELEMETRY
            )
        elif "DEGRADED" in pressure_status or "LOW" in pressure_status:
            return MissionDeviation(
                deviation_name="CABIN_PRESSURE_DEVIATION",
                category="CABIN_ATMOSPHERE",
                expected_condition="Cabin pressure maintained at nominal atmospheric setpoint",
                actual_condition=f"Cabin pressure degraded: {env.cabin_pressure_status}",
                evidence={"pressure_status": env.cabin_pressure_status, "observed_pressure": env.observed_parameters.get("CABIN_PRESSURE")},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_co2(self, planned: MissionProfile, env: EnvironmentStatus) -> Optional[MissionDeviation]:
        co2_status = env.co2_status.upper()
        if "CRITICAL" in co2_status or "HIGH" in co2_status and "ELEVATED" not in co2_status:
            return MissionDeviation(
                deviation_name="CO2_CONCENTRATION_HAZARD",
                category="CABIN_ATMOSPHERE",
                expected_condition="CO2 scrubbers holding partial pressure < 3.0 mmHg",
                actual_condition=f"CO2 concentration hazard: {env.co2_status}",
                evidence={"co2_status": env.co2_status, "observed_co2": env.observed_parameters.get("CO2_CONCENTRATION")},
                severity=DeviationSeverity.CRITICAL if "CRITICAL" in co2_status else DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_habitat(self, planned: MissionProfile, env: EnvironmentStatus) -> Optional[MissionDeviation]:
        hab = env.habitat_status.upper()
        if hab in ["DECOMPRESSION", "BREACH", "CRITICAL"]:
            return MissionDeviation(
                deviation_name="HABITAT_STRUCTURAL_COMPROMISE",
                category="HABITAT",
                expected_condition=f"Habitat nominal: {planned.habitat_type}",
                actual_condition=f"Habitat compromise reported: {env.habitat_status}",
                evidence={"habitat_status": env.habitat_status},
                severity=DeviationSeverity.CRITICAL,
                source=DataSource.TELEMETRY
            )
        elif hab in ["DEGRADED", "MINOR_LEAK", "MICROMETEOROID_IMPACT"]:
            return MissionDeviation(
                deviation_name="HABITAT_INTEGRITY_DEGRADATION",
                category="HABITAT",
                expected_condition=f"Habitat nominal: {planned.habitat_type}",
                actual_condition=f"Habitat integrity warning: {env.habitat_status}",
                evidence={"habitat_status": env.habitat_status},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

    def _check_mission_extension(self, planned: MissionProfile, actual: ActualMissionContext) -> Optional[MissionDeviation]:
        if planned.expected_duration_days:
            elapsed_days = actual.mission_elapsed_seconds / 86400.0
            if elapsed_days > (planned.expected_duration_days * 1.15):
                return MissionDeviation(
                    deviation_name="MISSION_DURATION_OVERRUN",
                    category="MISSION_TIMELINE",
                    expected_condition=f"Planned mission duration: {planned.expected_duration_days} days",
                    actual_condition=f"Elapsed time is {elapsed_days:.1f} days (15%+ beyond plan)",
                    evidence={"planned_days": planned.expected_duration_days, "elapsed_days": elapsed_days},
                    severity=DeviationSeverity.INFO,
                    source=DataSource.TELEMETRY
                )
        return None

    def _check_unknown_conditions(self, actual: ActualMissionContext) -> Optional[MissionDeviation]:
        # If any core environmental parameters are missing, preserve a DATA_QUALITY deviation reflecting current unknown fields
        if actual.data_quality.unknown_parameters:
            return MissionDeviation(
                deviation_name="ENVIRONMENTAL_TELEMETRY_UNKNOWN",
                category="DATA_QUALITY",
                expected_condition="Verified active telemetry streams for all core spacecraft environmental parameters",
                actual_condition=f"Core environmental parameters unverified: {', '.join(actual.data_quality.unknown_parameters)}",
                evidence={
                    "unknown_parameters": actual.data_quality.unknown_parameters,
                    "stale_parameters": actual.data_quality.stale_parameters
                },
                severity=DeviationSeverity.UNKNOWN,
                source=DataSource.TELEMETRY
            )
        elif actual.data_quality.stale_parameters:
            return MissionDeviation(
                deviation_name="ENVIRONMENTAL_TELEMETRY_STALE",
                category="DATA_QUALITY",
                expected_condition="Fresh telemetry for all observed parameters",
                actual_condition=f"Telemetry parameters stale: {', '.join(actual.data_quality.stale_parameters)}",
                evidence={"stale_parameters": actual.data_quality.stale_parameters},
                severity=DeviationSeverity.WARNING,
                source=DataSource.TELEMETRY
            )
        return None

