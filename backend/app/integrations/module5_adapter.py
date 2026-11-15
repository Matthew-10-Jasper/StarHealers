from typing import List, Dict, Any, Optional
from app.modules.module5_hazard_simulation.services.scenario_manager import ScenarioManager
from app.modules.module5_hazard_simulation.services.engines.radiation_engine import SpaceRadiationEngine
from app.modules.module5_hazard_simulation.services.engines.co2_engine import SpacecraftCO2Engine
from app.modules.module5_hazard_simulation.services.engines.sleep_engine import AstronautSleepEngine

class Module5Adapter:
    """Adapter exposing Module 5 Hazard Simulation Engines without duplicating calculation logic."""

    def __init__(self):
        self.scenario_manager = ScenarioManager()

    def get_scenarios(self) -> List[Dict[str, Any]]:
        scenarios = self.scenario_manager.list_scenarios()
        return [s.model_dump() for s in scenarios]

    def run_radiation_simulation(self, total_duration_hours: float = 24.0, has_spe: bool = False) -> Dict[str, Any]:
        from app.modules.module5_hazard_simulation.schemas.radiation import RadiationInput
        input_params = RadiationInput(
            initial_dose_rate_msv_day=1.8,
            spe_active=has_spe
        )
        engine = SpaceRadiationEngine(input_params)
        res = engine.run_full_simulation()
        return res.model_dump()

    def run_co2_simulation(self, total_duration_hours: float = 24.0, scrubber_active: bool = True) -> Dict[str, Any]:
        from app.modules.module5_hazard_simulation.schemas.co2 import CO2Input
        input_params = CO2Input(
            cabin_volume_m3=150.0,
            failure_active=not scrubber_active
        )
        engine = SpacecraftCO2Engine(input_params)
        res = engine.run_full_simulation()
        return res.model_dump()

    def run_sleep_simulation(self, total_duration_hours: float = 24.0, daily_sleep_hours: float = 6.0) -> Dict[str, Any]:
        from app.modules.module5_hazard_simulation.schemas.sleep import SleepInput
        input_params = SleepInput(
            baseline_sleep_hours=8.0,
            nominal_sleep_hours=daily_sleep_hours
        )
        engine = AstronautSleepEngine(input_params)
        res = engine.run_full_simulation()
        return res.model_dump()

module5_adapter = Module5Adapter()
