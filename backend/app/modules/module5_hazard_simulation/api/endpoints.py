import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import httpx

from app.modules.module5_hazard_simulation.core.config import settings
from app.modules.module5_hazard_simulation.database.session import SessionLocal
from app.modules.module5_hazard_simulation.schemas.enums import SimulationStatus, EngineType
from app.modules.module5_hazard_simulation.schemas.radiation import RadiationInput, RadiationSimulationResult
from app.modules.module5_hazard_simulation.schemas.co2 import CO2Input, CO2SimulationResult
from app.modules.module5_hazard_simulation.schemas.sleep import SleepInput, SleepSimulationResult
from app.modules.module5_hazard_simulation.schemas.scenario import SimulationScenarioConfig, ScenarioCreateRequest
from app.modules.module5_hazard_simulation.schemas.session import (
    SimulationSessionCreate, SimulationSessionResponse, SimulationResultsResponse,
    CombinedStepReading, Module4ExportPayload
)
from app.modules.module5_hazard_simulation.services.scenario_manager import ScenarioManager
from app.modules.module5_hazard_simulation.services.controller import SimulationController
from app.modules.module5_hazard_simulation.services.engines.radiation_engine import SpaceRadiationEngine
from app.modules.module5_hazard_simulation.services.engines.co2_engine import SpacecraftCO2Engine
from app.modules.module5_hazard_simulation.services.engines.sleep_engine import AstronautSleepEngine

logger = logging.getLogger("SimulationEndpoints")

router = APIRouter()

scenario_mgr = ScenarioManager()
controller = SimulationController(db_session_factory=SessionLocal)

# ----------------- SYSTEM & ENGINES -----------------

@router.get("/health", tags=["System Health"])
def get_health():
    """Health check endpoint for Module 5 Space Hazard Simulation Engine."""
    return {
        "status": "HEALTHY",
        "service": settings.MODULE_NAME,
        "module_id": settings.MODULE_ID,
        "version": settings.VERSION,
        "mode": "STANDALONE_INTEGRATION_READY",
        "supported_engines": ["RADIATION", "CO2", "SLEEP", "COMBINED"]
    }

@router.get("/engines", tags=["Simulation Engines"])
def get_available_engines():
    """Lists available space hazard simulation engines, physical models, and scientific inputs."""
    return [
        {
            "engine": "RADIATION",
            "name": "Space Radiation Simulator",
            "description": "Models Galactic Cosmic Ray background and Solar Particle Events (SPE) with physical shielding attenuation.",
            "primary_units": "mSv/day (dose rate), mSv (cumulative dose)",
            "governing_model": "Attenuated GCR background with lognormal/Weibull SPE proton outburst."
        },
        {
            "engine": "CO2",
            "name": "Spacecraft Cabin CO2 Simulator",
            "description": "Calculates cabin atmosphere CO2 evolution, crew generation, and scrubber degradation dynamics.",
            "primary_units": "mmHg (partial pressure), ppm (molar fraction), L/h (volumetric rate)",
            "governing_model": "Well-mixed single-compartment mass balance ODE: dC/dt = (G - R) / V."
        },
        {
            "engine": "SLEEP",
            "name": "Astronaut Sleep Debt Simulator",
            "description": "Simulates daily sleep deficit accumulation and recovery during mission operations.",
            "primary_units": "hours (daily deficit, recovery credit, cumulative debt)",
            "governing_model": "Non-clinical discrete daily sleep deficit and sub-unity recovery model."
        }
    ]

# ----------------- STANDALONE ENGINE RUNS -----------------

@router.post("/engines/radiation/run", response_model=RadiationSimulationResult, tags=["Simulation Engines"])
def run_standalone_radiation(params: RadiationInput):
    """Executes a standalone Space Radiation simulation trajectory."""
    engine = SpaceRadiationEngine(params)
    return engine.run_full_simulation()

@router.post("/engines/co2/run", response_model=CO2SimulationResult, tags=["Simulation Engines"])
def run_standalone_co2(params: CO2Input):
    """Executes a standalone Cabin CO2 evolution simulation trajectory."""
    engine = SpacecraftCO2Engine(params)
    return engine.run_full_simulation()

@router.post("/engines/sleep/run", response_model=SleepSimulationResult, tags=["Simulation Engines"])
def run_standalone_sleep(params: SleepInput):
    """Executes a standalone Astronaut Sleep Debt simulation trajectory."""
    engine = AstronautSleepEngine(params)
    return engine.run_full_simulation()

# ----------------- SCENARIOS -----------------

@router.get("/scenarios", response_model=List[SimulationScenarioConfig], tags=["Scenarios"])
def list_scenarios():
    """Lists all registered baseline and space hazard simulation scenarios."""
    return scenario_mgr.list_scenarios()

