from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.health import check_system_health
from app.core.logging import logger
from app.api.router import api_v1_router

# Direct module routers for backwards compatibility
from app.modules.module123_suba.routers import (
    astronauts as suba_astros,
    health as suba_health,
    bodymap as suba_bodymap,
    triage as suba_triage,
    missions as suba_missions
)
from app.modules.module4_mission_intelligence.api.endpoints import router as m4_router
from app.modules.module5_hazard_simulation.api.endpoints import router as m5_router
from app.modules.module5_hazard_simulation.api.websocket import ws_router as m5_ws_router
from app.modules.module6_circadian_fatigue.api.endpoints import router as m6_router
from app.modules.module7_space_environment.api.endpoints import router as m7_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Consolidated Single-Entrypoint Backend for all 7 STARHEALERS modules",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount Unified Versioned API (/api/v1)
app.include_router(api_v1_router)

# 2. Mount Backward-Compatible Direct Routes
# Suba Modules 1-3
app.include_router(suba_missions.router)
app.include_router(suba_astros.router)
app.include_router(suba_health.router)
app.include_router(suba_bodymap.router)
app.include_router(suba_triage.router)

# Module 4 Mission Intelligence
app.include_router(m4_router)

# Module 5 Hazard Simulation
app.include_router(m5_router)
app.include_router(m5_ws_router)

# Module 6 Circadian, Fatigue & PVT
app.include_router(m6_router)

# Module 7 Space Environment & Radiation
app.include_router(m7_router)

@app.get("/")
def root():
    return {
        "platform": "STARHEALERS UNIFIED PLATFORM",
        "status": "OPERATIONAL",
        "version": settings.VERSION,
        "entrypoints": {
            "unified_v1_api": "/api/v1",
            "mission_overview": "/api/v1/overview",
            "health_check": "/health",
            "api_docs": "/docs"
        },
        "modules": [
            "Module 1: Astronaut Health & Continuous Physiological Readings",
            "Module 2: Anatomical Body Map & Regional Health Telemetry",
            "Module 3: Intelligent Clinical Triage & Flight Rule Engine",
            "Module 4: Mission Environment Intelligence & Adaptive Context",
            "Module 5: Space Hazard Simulation Engine (Radiation, CO2, Sleep)",
            "Module 6: Circadian Rhythm, Fatigue, Stress & PVT Test Battery",
            "Module 7: Space Environment, Radiation Limits & Life Support"
        ]
    }

@app.get("/health")
def health():
    return check_system_health()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting STARHEALERS Unified Backend on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
