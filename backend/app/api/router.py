from fastapi import APIRouter
from app.api.v1.overview import router as overview_router
from app.modules.module123_suba.routers import (
    astronauts as suba_astros,
    health as suba_health,
    bodymap as suba_bodymap,
    triage as suba_triage,
    missions as suba_missions
)
from app.modules.module4_mission_intelligence.api.endpoints import router as m4_router
from app.modules.module5_hazard_simulation.api.endpoints import router as m5_router
from app.modules.module6_circadian_fatigue.api.endpoints import router as m6_router
from app.modules.module7_space_environment.api.endpoints import router as m7_router

api_v1_router = APIRouter(prefix="/api/v1")

# Unified Overview
api_v1_router.include_router(overview_router)

# Module 1: Astronaut Health & Vitals
api_v1_router.include_router(suba_astros.router, prefix="/module1")
api_v1_router.include_router(suba_health.router, prefix="/module1")

# Module 2: Anatomical Body Map
api_v1_router.include_router(suba_bodymap.router, prefix="/module2")

# Module 3: Intelligent Clinical Triage
api_v1_router.include_router(suba_triage.router, prefix="/module3")

# Module 4: Mission Environment Intelligence
api_v1_router.include_router(m4_router, prefix="/module4")

# Module 5: Space Hazard Simulation Engine
api_v1_router.include_router(m5_router, prefix="/module5")

# Module 6: Circadian, Fatigue & Stress
api_v1_router.include_router(m6_router, prefix="/module6")

# Module 7: Space Environment & Radiation
api_v1_router.include_router(m7_router, prefix="/module7")
