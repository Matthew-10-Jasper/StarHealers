import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.core.units import validate_and_convert_observation, UnitConversionResult, PARAMETER_ALIASES
from app.schemas.enums import (
    DataSource, QualityStatus, GravityEnvironment, CommStatus
)
from app.schemas.observation import EnvironmentalObservation, ObservationCreate
from app.schemas.context import EnvironmentStatus, DataQualityContext, CommunicationContext
from app.schemas.mission_profile import MissionProfile

logger = logging.getLogger("ActualEnvironmentManager")

VALID_UNITS = {
    "CABIN_PRESSURE": ["kPa", "kpa", "psi", "hPa", "bar", "mmHg", "torr", "atm"],
    "CO2_CONCENTRATION": ["mmHg", "mmhg", "ppm", "%"],
    "CO2": ["mmHg", "mmhg", "ppm", "%"],
    "O2_PERCENTAGE": ["%", "percent"],
    "RADIATION": ["mSv/day", "msv/day", "uSv/h", "mSv/h", "Sv/yr", "rem/day", "mrem/h", "mGy/d", "mGy/day", "uGy/h", "rad/day", "cGy/d"],
    "GRAVITY": ["g", "m/s2", "m/s^2"],
    "LIFE_SUPPORT": ["status", "string", "enum"],
    "HABITAT_INTEGRITY": ["status", "string", "enum"],
    "COMMUNICATION": ["status", "delay_s", "mbps"],
    "COMMUNICATION_DELAY": ["s", "sec", "min", "h", "hour", "ms"]
}

