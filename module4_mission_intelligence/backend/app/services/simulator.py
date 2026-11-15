import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.schemas.enums import DataSource, CommStatus, GravityEnvironment, OperationalState
from app.schemas.observation import ObservationCreate

class MissionTelemetrySimulator:
    """Development Telemetry Simulator.
    Generates synthetic spacecraft sensor telemetry and scenario triggers for testing.
    All outputs are explicitly labeled DataSource.SIMULATED.
    """
    def __init__(self):
        pass

    def generate_nominal_telemetry_stream(self, destination: str = "MARS") -> List[ObservationCreate]:
        """Generates realistic nominal environmental sensor readings."""
        now = datetime.now(timezone.utc)
        
        # Determine nominal ranges based on vehicle / destination
        if destination == "LOW_EARTH_ORBIT":
            pressure = round(random.uniform(100.8, 101.6), 2)
            co2 = round(random.uniform(1.2, 2.4), 2)
            radiation = round(random.uniform(0.2, 0.5), 3)
            o2 = round(random.uniform(20.8, 21.4), 1)
        elif destination == "MOON":
            pressure = round(random.uniform(56.0, 58.0), 2)
            co2 = round(random.uniform(1.0, 2.0), 2)
            radiation = round(random.uniform(0.7, 1.2), 3)
            o2 = round(random.uniform(29.5, 31.0), 1)
        else: # MARS
            pressure = round(random.uniform(69.8, 70.8), 2)
            co2 = round(random.uniform(0.8, 1.6), 2)
            radiation = round(random.uniform(1.4, 2.1), 3)
            o2 = round(random.uniform(26.0, 27.2), 1)

        return [
            ObservationCreate(
                parameter="CABIN_PRESSURE",
                value=pressure,
                unit="kPa",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"sensor_id": "PT-CABIN-01A", "telemetry_mode": "SIMULATED"}
            ),
            ObservationCreate(
                parameter="CO2_CONCENTRATION",
                value=co2,
                unit="mmHg",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"sensor_id": "CO2-CDRA-02B", "telemetry_mode": "SIMULATED"}
            ),
            ObservationCreate(
                parameter="O2_PERCENTAGE",
                value=o2,
                unit="%",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"sensor_id": "O2-PARTIAL-03", "telemetry_mode": "SIMULATED"}
            ),
            ObservationCreate(
                parameter="RADIATION",
                value=radiation,
                unit="mSv/day",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"sensor_id": "RAD-LID-DOSIMETER", "telemetry_mode": "SIMULATED"}
            ),
            ObservationCreate(
                parameter="LIFE_SUPPORT",
                value="NOMINAL",
                unit="status",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"subsystem": "ECLSS", "telemetry_mode": "SIMULATED"}
            ),
            ObservationCreate(
                parameter="HABITAT_INTEGRITY",
                value="NOMINAL",
                unit="status",
                timestamp=now,
                source=DataSource.SIMULATED,
                metadata={"subsystem": "HULL_PRESSURE_MONITOR", "telemetry_mode": "SIMULATED"}
            )
        ]

    def generate_scenario_telemetry(self, scenario: str) -> List[ObservationCreate]:
        """Generates synthetic anomalous telemetry for testing specific failure modes."""
        now = datetime.now(timezone.utc)
        scenario_upper = scenario.upper()

        if "COMM_LOSS" in scenario_upper or "BLACKOUT" in scenario_upper:
            return [
                ObservationCreate(
                    parameter="COMMUNICATION",
                    value="BLACKOUT",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"reason": "RF High-Gain Gimbal Jam / Solar Conjunction", "telemetry_mode": "SIMULATED"}
                )
            ]
        elif "LIFE_SUPPORT" in scenario_upper or "ECLSS" in scenario_upper:
            return [
                ObservationCreate(
                    parameter="LIFE_SUPPORT",
                    value="DEGRADED",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"fault": "CDRA Carbon Dioxide Removal Scrubber Bed 2 Desorption Failure", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="CO2_CONCENTRATION",
                    value=4.6,
                    unit="mmHg",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"trend": "RISING", "telemetry_mode": "SIMULATED"}
                )
            ]
        elif "CABIN_DEPRESSURIZATION" in scenario_upper or "PRESSURE" in scenario_upper:
            return [
                ObservationCreate(
                    parameter="CABIN_PRESSURE",
                    value=48.2,
                    unit="kPa",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"trend": "RAPID_DECAY", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="HABITAT_INTEGRITY",
                    value="MINOR_LEAK",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"fault": "Forward airlock seal integrity compromised", "telemetry_mode": "SIMULATED"}
                )
            ]
        elif "RADIATION_SPIKE" in scenario_upper or "SPE" in scenario_upper:
            return [
                ObservationCreate(
                    parameter="RADIATION",
                    value=4.8,
                    unit="mSv/day",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"event": "Solar Particle Event Class X4.2 Inbound", "telemetry_mode": "SIMULATED"}
                )
            ]
        elif "RESTORE_NOMINAL" in scenario_upper:
            return [
                ObservationCreate(
                    parameter="CABIN_PRESSURE",
                    value=70.3,
                    unit="kPa",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "REPRESSURIZED_NOMINAL", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="CO2_CONCENTRATION",
                    value=1.1,
                    unit="mmHg",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "SCRUBBERS_NOMINAL", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="RADIATION",
                    value=1.5,
                    unit="mSv/day",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "BACKGROUND_NOMINAL", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="LIFE_SUPPORT",
                    value="NOMINAL",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "DUAL_LOOPS_OPERATIONAL", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="HABITAT_INTEGRITY",
                    value="NOMINAL",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "SEALS_NOMINAL", "telemetry_mode": "SIMULATED"}
                ),
                ObservationCreate(
                    parameter="COMMUNICATION",
                    value="NOMINAL",
                    unit="status",
                    timestamp=now,
                    source=DataSource.SIMULATED,
                    metadata={"status": "DSN_LINK_RESTORED", "telemetry_mode": "SIMULATED"}
                )
            ]
        return []