@router.get("/scenarios/{scenario_id}", response_model=SimulationScenarioConfig, tags=["Scenarios"])
def get_scenario(scenario_id: str):
    """Retrieves specific scenario configuration."""
    sc = scenario_mgr.get_scenario(scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return sc

@router.post("/scenarios", response_model=SimulationScenarioConfig, tags=["Scenarios"])
def create_scenario(req: ScenarioCreateRequest):
    """Registers a new user-configured simulation scenario."""
    sc = SimulationScenarioConfig(
        scenario_id=req.scenario_id,
        scenario_name=req.scenario_name,
        description=req.description,
        radiation_params=req.radiation_params or RadiationInput(),
        co2_params=req.co2_params or CO2Input(),
        sleep_params=req.sleep_params or SleepInput(),
        mission_duration_hours=req.mission_duration_hours or 168.0,
        timestep_hours=req.timestep_hours or 1.0
    )
    return scenario_mgr.register_scenario(sc)

# ----------------- SIMULATION SESSIONS -----------------

@router.post("/simulations", response_model=SimulationSessionResponse, tags=["Simulations"])
def create_simulation_session(req: SimulationSessionCreate):
    """Creates a new simulation session initialized with the specified scenario and engine configuration."""
    if req.custom_scenario:
        scenario = req.custom_scenario
        scenario_mgr.register_scenario(scenario)
    else:
        scenario = scenario_mgr.get_scenario(req.scenario_id or "NORMAL_MISSION")
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    session = controller.create_session(
        scenario=scenario,
        engine_type=req.engine_type,
        mission_duration_hours=req.mission_duration_hours,
        timestep_hours=req.timestep_hours
    )
    return session.to_response()

@router.get("/simulations/{session_id}", response_model=SimulationSessionResponse, tags=["Simulations"])
def get_simulation_session(session_id: str):
    """Retrieves current session status, simulation clock, and active reading."""
    session = controller.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Simulation session '{session_id}' not found.")
    return session.to_response()

@router.post("/simulations/{session_id}/start", response_model=SimulationSessionResponse, tags=["Simulations"])
def start_simulation(session_id: str):
    """Starts the simulation clock for the specified session."""
    try:
        session = controller.start_session(session_id)
        return session.to_response()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulations/{session_id}/pause", response_model=SimulationSessionResponse, tags=["Simulations"])
def pause_simulation(session_id: str):
    """Pauses the simulation clock."""
    try:
        session = controller.pause_session(session_id)
        return session.to_response()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulations/{session_id}/resume", response_model=SimulationSessionResponse, tags=["Simulations"])
def resume_simulation(session_id: str):
    """Resumes a paused simulation session."""
    try:
        session = controller.resume_session(session_id)
        return session.to_response()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulations/{session_id}/stop", response_model=SimulationSessionResponse, tags=["Simulations"])
def stop_simulation(session_id: str):
    """Stops the active simulation session."""
    try:
        session = controller.stop_session(session_id)
        return session.to_response()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulations/{session_id}/reset", response_model=SimulationSessionResponse, tags=["Simulations"])
def reset_simulation(session_id: str):
    """Resets the simulation clock and clear accumulated state back to t=0."""
    try:
        session = controller.reset_session(session_id)
        return session.to_response()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/simulations/{session_id}/step", response_model=CombinedStepReading, tags=["Simulations"])
def step_simulation(session_id: str):
    """Advances the simulation clock by one discrete timestep."""
    try:
        reading = controller.step_session(session_id)
        return reading
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulations/{session_id}/run-all", response_model=SimulationResultsResponse, tags=["Simulations"])
def run_simulation_to_end(session_id: str):
    """Runs the simulation synchronously from current time to total duration."""
    try:
        results = controller.run_session_to_end(session_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/simulations/{session_id}/results", response_model=SimulationResultsResponse, tags=["Simulations"])
def get_simulation_results(session_id: str):
    """Retrieves complete time-series results, engine summaries, and event history."""
    try:
        return controller.get_results(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- MODULE 4 INTEGRATION -----------------

@router.get("/simulations/{session_id}/export-module4", response_model=Module4ExportPayload, tags=["Module 4 Integration"])
def export_for_module4(session_id: str):
    """Formats current simulated readings into Module 4 EnvironmentalObservation integration payload."""
    session = controller.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Simulation session '{session_id}' not found.")
    return session.export_to_module4_format()

@router.post("/simulations/{session_id}/dispatch-module4", tags=["Module 4 Integration"])
def dispatch_to_module4(session_id: str):
    """Pushes simulated environmental observations directly to Module 4 live API."""
    session = controller.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Simulation session '{session_id}' not found.")

    payload = session.export_to_module4_format()
    if not payload.observations:
        raise HTTPException(status_code=400, detail="No observations available to dispatch. Advance simulation at least one step.")

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(
                f"{settings.MODULE4_API_URL}/missions/observations",
                json={"observations": payload.observations}
            )
            if resp.status_code == 200:
                return {
                    "status": "DISPATCHED",
                    "module4_response": resp.json(),
                    "exported_observations_count": len(payload.observations)
                }
            else:
                return {
                    "status": "MODULE4_ERROR",
                    "status_code": resp.status_code,
                    "detail": resp.text
                }
    except Exception as e:
        logger.warning(f"Failed to connect to Module 4 on {settings.MODULE4_API_URL}: {e}")
        return {
            "status": "MODULE4_UNREACHABLE",
            "message": f"Module 4 is not reachable at {settings.MODULE4_API_URL}. Ensure Module 4 backend is running on port 8004.",
            "payload_prepared": payload.model_dump()
        }

