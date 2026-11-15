from enum import Enum

class SimulationStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class EngineType(str, Enum):
    RADIATION = "RADIATION"
    CO2 = "CO2"
    SLEEP = "SLEEP"
    COMBINED = "COMBINED"

class HazardSeverity(str, Enum):
    NOMINAL = "NOMINAL"
    ELEVATED = "ELEVATED"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class RadiationEnvironment(str, Enum):
    GCR_DEEP_SPACE = "GCR_DEEP_SPACE"
    LEO_NOMINAL = "LEO_NOMINAL"
    LUNAR_SURFACE = "LUNAR_SURFACE"
    SOLAR_PARTICLE_EVENT = "SOLAR_PARTICLE_EVENT"

class ProvenanceType(str, Enum):
    SIMULATED = "SIMULATED"
    CALIBRATED = "CALIBRATED"
    BENCHMARK = "BENCHMARK"

