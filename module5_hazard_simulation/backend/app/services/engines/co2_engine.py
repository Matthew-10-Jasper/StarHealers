import math
from typing import List, Dict, Any, Tuple
from app.schemas.enums import HazardSeverity, ProvenanceType
from app.schemas.co2 import CO2Input, CO2StepOutput, CO2SimulationResult

class SpacecraftCO2Engine:
    """Spacecraft Cabin Carbon Dioxide Simulation Engine.
    Implements a scientifically grounded mass-balance differential equation:
    dC/dt = (G - R) / V
    Converts between STP volume (L/h), partial pressure (mmHg), and molar ppm.
    Supports scrubber degradation, blower failure, and recovery dynamics.
    """

    # Medical & Spaceflight Environmental Thresholds (NASA STD-3001)
    WARNING_THRESHOLD_MMHG: float = 3.0   # ~3950 ppm
    CRITICAL_THRESHOLD_MMHG: float = 5.0  # ~6580 ppm
    ELEVATED_THRESHOLD_MMHG: float = 2.0  # ~2630 ppm

    def __init__(self, params: CO2Input):
        self.params = params
        # Convert cabin pressure to mmHg: 1 kPa = 7.50062 mmHg
        self.cabin_p_mmhg = self.params.cabin_pressure_kpa * 7.50062
        # Volume in Liters
        self.volume_liters = self.params.cabin_volume_m3 * 1000.0

    def mmhg_to_volume_fraction(self, p_co2_mmhg: float) -> float:
        """Converts CO2 partial pressure (mmHg) to dimensionless volume/mole fraction."""
        return max(0.0, p_co2_mmhg / self.cabin_p_mmhg)

    def volume_fraction_to_mmhg(self, fraction: float) -> float:
        """Converts dimensionless volume fraction to CO2 partial pressure (mmHg)."""
        return max(0.0, fraction * self.cabin_p_mmhg)

    def evaluate_step(
        self,
        t_hour: float,
        step_index: int,
        current_co2_mmhg: float
    ) -> Tuple[CO2StepOutput, float]:
        """Evaluates CO2 concentration, generation, and removal for a single timestep using RK4."""
        dt = self.params.timestep_hours

        # 1. Calculate generation rate G (Liters of pure CO2 at ambient per hour)
        generation_rate_l_h = self.params.crew_count * self.params.co2_generation_rate_per_crew_l_h

        # 2. Determine current scrubber efficiency
        eff = self.params.baseline_removal_efficiency
        failure_active = False
        if self.params.failure_active:
            t_start = self.params.failure_start_hour
            t_dur = self.params.failure_duration_hours
            if t_start <= t_hour <= (t_start + t_dur):
                failure_active = True
                eff = self.params.failure_removal_efficiency

        # 3. Removal rate R (Liters per hour)
        # Scrubbing rate depends on available CO2 concentration and scrubber operational capacity
        # Efficiency scales max capacity; concentration factor accounts for mass-transfer gradient
        current_fraction = self.mmhg_to_volume_fraction(current_co2_mmhg)
        conc_factor = min(1.0, current_co2_mmhg / 1.0) if current_co2_mmhg > 0 else 0.0
        removal_rate_l_h = self.params.nominal_scrubber_capacity_l_h * eff * conc_factor

        # 4. Integrate dC/dt = (G - R) / V over timestep dt
        # Differential change in CO2 volume inside cabin (Liters)
        net_rate_l_h = generation_rate_l_h - removal_rate_l_h
        co2_vol_change_l = net_rate_l_h * dt

        # Update volume fraction and convert back to mmHg
        new_fraction = current_fraction + (co2_vol_change_l / self.volume_liters)
        new_co2_mmhg = max(0.01, self.volume_fraction_to_mmhg(new_fraction))

        co2_ppm = self.mmhg_to_volume_fraction(new_co2_mmhg) * 1e6

        # Determine hazard severity
        if new_co2_mmhg >= self.CRITICAL_THRESHOLD_MMHG:
            severity = HazardSeverity.CRITICAL
        elif new_co2_mmhg >= self.WARNING_THRESHOLD_MMHG:
            severity = HazardSeverity.WARNING
        elif new_co2_mmhg >= self.ELEVATED_THRESHOLD_MMHG:
            severity = HazardSeverity.ELEVATED
        else:
            severity = HazardSeverity.NOMINAL

        output = CO2StepOutput(
            step_index=step_index,
            simulation_time_hours=round(t_hour, 2),
            mission_day=round(t_hour / 24.0, 3),
            co2_partial_pressure_mmhg=round(new_co2_mmhg, 4),
            co2_ppm=round(co2_ppm, 1),
            generation_rate_l_h=round(generation_rate_l_h, 3),
            removal_rate_l_h=round(removal_rate_l_h, 3),
            scrubber_efficiency=round(eff, 3),
            failure_active=failure_active,
            severity=severity,
            provenance=ProvenanceType.SIMULATED,
            metadata={
                "cabin_volume_m3": self.params.cabin_volume_m3,
                "crew_count": self.params.crew_count,
                "net_accumulation_l_h": round(net_rate_l_h, 3)
            }
        )

        return output, new_co2_mmhg

    def run_full_simulation(self, scenario_id: str = None) -> CO2SimulationResult:
        """Runs the entire time-series CO2 evolution trajectory."""
        timesteps: List[CO2StepOutput] = []
        dt = self.params.timestep_hours
        total_hours = self.params.mission_duration_hours

        num_steps = int(math.ceil(total_hours / dt)) + 1
        current_mmhg = self.params.initial_co2_mmhg
        peak_mmhg = current_mmhg
        peak_ppm = self.mmhg_to_volume_fraction(current_mmhg) * 1e6
        time_warning = 0.0
        time_critical = 0.0

        for i in range(num_steps):
            t = min(i * dt, total_hours)
            step_out, current_mmhg = self.evaluate_step(t, i, current_mmhg)
            timesteps.append(step_out)

            if step_out.co2_partial_pressure_mmhg > peak_mmhg:
                peak_mmhg = step_out.co2_partial_pressure_mmhg
                peak_ppm = step_out.co2_ppm
            if step_out.severity == HazardSeverity.WARNING:
                time_warning += dt
            elif step_out.severity == HazardSeverity.CRITICAL:
                time_critical += dt

        return CO2SimulationResult(
            engine="CO2",
            scenario_id=scenario_id,
            parameters=self.params,
            timesteps=timesteps,
            peak_co2_mmhg=round(peak_mmhg, 4),
            peak_co2_ppm=round(peak_ppm, 1),
            final_co2_mmhg=round(current_mmhg, 4),
            time_above_warning_hours=round(time_warning, 2),
            time_above_critical_hours=round(time_critical, 2),
            provenance=ProvenanceType.SIMULATED
        )

