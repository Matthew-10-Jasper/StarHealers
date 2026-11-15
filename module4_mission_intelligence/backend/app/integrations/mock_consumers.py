import logging
from typing import Dict, Any, List
from app.integrations.adapters import BaseModuleIntegrationAdapter

logger = logging.getLogger("MockConsumerIntegrations")

class MockModule1HealthAdapter(BaseModuleIntegrationAdapter):
    """MOCK ONLY: Demonstrates Module 1 (Astronaut Health Monitoring) receiving mission context."""
    target_module_id = "MODULE_1_ASTRONAUT_HEALTH_MONITORING"

    def __init__(self):
        self.received_contexts: List[Dict[str, Any]] = []

    def deliver_mission_context(self, context_contract: Dict[str, Any]) -> Dict[str, Any]:
        self.received_contexts.append(context_contract)
        # Module 1 extracts gravity and operational state to calibrate physiological baselines
        gravity = context_contract.get("gravity_environment")
        state = context_contract.get("operational_state")
        return {
            "status": "ACCEPTED",
            "mock": True,
            "target": self.target_module_id,
            "calibrated_gravity": gravity,
            "operational_state": state,
            "context_version": context_contract.get("context_version")
        }

    def query_delivery_status(self) -> Dict[str, Any]:
        return {
            "target": self.target_module_id,
            "connected": True,
            "mode": "MOCK_DEVELOPMENT",
            "received_count": len(self.received_contexts)
        }

class MockModule3TriageAdapter(BaseModuleIntegrationAdapter):
    """MOCK ONLY: Demonstrates Module 3 (Clinical Triage Engine) receiving environmental evidence."""
    target_module_id = "MODULE_3_CLINICAL_TRIAGE_ENGINE"

    def __init__(self):
        self.received_contexts: List[Dict[str, Any]] = []

    def deliver_mission_context(self, context_contract: Dict[str, Any]) -> Dict[str, Any]:
        self.received_contexts.append(context_contract)
        # Module 3 uses environmental status (CO2, pressure, radiation) to contextualize symptoms
        env = context_contract.get("environment", {})
        comm = context_contract.get("communication", {})
        return {
            "status": "ACCEPTED",
            "mock": True,
            "target": self.target_module_id,
            "triage_environmental_modifiers": {
                "hypoxia_risk": env.get("cabin_pressure_status") != "NOMINAL",
                "hypercapnia_risk": env.get("co2_status") != "NOMINAL",
                "acute_radiation_risk": env.get("radiation_status") != "NOMINAL",
                "ground_support_delay_s": comm.get("expected_delay_seconds", 0)
            }
        }

    def query_delivery_status(self) -> Dict[str, Any]:
        return {
            "target": self.target_module_id,
            "connected": True,
            "mode": "MOCK_DEVELOPMENT",
            "received_count": len(self.received_contexts)
        }

class MockModule5SimulationAdapter(BaseModuleIntegrationAdapter):
    """MOCK ONLY: Demonstrates Module 5 (Radiation, CO2 & Sleep Simulation) sync."""
    target_module_id = "MODULE_5_RADIATION_CO2_SLEEP_SIMULATOR"

    def __init__(self):
        self.received_contexts: List[Dict[str, Any]] = []

    def deliver_mission_context(self, context_contract: Dict[str, Any]) -> Dict[str, Any]:
        self.received_contexts.append(context_contract)
        return {
            "status": "ACCEPTED",
            "mock": True,
            "target": self.target_module_id,
            "sync_phase": context_contract.get("actual_mission_phase"),
            "context_version": context_contract.get("context_version")
        }

    def query_delivery_status(self) -> Dict[str, Any]:
        return {
            "target": self.target_module_id,
            "connected": True,
            "mode": "MOCK_DEVELOPMENT",
            "received_count": len(self.received_contexts)
        }

