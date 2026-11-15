import math
import numpy as np
from typing import List, Dict, Any, Tuple
from app.schemas.enums import HazardSeverity, ProvenanceType
from app.schemas.radiation import RadiationInput, RadiationStepOutput, RadiationSimulationResult

class SpaceRadiationEngine:
    """Space Radiation Exposure Simulation Engine.
    Models Galactic Cosmic Ray (GCR) background and Solar Particle Events (SPE).
    Applies configurable physical shielding attenuation.
    Calculates time-dependent dose rate and cumulative ionizing radiation exposure.
    """

    WARNING_THRESHOLD_MSV_DAY: float = 5.0
    CRITICAL_THRESHOLD_MSV_DAY: float = 20.0
    ELEVATED_THRESHOLD_MSV_DAY: float = 2.5

    def __init__(self, params: RadiationInput):
        self.params = params

    def evaluate_step(
        self,
        t_hour: float,
        step_index: int,
        prev_cumulative_msv: float = 0.0
    ) -> RadiationStepOutput:
        """Evaluates radiation metrics for a single simulation timestep."""
        dt = self.params.timestep_hours
        base_rate = self.params.initial_dose_rate_msv_day  # in mSv/day

        # Model SPE contribution if active
        spe_intensity = 0.0
        spe_active_at_t = False
        if self.params.spe_active:
            t_start = self.params.spe_start_hour
            t_dur = self.params.spe_duration_hours
            if t_start <= t_hour <= (t_start + t_dur):
                spe_active_at_t = True
                delta_t = t_hour - t_start
                if self.params.spe_profile_type == "LOGNORMAL":
                    # Lognormal asymmetric rise and long exponential decay profile
                    t_peak = t_dur * 0.25
                    sigma = 0.6
                    if delta_t > 0:
                        # Scaled lognormal density
                        scaled = (1.0 / (delta_t * sigma * math.sqrt(2 * math.pi))) * math.exp(
                            -((math.log(delta_t) - math.log(t_peak)) ** 2) / (2 * sigma ** 2)
                        )
                        max_scale = (1.0 / (t_peak * sigma * math.sqrt(2 * math.pi)))
                        norm_factor = scaled / max_scale if max_scale > 0 else 1.0
                        spe_intensity = self.params.spe_peak_intensity_msv_day * norm_factor
                elif self.params.spe_profile_type == "WEIBULL":
                    k = 2.0
                    lam = t_dur * 0.35
                    norm_t = delta_t / lam
                    spe_intensity = self.params.spe_peak_intensity_msv_day * (k / lam) * (norm_t ** (k - 1)) * math.exp(-(norm_t ** k))
                else:
                    # Constant step pulse
                    spe_intensity = self.params.spe_peak_intensity_msv_day

        incident_rate = max(0.0, base_rate + spe_intensity)
        # Apply shielding attenuation factor: fraction absorbed = incident * (1 - shielding)
        shielding = min(0.99, max(0.0, self.params.shielding_factor))
        absorbed_rate = incident_rate * (1.0 - shielding)

        # Cumulative dose increment: dose rate (mSv/day) * (elapsed dt hours / 24 hours/day)
        # At t=0 (initial state before mission time elapses), 0 elapsed time has passed.
        # Exactly 1 interval dt has elapsed for step_index >= 1 (or t_hour > 0).
        if step_index == 0 or t_hour == 0.0:
            dose_increment_msv = 0.0
        else:
            dose_increment_msv = absorbed_rate * (dt / 24.0)

        cumulative_dose = prev_cumulative_msv + dose_increment_msv

        # Determine hazard severity
        if absorbed_rate >= self.CRITICAL_THRESHOLD_MSV_DAY:
            severity = HazardSeverity.CRITICAL
        elif absorbed_rate >= self.WARNING_THRESHOLD_MSV_DAY:
            severity = HazardSeverity.WARNING
        elif absorbed_rate >= self.ELEVATED_THRESHOLD_MSV_DAY:
            severity = HazardSeverity.ELEVATED
        else:
            severity = HazardSeverity.NOMINAL

        return RadiationStepOutput(
            step_index=step_index,
            simulation_time_hours=round(t_hour, 2),
            mission_day=round(t_hour / 24.0, 3),
            incident_dose_rate_msv_day=round(incident_rate, 4),
            absorbed_dose_rate_msv_day=round(absorbed_rate, 4),
            cumulative_dose_msv=round(cumulative_dose, 4),
            shielding_factor=round(shielding, 3),
            spe_active=spe_active_at_t,
            severity=severity,
            provenance=ProvenanceType.SIMULATED,
            metadata={
                "base_dose_rate": base_rate,
                "spe_contribution": round(spe_intensity, 4),
                "environment": self.params.environment.value
            }
        )

    def run_full_simulation(self, scenario_id: str = None) -> RadiationSimulationResult:
        """Runs the entire time-series trajectory from t=0 to mission_duration_hours."""
        timesteps: List[RadiationStepOutput] = []
        dt = self.params.timestep_hours
        total_hours = self.params.mission_duration_hours
        
        num_steps = int(math.ceil(total_hours / dt)) + 1
        cum_dose = 0.0
        time_warning = 0.0
        time_critical = 0.0
        max_dose_rate = 0.0

        for i in range(num_steps):
            t = min(i * dt, total_hours)
            step_out = self.evaluate_step(t, i, cum_dose)
            cum_dose = step_out.cumulative_dose_msv
            timesteps.append(step_out)

            if step_out.absorbed_dose_rate_msv_day > max_dose_rate:
                max_dose_rate = step_out.absorbed_dose_rate_msv_day
            if i > 0:
                if step_out.severity == HazardSeverity.WARNING:
                    time_warning += dt
                elif step_out.severity == HazardSeverity.CRITICAL:
                    time_critical += dt

        return RadiationSimulationResult(
            engine="RADIATION",
            scenario_id=scenario_id,
            parameters=self.params,
            timesteps=timesteps,
            final_cumulative_dose_msv=round(cum_dose, 4),
            max_dose_rate_msv_day=round(max_dose_rate, 4),
            time_above_warning_hours=round(time_warning, 2),
            time_above_critical_hours=round(time_critical, 2),
            provenance=ProvenanceType.SIMULATED
        )

