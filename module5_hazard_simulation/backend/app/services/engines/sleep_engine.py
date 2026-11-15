import math
from typing import List, Dict, Any, Tuple
from app.schemas.enums import HazardSeverity, ProvenanceType
from app.schemas.sleep import SleepInput, SleepStepOutput, SleepSimulationResult

class AstronautSleepEngine:
    """Astronaut Sleep Debt and Recovery Simulation Engine.
    Models daily sleep deficit accumulation and non-linear recovery dynamics.
    Supports mission-day scheduling and acute operational disruption events.
    """

    WARNING_THRESHOLD_DEBT_HOURS: float = 8.0
    CRITICAL_THRESHOLD_DEBT_HOURS: float = 16.0
    ELEVATED_THRESHOLD_DEBT_HOURS: float = 4.0

    def __init__(self, params: SleepInput):
        self.params = params

    def get_actual_sleep_for_day(self, day: int) -> Tuple[float, bool]:
        """Determines the actual sleep duration for a given mission day (1-indexed)."""
        # 1. Custom schedule override if provided
        if self.params.custom_daily_schedule and len(self.params.custom_daily_schedule) >= day:
            return self.params.custom_daily_schedule[day - 1], False

        # 2. Check disruption window
        is_disrupted = False
        if self.params.disruption_active:
            start = self.params.disruption_start_day
            end = start + self.params.disruption_duration_days - 1
            if start <= day <= end:
                is_disrupted = True
                return self.params.disrupted_sleep_hours, is_disrupted

        return self.params.nominal_sleep_hours, is_disrupted

    def evaluate_day_step(
        self,
        day: int,
        step_index: int,
        prev_cumulative_debt: float
    ) -> SleepStepOutput:
        """Evaluates sleep deficit and recovery for a given mission day."""
        required = self.params.baseline_sleep_hours
        actual, is_disrupted = self.get_actual_sleep_for_day(day)

        # Deficit calculation
        if actual < required:
            daily_deficit = required - actual
            daily_recovery = 0.0
        else:
            daily_deficit = 0.0
            surplus = actual - required
            daily_recovery = surplus * self.params.recovery_efficiency

        # Cumulative debt: debt increases with deficit, decreases with recovery
        new_debt = max(0.0, prev_cumulative_debt + daily_deficit - daily_recovery)

        # Severity classification
        if new_debt >= self.CRITICAL_THRESHOLD_DEBT_HOURS:
            severity = HazardSeverity.CRITICAL
        elif new_debt >= self.WARNING_THRESHOLD_DEBT_HOURS:
            severity = HazardSeverity.WARNING
        elif new_debt >= self.ELEVATED_THRESHOLD_DEBT_HOURS:
            severity = HazardSeverity.ELEVATED
        else:
            severity = HazardSeverity.NOMINAL

        return SleepStepOutput(
            step_index=step_index,
            mission_day=day,
            required_sleep_hours=round(required, 2),
            actual_sleep_hours=round(actual, 2),
            daily_deficit_hours=round(daily_deficit, 2),
            daily_recovery_hours=round(daily_recovery, 2),
            cumulative_debt_hours=round(new_debt, 2),
            disruption_active=is_disrupted,
            severity=severity,
            provenance=ProvenanceType.SIMULATED,
            metadata={
                "recovery_efficiency": self.params.recovery_efficiency,
                "surplus_hours": round(max(0.0, actual - required), 2)
            }
        )

    def evaluate_at_hour(
        self,
        t_hour: float,
        step_index: int,
        prev_cumulative_debt: float
    ) -> SleepStepOutput:
        """Evaluates sleep step aligned with a continuous mission hour timeline (t_hour)."""
        # Day index: 1-indexed (Hour 0 to 24 is Day 1)
        day = max(1, int(t_hour // 24) + 1)
        step = self.evaluate_day_step(day, step_index, prev_cumulative_debt)
        return step

    def run_full_simulation(self, scenario_id: str = None) -> SleepSimulationResult:
        """Runs the entire time-series sleep debt simulation for mission_days."""
        timesteps: List[SleepStepOutput] = []
        debt = self.params.initial_sleep_debt_hours
        peak_debt = debt
        total_deficit = 0.0
        total_recovery = 0.0
        days_warning = 0
        days_critical = 0

        for d in range(1, self.params.mission_days + 1):
            step_out = self.evaluate_day_step(d, d - 1, debt)
            debt = step_out.cumulative_debt_hours
            timesteps.append(step_out)

            total_deficit += step_out.daily_deficit_hours
            total_recovery += step_out.daily_recovery_hours
            if debt > peak_debt:
                peak_debt = debt
            if step_out.cumulative_debt_hours >= self.WARNING_THRESHOLD_DEBT_HOURS:
                days_warning += 1
            if step_out.cumulative_debt_hours >= self.CRITICAL_THRESHOLD_DEBT_HOURS:
                days_critical += 1

        return SleepSimulationResult(
            engine="SLEEP",
            scenario_id=scenario_id,
            parameters=self.params,
            timesteps=timesteps,
            peak_sleep_debt_hours=round(peak_debt, 2),
            final_sleep_debt_hours=round(debt, 2),
            total_deficit_accumulated_hours=round(total_deficit, 2),
            total_recovery_hours=round(total_recovery, 2),
            days_above_warning=days_warning,
            days_above_critical=days_critical,
            provenance=ProvenanceType.SIMULATED
        )