class ActualEnvironmentManager:
    """Component B: Actual Environment Manager.
    Maintains verified vs unverified spacecraft environmental states independently.
    Integrates Pint scientific unit conversion with dimensional integrity checks.
    Evaluates telemetry freshness, detects contradictory readings, supports idempotency,
    and rejects invalid units. Missing parameters strictly remain UNKNOWN.
    """
    def __init__(self, stale_threshold_seconds: float = settings.TELEMETRY_STALE_THRESHOLD_SECONDS):
        self.stale_threshold_seconds = stale_threshold_seconds

    def validate_observation(
        self,
        obs_input: ObservationCreate,
        recent_history: Optional[List[EnvironmentalObservation]] = None
    ) -> EnvironmentalObservation:
        """Applies rigorous validation rules to an incoming observation."""
        now = datetime.now(timezone.utc)
        obs_timestamp = obs_input.timestamp or now
        if obs_timestamp.tzinfo is None:
            obs_timestamp = obs_timestamp.replace(tzinfo=timezone.utc)

        parameter_raw_upper = obs_input.parameter.strip().upper()
        parameter_upper = PARAMETER_ALIASES.get(parameter_raw_upper, parameter_raw_upper)
        unit_str = obs_input.unit.strip() if obs_input.unit else None

        # 0. Idempotency check: Reject/acknowledge duplicate deep-space packets
        if obs_input.idempotency_key and recent_history:
            for h in recent_history:
                if getattr(h, "idempotency_key", None) == obs_input.idempotency_key:
                    logger.info(f"Duplicate observation recognized via idempotency key: {obs_input.idempotency_key}")
                    dup_obs = h.model_copy()
                    dup_obs.metadata["idempotent_duplicate"] = True
                    return dup_obs

        # 1. Scientific Unit Validation & Dimensional Conversion via Pint
        canonical_val = obs_input.value
        canonical_u = unit_str
        is_numeric = isinstance(obs_input.value, (int, float))

        # Check if parameter has strict dimensional physics requirements
        if is_numeric and parameter_upper in ("CABIN_PRESSURE", "CO2_CONCENTRATION", "CO2", "RADIATION", "GRAVITY", "COMMUNICATION_DELAY", "TEMPERATURE"):
            conv_result: UnitConversionResult = validate_and_convert_observation(
                parameter_upper,
                float(obs_input.value),
                unit_str,
                radiation_weighting_factor=obs_input.radiation_weighting_factor
            )
            if not conv_result.is_valid:
                logger.warning(f"Scientific unit validation failed for {parameter_upper}: {conv_result.error_message}")
                return EnvironmentalObservation(
                    parameter=parameter_upper,
                    value=obs_input.value,
                    unit=unit_str,
                    raw_value=obs_input.value,
                    raw_unit=unit_str,
                    idempotency_key=obs_input.idempotency_key,
                    timestamp=obs_timestamp,
                    source=obs_input.source,
                    quality_status=QualityStatus.INVALID_UNIT,
                    validation_status=False,
                    metadata={"error": conv_result.error_message, "raw_parameter": obs_input.parameter, **obs_input.metadata}
                )
            # If conversion succeeded, adopt canonical value and unit
            canonical_val = conv_result.canonical_value
            canonical_u = conv_result.canonical_unit
        elif parameter_upper in VALID_UNITS and unit_str:
            allowed = VALID_UNITS[parameter_upper]
            if unit_str not in allowed and unit_str.lower() not in [u.lower() for u in allowed]:
                logger.warning(f"Invalid unit {unit_str} for parameter {parameter_upper}")
                return EnvironmentalObservation(
                    parameter=parameter_upper,
                    value=obs_input.value,
                    unit=unit_str,
                    raw_value=obs_input.value,
                    raw_unit=unit_str,
                    idempotency_key=obs_input.idempotency_key,
                    timestamp=obs_timestamp,
                    source=obs_input.source,
                    quality_status=QualityStatus.INVALID_UNIT,
                    validation_status=False,
                    metadata={"error": f"Invalid unit '{unit_str}'. Allowed: {allowed}", "raw_parameter": obs_input.parameter, **obs_input.metadata}
                )

        # 2. Staleness check
        age_seconds = (now - obs_timestamp).total_seconds()
        if age_seconds > self.stale_threshold_seconds:
            logger.warning(f"Stale observation for {parameter_upper}: age={age_seconds}s")
            return EnvironmentalObservation(
                parameter=parameter_upper,
                value=canonical_val,
                unit=canonical_u,
                canonical_value=canonical_val if is_numeric else None,
                canonical_unit=canonical_u,
                raw_value=obs_input.value,
                raw_unit=unit_str,
                idempotency_key=obs_input.idempotency_key,
                timestamp=obs_timestamp,
                source=obs_input.source,
                quality_status=QualityStatus.STALE,
                validation_status=False,
                metadata={"warning": f"Observation is stale by {age_seconds:.1f}s", "raw_parameter": obs_input.parameter, **obs_input.metadata}
            )

        # 3. Contradictory observation check
        if recent_history:
            recent_same = [h for h in recent_history if h.parameter == parameter_upper and h.validation_status]
            if recent_same:
                latest = recent_same[0]
                delta_t = abs((obs_timestamp - latest.timestamp).total_seconds())
                latest_val = latest.canonical_value if latest.canonical_value is not None else latest.value
                # If reading arrives within 30 seconds but numeric value diverges dramatically (>80% drop or >4x ratio)
                if delta_t < 30.0 and isinstance(canonical_val, (int, float)) and isinstance(latest_val, (int, float)):
                    min_val = min(abs(canonical_val), abs(latest_val))
                    max_val = max(abs(canonical_val), abs(latest_val))
                    ratio = max_val / max(min_val, 0.001)
                    rel_change = abs(canonical_val - latest_val) / max(abs(latest_val), 0.1)
                    if ratio >= 4.0 or rel_change >= 0.85:
                        logger.warning(f"Contradictory reading detected for {parameter_upper}: {canonical_val} vs {latest_val}")
                        return EnvironmentalObservation(
                            parameter=parameter_upper,
                            value=canonical_val,
                            unit=canonical_u,
                            canonical_value=canonical_val,
                            canonical_unit=canonical_u,
                            raw_value=obs_input.value,
                            raw_unit=unit_str,
                            idempotency_key=obs_input.idempotency_key,
                            timestamp=obs_timestamp,
                            source=obs_input.source,
                            quality_status=QualityStatus.CONTRADICTORY,
                            validation_status=False,
                            metadata={
                                "error": "Contradictory to recent observation",
                                "raw_parameter": obs_input.parameter,
                                "previous_value": latest_val,
                                "previous_timestamp": latest.timestamp.isoformat(),
                                **obs_input.metadata
                            }
                        )

        # 4. Verified Observation
        return EnvironmentalObservation(
            parameter=parameter_upper,
            value=canonical_val,
            unit=canonical_u,
            canonical_value=canonical_val if is_numeric else None,
            canonical_unit=canonical_u,
            raw_value=obs_input.value,
            raw_unit=unit_str,
            idempotency_key=obs_input.idempotency_key,
            timestamp=obs_timestamp,
            source=obs_input.source,
            quality_status=QualityStatus.VERIFIED,
            validation_status=True,
            metadata={"raw_parameter": obs_input.parameter, **obs_input.metadata}
        )

    def evaluate_environment_state(
        self,
        current_env: EnvironmentStatus,
        recent_verified: List[EnvironmentalObservation],
        planned_profile: Optional[MissionProfile] = None
    ) -> Tuple[EnvironmentStatus, DataQualityContext]:
        """Synthesizes verified observations into current environmental state and quality metrics.
        Reconciles legacy alias telemetry streams into canonical parameters.
        Evaluates freshness and staleness exclusively on canonical parameters.
        Maps individual verified observations to their corresponding status fields.
        Validates canonical values against the selected mission profile's configured bounds.
        Missing values strictly remain UNKNOWN.
        """
        now = datetime.now(timezone.utc)
        env = current_env.model_copy(deep=True)

        # 1. Reconcile legacy and alias parameters into canonical representations
        reconciled_params: Dict[str, Any] = {}
        reconciled_timestamps: Dict[str, datetime] = {}

        # Reconcile timestamps first (latest timestamp per canonical parameter wins)
        for raw_k, ts in env.parameter_timestamps.items():
            canon_k = PARAMETER_ALIASES.get(raw_k.strip().upper(), raw_k.strip().upper())
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if canon_k not in reconciled_timestamps or ts > reconciled_timestamps[canon_k]:
                reconciled_timestamps[canon_k] = ts

        # Reconcile observed values
        for raw_k, val in env.observed_parameters.items():
            canon_k = PARAMETER_ALIASES.get(raw_k.strip().upper(), raw_k.strip().upper())
            ts = env.parameter_timestamps.get(raw_k)
            if ts and ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if canon_k not in reconciled_params or (ts and ts == reconciled_timestamps.get(canon_k)):
                reconciled_params[canon_k] = val

        env.observed_parameters = reconciled_params
        env.parameter_timestamps = reconciled_timestamps

        # 2. Update with newest verified incoming observations (superseding older representations)
        latest_telemetry_ts = None
        for canon_k, ts in env.parameter_timestamps.items():
            if latest_telemetry_ts is None or ts > latest_telemetry_ts:
                latest_telemetry_ts = ts

        for obs in recent_verified:
            if obs.validation_status and obs.quality_status == QualityStatus.VERIFIED:
                param = PARAMETER_ALIASES.get(obs.parameter.strip().upper(), obs.parameter.strip().upper())
                obs_ts = obs.timestamp
                if obs_ts.tzinfo is None:
                    obs_ts = obs_ts.replace(tzinfo=timezone.utc)

                existing_ts = env.parameter_timestamps.get(param)
                if existing_ts is None or obs_ts >= existing_ts:
                    env.observed_parameters[param] = obs.canonical_value if obs.canonical_value is not None else obs.value
                    env.parameter_timestamps[param] = obs_ts

                if latest_telemetry_ts is None or obs_ts > latest_telemetry_ts:
                    latest_telemetry_ts = obs_ts

                # Update individual categorical statuses independently
                if param == "CABIN_PRESSURE":
                    try:
                        val = float(obs.value)
                        # Check configured nominal bounds from selected mission profile
                        bounds = None
                        if planned_profile and planned_profile.nominal_bounds:
                            bounds = (
                                planned_profile.nominal_bounds.get("cabin_pressure_kpa")
                                or planned_profile.nominal_bounds.get("cabin_pressure")
                            )

                        p_min = getattr(bounds, "min", None) if not isinstance(bounds, dict) else bounds.get("min")
                        p_max = getattr(bounds, "max", None) if not isinstance(bounds, dict) else bounds.get("max")

                        if p_min is not None and p_max is not None:
                            p_min = float(p_min)
                            p_max = float(p_max)
                            if p_min <= val <= p_max:
                                env.cabin_pressure_status = "NOMINAL"
                            elif val < p_min:
                                if val < 50.0 or val < (p_min * 0.75):
                                    env.cabin_pressure_status = "CRITICAL_LOW"
                                else:
                                    env.cabin_pressure_status = "DEGRADED_LOW"
                            else:
                                if val > (p_max * 1.25):
                                    env.cabin_pressure_status = "CRITICAL_HIGH"
                                else:
                                    env.cabin_pressure_status = "DEGRADED_HIGH"
                        else:
                            # Standard reference bounds fallback
                            if val < 50.0:
                                env.cabin_pressure_status = "CRITICAL_LOW"
                            elif val < 68.0:
                                env.cabin_pressure_status = "DEGRADED_LOW"
                            elif val > 115.0:
                                env.cabin_pressure_status = "CRITICAL_HIGH"
                            elif val > 105.0:
                                env.cabin_pressure_status = "DEGRADED_HIGH"
                            else:
                                env.cabin_pressure_status = "NOMINAL"
                    except (ValueError, TypeError):
                        env.cabin_pressure_status = str(obs.value)
                elif param == "CO2_CONCENTRATION":
                    try:
                        val = float(obs.value)
                        co2_bounds = None
                        if planned_profile and planned_profile.nominal_bounds:
                            co2_bounds = (
                                planned_profile.nominal_bounds.get("co2_partial_pressure_mmhg")
                                or planned_profile.nominal_bounds.get("co2_concentration")
                            )
                        co2_max = getattr(co2_bounds, "max", None) if not isinstance(co2_bounds, dict) else co2_bounds.get("max")
                        if co2_max is not None:
                            co2_max = float(co2_max)
                            if val <= 20.0:
                                # Partial pressure mmHg
                                if val <= co2_max:
                                    env.co2_status = "NOMINAL"
                                elif val > co2_max * 1.8:
                                    env.co2_status = "CRITICAL_HIGH"
                                else:
                                    env.co2_status = "ELEVATED_WARNING"
                            else:
                                # ppm
                                ppm_max = co2_max / 760.0 * 1e6
                                if val <= ppm_max:
                                    env.co2_status = "NOMINAL"
                                elif val > ppm_max * 1.8:
                                    env.co2_status = "CRITICAL_HIGH"
                                else:
                                    env.co2_status = "ELEVATED_WARNING"
                        else:
                            if val > 5.0 and val <= 100.0:
                                env.co2_status = "CRITICAL_HIGH"
                            elif val > 3.0 and val <= 100.0:
                                env.co2_status = "ELEVATED_WARNING"
                            elif val > 6500.0:
                                env.co2_status = "CRITICAL_HIGH"
                            elif val > 4000.0:
                                env.co2_status = "ELEVATED_WARNING"
                            else:
                                env.co2_status = "NOMINAL"
                    except (ValueError, TypeError):
                        env.co2_status = str(obs.value)
                elif param == "RADIATION":
                    try:
                        val = float(obs.value)
                        rad_bounds = None
                        if planned_profile and planned_profile.nominal_bounds:
                            rad_bounds = (
                                planned_profile.nominal_bounds.get("radiation_msv_per_day")
                                or planned_profile.nominal_bounds.get("radiation")
                            )
                        rad_max = getattr(rad_bounds, "max", None) if not isinstance(rad_bounds, dict) else rad_bounds.get("max")
                        if rad_max is not None:
                            rad_max = float(rad_max)
                            if val <= rad_max:
                                env.radiation_status = "NOMINAL"
                            elif val > max(rad_max * 3.5, 3.5):
                                env.radiation_status = "CRITICAL_ELEVATED"
                            else:
                                env.radiation_status = "MODERATE_ELEVATED"
                        else:
                            if val > 3.5:
                                env.radiation_status = "CRITICAL_ELEVATED"
                            elif val > 1.5:
                                env.radiation_status = "MODERATE_ELEVATED"
                            else:
                                env.radiation_status = "NOMINAL"
                    except (ValueError, TypeError):
                        env.radiation_status = str(obs.value)
                elif param == "LIFE_SUPPORT":
                    env.life_support_status = str(obs.value).upper()
                elif param == "HABITAT_INTEGRITY":
                    env.habitat_status = str(obs.value).upper()

        # Check staleness exclusively on canonical observed parameters AFTER updates
        stale_params = []
        for param, ts in env.parameter_timestamps.items():
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if (now - ts).total_seconds() > self.stale_threshold_seconds:
                stale_params.append(param)

        # Identify missing / unknown parameters
        required_params = ["CABIN_PRESSURE", "CO2_CONCENTRATION", "RADIATION", "LIFE_SUPPORT", "HABITAT_INTEGRITY"]
        unknown_params = []
        for p in required_params:
            if p not in env.observed_parameters:
                unknown_params.append(p.lower() + "_status")
            elif p == "CABIN_PRESSURE" and env.cabin_pressure_status == "UNKNOWN":
                unknown_params.append("cabin_pressure_status")
            elif p == "CO2_CONCENTRATION" and env.co2_status == "UNKNOWN":
                unknown_params.append("co2_concentration_status")
            elif p == "RADIATION" and env.radiation_status == "UNKNOWN":
                unknown_params.append("radiation_status")
            elif p == "LIFE_SUPPORT" and env.life_support_status == "UNKNOWN":
                unknown_params.append("life_support_status")
            elif p == "HABITAT_INTEGRITY" and env.habitat_status == "UNKNOWN":
                unknown_params.append("habitat_integrity_status")

        # Telemetry completeness: NONE, PARTIAL, or COMPLETE
        if len(unknown_params) == len(required_params):
            completeness = "NONE"
        elif len(unknown_params) > 0:
            completeness = "PARTIAL"
        else:
            completeness = "COMPLETE"

        # Telemetry freshness: UNKNOWN, STALE, or FRESH
        if not env.parameter_timestamps:
            freshness = "UNKNOWN"
        elif stale_params:
            freshness = "STALE"
        else:
            freshness = "FRESH"

        # Validation quality of incoming sensor feeds: UNKNOWN, UNVERIFIED, or VERIFIED
        if not env.observed_parameters:
            validation_qual = QualityStatus.UNKNOWN
        elif any(not obs.validation_status for obs in recent_verified):
            validation_qual = QualityStatus.UNVERIFIED
        else:
            validation_qual = QualityStatus.VERIFIED

        # Determine overall quality status:
        # - UNKNOWN when all required parameters are unmeasured.
        # - STALE when any measured parameter has exceeded staleness threshold.
        # - PARTIAL when only a subset of required parameters is measured and fresh.
        # - VERIFIED only when all required parameters are observed, valid, and fresh.
        if completeness == "NONE":
            overall_quality = QualityStatus.UNKNOWN
        elif stale_params:
            overall_quality = QualityStatus.STALE
        elif completeness == "PARTIAL":
            overall_quality = QualityStatus.PARTIAL
        else:
            overall_quality = QualityStatus.VERIFIED

        data_quality = DataQualityContext(
            overall_status=overall_quality,
            validation_quality=validation_qual,
            telemetry_completeness=completeness,
            telemetry_freshness=freshness,
            unknown_parameters=unknown_params,
            stale_parameters=stale_params,
            contradictory_parameters=[],
            last_telemetry_timestamp=latest_telemetry_ts
        )

        return env, data_quality

