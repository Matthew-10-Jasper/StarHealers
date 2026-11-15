import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.module5_hazard_simulation.core.config import settings
from app.modules.module5_hazard_simulation.api.endpoints import router as api_router
from app.modules.module5_hazard_simulation.api.websocket import ws_router
from app.modules.module5_hazard_simulation.database.session import engine, Base

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("StarhealersModule5")

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Module 5 — Space Hazard Simulation Engine. "
        "Simulates radiation exposure, cabin atmospheric CO2 mass balance, and astronaut sleep debt "
        "across configurable spaceflight scenarios."
    ),
    version=settings.VERSION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under both /api/v1 and root for seamless compatibility
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.PORT, reload=True)

