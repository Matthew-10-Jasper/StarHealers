from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseModuleIntegrationAdapter(ABC):
    """Abstract interface defining the integration contract for downstream Starhealers modules."""

    @property
    @abstractmethod
    def target_module_id(self) -> str:
        """Identifier for target module (e.g. MODULE_1_ASTRONAUT_HEALTH)."""
        pass

    @abstractmethod
    def deliver_mission_context(self, context_contract: Dict[str, Any]) -> Dict[str, Any]:
        """Transfers the latest validated Module 4 Mission Context to the downstream consumer."""
        pass

    @abstractmethod
    def query_delivery_status(self) -> Dict[str, Any]:
        """Checks the handshake status and telemetry sync of the integration adapter."""
        pass

