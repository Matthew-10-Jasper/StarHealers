import json
from typing import Dict, List, Optional
from app.schemas.enums import RadiationEnvironment
from app.schemas.radiation import RadiationInput
from app.schemas.co2 import CO2Input
from app.schemas.sleep import SleepInput
from app.schemas.scenario import SimulationScenarioConfig

class ScenarioManager:
    """Manages predefined and custom space hazard simulation scenarios."""

    def __init__(self):
        self._scenarios: Dict[str, SimulationScenarioConfig] = {}
        self._load_predefined_scenarios()

    def _load_predefined_scenarios(self):
        """Loads canonical baseline and hazard scenarios into memory."""

        # 1. NORMAL_MISSION: Nominal baseline conditions across all environmental stressors
        normal = SimulationScenarioConfig(
            scenario_id="NORMAL_MISSION",
            scenario_name="Nominal Deep-Space Baseline",
            description="Baseline GCR radiation exposure, fully functional CDRA CO2 scrubbing, and regular sleep schedule.",
            radiation_params=RadiationInput(
                initial_dose_rate_msv_day=1.8,
                shielding_factor=0.20,
                spe_active=False
            ),
            co2_params=CO2Input(
                cabin_volume_m3=150.0,
                initial_co2_mmhg=1.0,
                crew_count=4,
                co2_generation_rate_per_crew_l_h=18.0,
                nominal_scrubber_capacity_l_h=80.0,
                baseline_removal_efficiency=1.0,
                failure_active=False
            ),
            sleep_params=SleepInput(
                baseline_sleep_hours=8.0,
                nominal_sleep_hours=7.5,
                initial_sleep_debt_hours=0.0,
                recovery_efficiency=0.75,
                mission_days=7,
                disruption_active=False
            ),
            mission_duration_hours=168.0,
            timestep_hours=1.0,
            metadata={"category": "BASELINE", "mission_type": "INTERPLANETARY"}
        )
        self._scenarios["NORMAL_MISSION"] = normal

        # 2. SOLAR_RADIATION_EVENT: Severe solar particle event (SPE)
        spe = SimulationScenarioConfig(
            scenario_id="SOLAR_RADIATION_EVENT",
            scenario_name="Solar Particle Event (SPE) Outburst",
            description="High-energy coronal mass ejection proton flux causing acute radiation spike at Hour 24 lasting 48 hours.",
            radiation_params=RadiationInput(
                initial_dose_rate_msv_day=1.8,
                shielding_factor=0.20,
                spe_active=True,
                spe_start_hour=24.0,
                spe_duration_hours=48.0,
                spe_peak_intensity_msv_day=35.0,
                spe_profile_type="LOGNORMAL",
                environment=RadiationEnvironment.SOLAR_PARTICLE_EVENT
            ),
            co2_params=CO2Input(
                cabin_volume_m3=150.0,
                initial_co2_mmhg=1.0,
                crew_count=4,
                failure_active=False
            ),
            sleep_params=SleepInput(
                baseline_sleep_hours=8.0,
                nominal_sleep_hours=7.5,
                mission_days=7,
                disruption_active=False
            ),
            mission_duration_hours=168.0,
            timestep_hours=1.0,
            metadata={"category": "RADIATION_HAZARD", "threat_level": "CRITICAL"}
        )
        self._scenarios["SOLAR_RADIATION_EVENT"] = spe

        # 3. CO2_REMOVAL_FAILURE: Environmental life-support scrubber degradation
        co2_fail = SimulationScenarioConfig(
            scenario_id="CO2_REMOVAL_FAILURE",
            scenario_name="ECLSS Carbon Dioxide Scrubber Failure",
            description="CDRA amine bed saturation and blower mechanical degradation at Hour 24 for 48 hours, causing dangerous CO2 accumulation.",
            radiation_params=RadiationInput(
                initial_dose_rate_msv_day=1.8,
                shielding_factor=0.20,
                spe_active=False
            ),
            co2_params=CO2Input(
                cabin_volume_m3=150.0,
                initial_co2_mmhg=1.0,
                crew_count=4,
                failure_active=True,
                failure_start_hour=24.0,
                failure_duration_hours=48.0,
                failure_removal_efficiency=0.10
            ),
            sleep_params=SleepInput(
                baseline_sleep_hours=8.0,
                nominal_sleep_hours=7.5,
                mission_days=7,
                disruption_active=False
            ),
            mission_duration_hours=168.0,
            timestep_hours=1.0,
            metadata={"category": "ATMOSPHERIC_HAZARD", "threat_level": "WARNING"}
        )
        self._scenarios["CO2_REMOVAL_FAILURE"] = co2_fail

        # 4. SLEEP_DISRUPTION: Chronic operational workload sleep debt
        sleep_disrupt = SimulationScenarioConfig(
            scenario_id="SLEEP_DISRUPTION",
            scenario_name="Extended Operational Sleep Disruption",
            description="Consecutive mission days with truncated sleep (3.5 hours/day) due to emergency drilling and telemetry anomaly triage.",
            radiation_params=RadiationInput(
                initial_dose_rate_msv_day=1.8,
                shielding_factor=0.20,
                spe_active=False
            ),
            co2_params=CO2Input(
                cabin_volume_m3=150.0,
                initial_co2_mmhg=1.0,
                crew_count=4,
                failure_active=False
            ),
            sleep_params=SleepInput(
                baseline_sleep_hours=8.0,
                nominal_sleep_hours=7.5,
                mission_days=14,
                disruption_active=True,
                disruption_start_day=3,
                disruption_duration_days=5,
                disrupted_sleep_hours=3.5,
                recovery_efficiency=0.75
            ),
            mission_duration_hours=336.0,
            timestep_hours=1.0,
            metadata={"category": "PHYSIOLOGICAL_HAZARD", "threat_level": "WARNING"}
        )
        self._scenarios["SLEEP_DISRUPTION"] = sleep_disrupt

        # 5. COMBINED_SPACE_HAZARD: Multi-stressor compound space mission hazard
        combined = SimulationScenarioConfig(
            scenario_id="COMBINED_SPACE_HAZARD",
            scenario_name="Compound Multi-Stressor Space Hazard",
            description="Concomitant solar proton event, CDRA scrubber degradation, and emergency-induced astronaut sleep disruption on a synchronized timeline.",
            radiation_params=RadiationInput(
                initial_dose_rate_msv_day=1.8,
                shielding_factor=0.25,
                spe_active=True,
                spe_start_hour=36.0,
                spe_duration_hours=60.0,
                spe_peak_intensity_msv_day=30.0,
                spe_profile_type="LOGNORMAL",
                environment=RadiationEnvironment.SOLAR_PARTICLE_EVENT
            ),
            co2_params=CO2Input(
                cabin_volume_m3=150.0,
                initial_co2_mmhg=1.0,
                crew_count=4,
                failure_active=True,
                failure_start_hour=30.0,
                failure_duration_hours=48.0,
                failure_removal_efficiency=0.15
            ),
            sleep_params=SleepInput(
                baseline_sleep_hours=8.0,
                nominal_sleep_hours=7.5,
                mission_days=14,
                disruption_active=True,
                disruption_start_day=2,
                disruption_duration_days=4,
                disrupted_sleep_hours=4.0,
                recovery_efficiency=0.70
            ),
            mission_duration_hours=336.0,
            timestep_hours=1.0,
            metadata={"category": "COMPOUND_HAZARD", "threat_level": "CRITICAL"}
        )
        self._scenarios["COMBINED_SPACE_HAZARD"] = combined

    def get_scenario(self, scenario_id: str) -> Optional[SimulationScenarioConfig]:
        """Retrieves a scenario by ID."""
        return self._scenarios.get(scenario_id)

    def list_scenarios(self) -> List[SimulationScenarioConfig]:
        """Lists all registered simulation scenarios."""
        return list(self._scenarios.values())

    def register_scenario(self, scenario: SimulationScenarioConfig) -> SimulationScenarioConfig:
        """Registers a new custom scenario configuration."""
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

