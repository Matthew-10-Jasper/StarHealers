import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from sqlalchemy.orm import Session

from app.modules.module5_hazard_simulation.schemas.enums import SimulationStatus, EngineType, HazardSeverity, ProvenanceType
from app.modules.module5_hazard_simulation.schemas.radiation import RadiationStepOutput, RadiationSimulationResult
from app.modules.module5_hazard_simulation.schemas.co2 import CO2StepOutput, CO2SimulationResult
from app.modules.module5_hazard_simulation.schemas.sleep import SleepStepOutput, SleepSimulationResult
from app.modules.module5_hazard_simulation.schemas.scenario import SimulationScenarioConfig
from app.modules.module5_hazard_simulation.schemas.session import (
    CombinedStepReading, SimulationEvent, SimulationSessionResponse,
    SimulationResultsResponse, Module4ExportPayload
)
from app.modules.module5_hazard_simulation.models.simulation import (
    SimulationSessionModel, SimulationReadingModel, SimulationEventModel, SimulationConfigurationModel
)
from app.modules.module5_hazard_simulation.services.engines.radiation_engine import SpaceRadiationEngine
from app.modules.module5_hazard_simulation.services.engines.co2_engine import SpacecraftCO2Engine
from app.modules.module5_hazard_simulation.services.engines.sleep_engine import AstronautSleepEngine

logger = logging.getLogger("SimulationController")

class SimulationSession:
    """Represents an active or persisted simulation run."""

    def __init__(
        self,
        session_id: str,
        scenario: SimulationScenarioConfig,
        engine_type: EngineType = EngineType.COMBINED,
        mission_duration_hours: float = 168.0,
        timestep_hours: float = 1.0
    ):
        self.session_id = session_id
        self.scenario = scenario
        self.engine_type = engine_type
        self.status = SimulationStatus.IDLE
        self.current_time_hours = 0.0
        self.total_duration_hours = mission_duration_hours
        self.timestep_hours = timestep_hours
        self.step_index = 0

        # State accumulators for engines
        self.current_cumulative_radiation_msv = 0.0
        self.current_co2_mmhg = scenario.co2_params.initial_co2_mmhg
        self.current_sleep_debt_hours = scenario.sleep_params.initial_sleep_debt_hours

        # Synchronize scenario duration and timestep with session parameters
        scenario.radiation_params.mission_duration_hours = self.total_duration_hours
        scenario.radiation_params.timestep_hours = self.timestep_hours
        scenario.co2_params.mission_duration_hours = self.total_duration_hours
        scenario.co2_params.timestep_hours = self.timestep_hours
        import math
        scenario.sleep_params.mission_days = max(1, int(math.ceil(self.total_duration_hours / 24.0)))

        # Instantiate engines
        self.radiation_engine = SpaceRadiationEngine(scenario.radiation_params)
        self.co2_engine = SpacecraftCO2Engine(scenario.co2_params)
        self.sleep_engine = AstronautSleepEngine(scenario.sleep_params)

        # History timeline and event logs
        self.timeline: List[CombinedStepReading] = []
        self.events: List[SimulationEvent] = []
        self.latest_reading: Optional[CombinedStepReading] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_response(self) -> SimulationSessionResponse:
        return SimulationSessionResponse(
            session_id=self.session_id,
            scenario_id=self.scenario.scenario_id,
            scenario_name=self.scenario.scenario_name,
            engine_type=self.engine_type,
            status=self.status,
            current_time_hours=round(self.current_time_hours, 2),
            total_duration_hours=round(self.total_duration_hours, 2),
            timestep_hours=round(self.timestep_hours, 2),
            latest_reading=self.latest_reading,
            events_count=len(self.events),
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def advance_step(self) -> CombinedStepReading:
        """Advances the simulation by one discrete timestep, coordinating all active engines."""
        dt = self.timestep_hours
        t = self.current_time_hours
        idx = self.step_index
        day = round(t / 24.0, 3)

        rad_out: Optional[RadiationStepOutput] = None
        co2_out: Optional[CO2StepOutput] = None
        sleep_out: Optional[SleepStepOutput] = None
        step_events: List[SimulationEvent] = []

        # 1. Evaluate Radiation Engine with fault isolation
        if self.engine_type in (EngineType.RADIATION, EngineType.COMBINED):
            try:
                rad_out = self.radiation_engine.evaluate_step(
                    t_hour=t,
                    step_index=idx,
                    prev_cumulative_msv=self.current_cumulative_radiation_msv
                )
                self.current_cumulative_radiation_msv = rad_out.cumulative_dose_msv
                if rad_out.severity in (HazardSeverity.WARNING, HazardSeverity.CRITICAL):
                    evt = SimulationEvent(
                        timestamp_hour=t,
                        event_type=f"RADIATION_{rad_out.severity.value}",
                        engine="RADIATION",
                        severity=rad_out.severity,
                        message=f"Radiation dose rate reached {rad_out.absorbed_dose_rate_msv_day:.2f} mSv/day ({rad_out.severity.value}).",
                        data={"dose_rate": rad_out.absorbed_dose_rate_msv_day, "cumulative": rad_out.cumulative_dose_msv}
                    )
                    step_events.append(evt)
                    self.events.append(evt)
            except Exception as e:
                logger.error(f"Radiation engine error at step {idx}: {e}")

        # 2. Evaluate CO2 Engine with fault isolation
        if self.engine_type in (EngineType.CO2, EngineType.COMBINED):
            try:
                co2_out, next_mmhg = self.co2_engine.evaluate_step(
                    t_hour=t,
                    step_index=idx,
                    current_co2_mmhg=self.current_co2_mmhg
                )
                self.current_co2_mmhg = next_mmhg
                if co2_out.severity in (HazardSeverity.WARNING, HazardSeverity.CRITICAL):
                    evt = SimulationEvent(
                        timestamp_hour=t,
                        event_type=f"CO2_{co2_out.severity.value}",
                        engine="CO2",
                        severity=co2_out.severity,
                        message=f"Cabin CO2 concentration reached {co2_out.co2_partial_pressure_mmhg:.2f} mmHg ({co2_out.co2_ppm:.0f} ppm).",
                        data={"co2_mmhg": co2_out.co2_partial_pressure_mmhg, "co2_ppm": co2_out.co2_ppm}
                    )
                    step_events.append(evt)
                    self.events.append(evt)
            except Exception as e:
                logger.error(f"CO2 engine error at step {idx}: {e}")

        # 3. Evaluate Sleep Debt Engine with fault isolation
        if self.engine_type in (EngineType.SLEEP, EngineType.COMBINED):
            try:
                sleep_out = self.sleep_engine.evaluate_at_hour(
                    t_hour=t,
                    step_index=idx,
                    prev_cumulative_debt=self.current_sleep_debt_hours
                )
                self.current_sleep_debt_hours = sleep_out.cumulative_debt_hours
                if sleep_out.severity in (HazardSeverity.WARNING, HazardSeverity.CRITICAL):
                    evt = SimulationEvent(
                        timestamp_hour=t,
                        event_type=f"SLEEP_DEBT_{sleep_out.severity.value}",
                        engine="SLEEP",
                        severity=sleep_out.severity,
                        message=f"Cumulative astronaut sleep debt reached {sleep_out.cumulative_debt_hours:.1f} hours ({sleep_out.severity.value}).",
                        data={"debt_hours": sleep_out.cumulative_debt_hours, "day": sleep_out.mission_day}
                    )
                    step_events.append(evt)
                    self.events.append(evt)
            except Exception as e:
                logger.error(f"Sleep engine error at step {idx}: {e}")

        # Overall compound hazard level determination
        severities = [
            s for s in [
                rad_out.severity if rad_out else None,
                co2_out.severity if co2_out else None,
                sleep_out.severity if sleep_out else None
            ] if s is not None
        ]
        if HazardSeverity.CRITICAL in severities:
            overall = HazardSeverity.CRITICAL
        elif HazardSeverity.WARNING in severities:
            overall = HazardSeverity.WARNING
        elif HazardSeverity.ELEVATED in severities:
            overall = HazardSeverity.ELEVATED
        else:
            overall = HazardSeverity.NOMINAL

        reading = CombinedStepReading(
            step_index=idx,
            simulation_time_hours=round(t, 2),
            mission_day=day,
            radiation=rad_out,
            co2=co2_out,
            sleep=sleep_out,
            overall_hazard_level=overall,
            active_events=step_events
        )

        self.latest_reading = reading
        self.timeline.append(reading)

        # Check if we just completed the final boundary timestep (t >= total_duration_hours)
        if t >= self.total_duration_hours:
            self.status = SimulationStatus.COMPLETED
        else:
            self.step_index += 1
            self.current_time_hours = round(min(self.total_duration_hours, self.current_time_hours + dt), 4)

        self.updated_at = datetime.now(timezone.utc)
        return reading

    def export_to_module4_format(self) -> Module4ExportPayload:
        """Translates current simulated reading into Module 4 EnvironmentalObservation payload."""
        obs_list = []
        now_iso = datetime.now(timezone.utc).isoformat()
        
        if self.latest_reading:
            r = self.latest_reading
            if r.radiation:
                obs_list.append({
                    "parameter": "RADIATION",
                    "value": r.radiation.absorbed_dose_rate_msv_day,
                    "unit": "mSv/day",
                    "source": "SIMULATED",
                    "timestamp": now_iso
                })
            if r.co2:
                obs_list.append({
                    "parameter": "CO2_CONCENTRATION",
                    "value": r.co2.co2_partial_pressure_mmhg,
                    "unit": "mmHg",
                    "source": "SIMULATED",
                    "timestamp": now_iso
                })
            # Include cabin pressure baseline if not degraded
            obs_list.append({
                "parameter": "CABIN_PRESSURE",
                "value": self.scenario.co2_params.cabin_pressure_kpa,
                "unit": "kPa",
                "source": "SIMULATED",
                "timestamp": now_iso
            })

        suggested = "NOMINAL"
        if self.latest_reading:
            if self.latest_reading.overall_hazard_level == HazardSeverity.CRITICAL:
                suggested = "CONTINGENCY"
            elif self.latest_reading.overall_hazard_level == HazardSeverity.WARNING:
                suggested = "DEGRADED"

        return Module4ExportPayload(
            source_session_id=self.session_id,
            simulation_timestamp_hours=self.current_time_hours,
            observations=obs_list,
            suggested_operational_state=suggested,
            provenance="SIMULATED"
        )


class SimulationController:
    """Coordinates lifecycle, step execution, and persistence for all hazard simulation sessions."""

    def __init__(self, db_session_factory: Callable[[], Session]):
        self._db_factory = db_session_factory
        self._active_sessions: Dict[str, SimulationSession] = {}

    def create_session(
        self,
        scenario: SimulationScenarioConfig,
        engine_type: EngineType = EngineType.COMBINED,
        mission_duration_hours: Optional[float] = None,
        timestep_hours: Optional[float] = None
    ) -> SimulationSession:
        """Initializes a new simulation session and persists its initial record."""
        session_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
        dur = mission_duration_hours or scenario.mission_duration_hours
        dt = timestep_hours or scenario.timestep_hours

        session = SimulationSession(
            session_id=session_id,
            scenario=scenario,
            engine_type=engine_type,
            mission_duration_hours=dur,
            timestep_hours=dt
        )
        self._active_sessions[session_id] = session

        # Persist session in DB
        db = self._db_factory()
        try:
            entity = SimulationSessionModel(
                session_id=session.session_id,
                scenario_id=scenario.scenario_id,
                scenario_name=scenario.scenario_name,
                engine_type=engine_type.value,
                status=session.status.value,
                current_time_hours=session.current_time_hours,
                total_duration_hours=session.total_duration_hours,
                timestep_hours=session.timestep_hours,
                provenance="SIMULATED"
            )
            db.add(entity)
            db.commit()
        finally:
            db.close()

        return session

    def get_session(self, session_id: str) -> Optional[SimulationSession]:
        """Retrieves session from memory cache or database."""
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
        
        # Fallback to DB
        db = self._db_factory()
        try:
            m = db.query(SimulationSessionModel).filter(SimulationSessionModel.session_id == session_id).first()
            if not m:
                return None
            # Reconstruct basic session representation
            # For brevity in cold load, scenario manager can fetch by m.scenario_id
            return None
        finally:
            db.close()

    def start_session(self, session_id: str) -> SimulationSession:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        s.status = SimulationStatus.RUNNING
        self._update_db_status(s)
        return s

    def pause_session(self, session_id: str) -> SimulationSession:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        s.status = SimulationStatus.PAUSED
        self._update_db_status(s)
        return s

    def resume_session(self, session_id: str) -> SimulationSession:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        s.status = SimulationStatus.RUNNING
        self._update_db_status(s)
        return s

    def stop_session(self, session_id: str) -> SimulationSession:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        s.status = SimulationStatus.STOPPED
        self._update_db_status(s)
        return s

    def reset_session(self, session_id: str) -> SimulationSession:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        s.status = SimulationStatus.IDLE
        s.current_time_hours = 0.0
        s.step_index = 0
        s.current_cumulative_radiation_msv = 0.0
        s.current_co2_mmhg = s.scenario.co2_params.initial_co2_mmhg
        s.current_sleep_debt_hours = s.scenario.sleep_params.initial_sleep_debt_hours
        s.timeline.clear()
        s.events.clear()
        s.latest_reading = None
        s.updated_at = datetime.now(timezone.utc)
        self._update_db_status(s)
        return s

    def step_session(self, session_id: str) -> CombinedStepReading:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        if s.status == SimulationStatus.COMPLETED:
            raise ValueError("Simulation already completed.")
        
        reading = s.advance_step()
        
        # Persist reading and events to database
        db = self._db_factory()
        try:
            r_entity = SimulationReadingModel(
                session_id=s.session_id,
                step_index=reading.step_index,
                simulation_time_hours=reading.simulation_time_hours,
                mission_day=reading.mission_day,
                radiation_incident_msv_day=reading.radiation.incident_dose_rate_msv_day if reading.radiation else None,
                radiation_absorbed_msv_day=reading.radiation.absorbed_dose_rate_msv_day if reading.radiation else None,
                radiation_cumulative_msv=reading.radiation.cumulative_dose_msv if reading.radiation else None,
                radiation_severity=reading.radiation.severity.value if reading.radiation else None,
                co2_partial_pressure_mmhg=reading.co2.co2_partial_pressure_mmhg if reading.co2 else None,
                co2_ppm=reading.co2.co2_ppm if reading.co2 else None,
                co2_generation_l_h=reading.co2.generation_rate_l_h if reading.co2 else None,
                co2_removal_l_h=reading.co2.removal_rate_l_h if reading.co2 else None,
                co2_efficiency=reading.co2.scrubber_efficiency if reading.co2 else None,
                co2_severity=reading.co2.severity.value if reading.co2 else None,
                sleep_required_hours=reading.sleep.required_sleep_hours if reading.sleep else None,
                sleep_actual_hours=reading.sleep.actual_sleep_hours if reading.sleep else None,
                sleep_daily_deficit_hours=reading.sleep.daily_deficit_hours if reading.sleep else None,
                sleep_daily_recovery_hours=reading.sleep.daily_recovery_hours if reading.sleep else None,
                sleep_cumulative_debt_hours=reading.sleep.cumulative_debt_hours if reading.sleep else None,
                sleep_severity=reading.sleep.severity.value if reading.sleep else None,
                overall_hazard_level=reading.overall_hazard_level.value,
                payload_json=reading.model_dump_json()
            )
            db.add(r_entity)

            # Persist newly triggered events
            for evt in reading.active_events:
                e_entity = SimulationEventModel(
                    session_id=s.session_id,
                    event_id=evt.event_id,
                    timestamp_hour=evt.timestamp_hour,
                    event_type=evt.event_type,
                    engine=evt.engine,
                    severity=evt.severity.value,
                    message=evt.message,
                    data_json=json.dumps(evt.data)
                )
                db.add(e_entity)

            # Update session row
            s_entity = db.query(SimulationSessionModel).filter(SimulationSessionModel.session_id == s.session_id).first()
            if s_entity:
                s_entity.current_time_hours = s.current_time_hours
                s_entity.status = s.status.value
                s_entity.updated_at = datetime.now(timezone.utc)

            db.commit()
        finally:
            db.close()

        return reading

    def run_session_to_end(self, session_id: str) -> SimulationResultsResponse:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        
        s.status = SimulationStatus.RUNNING
        while s.status != SimulationStatus.COMPLETED:
            self.step_session(session_id)
        self._update_db_status(s)

        return self.get_results(session_id)

    def get_results(self, session_id: str) -> SimulationResultsResponse:
        s = self.get_session(session_id)
        if not s:
            raise ValueError(f"Session {session_id} not found.")
        
        # Calculate summaries for engines
        rad_summary = None
        if s.engine_type in (EngineType.RADIATION, EngineType.COMBINED):
            rad_summary = s.radiation_engine.run_full_simulation(s.scenario.scenario_id)
        
        co2_summary = None
        if s.engine_type in (EngineType.CO2, EngineType.COMBINED):
            co2_summary = s.co2_engine.run_full_simulation(s.scenario.scenario_id)
            
        sleep_summary = None
        if s.engine_type in (EngineType.SLEEP, EngineType.COMBINED):
            sleep_summary = s.sleep_engine.run_full_simulation(s.scenario.scenario_id)

        return SimulationResultsResponse(
            session_id=s.session_id,
            scenario_id=s.scenario.scenario_id,
            engine_type=s.engine_type,
            status=s.status,
            total_steps=len(s.timeline),
            mission_duration_hours=s.total_duration_hours,
            radiation_summary=rad_summary,
            co2_summary=co2_summary,
            sleep_summary=sleep_summary,
            timeline=s.timeline,
            events=s.events,
            provenance=ProvenanceType.SIMULATED
        )

    def _update_db_status(self, session: SimulationSession):
        db = self._db_factory()
        try:
            s_entity = db.query(SimulationSessionModel).filter(SimulationSessionModel.session_id == session.session_id).first()
            if s_entity:
                s_entity.status = session.status.value
                s_entity.current_time_hours = session.current_time_hours
                s_entity.updated_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

