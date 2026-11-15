"""
StarHealers — Autonomous Crew Medical Officer Backend
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers import missions, astronauts, health, bodymap, triage
from database import init_db, DB_PATH
from seed_data import seed

# Initialize Database on startup if not present
if not DB_PATH.exists():
    seed()

app = FastAPI(
    title="StarHealers — Autonomous Crew Medical Officer API",
    description="Autonomous deep-space mission medical decision support, continuous physiological vitals, SVG anatomical telemetry, and explainable rule-based clinical triage.",
    version="2.4-MED",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(missions.router)
app.include_router(astronauts.router)
app.include_router(health.router)
app.include_router(bodymap.router)
app.include_router(triage.router)


# Global Exception Handlers for Uniform Error Responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "status_code": 422,
            "message": "Input validation error in physiological telemetry payload",
            "details": jsonable_encoder(exc.errors()),
            "path": request.url.path
        }
    )


@app.get("/", tags=["System Status"])
def root():
    return {
        "system": "StarHealers Autonomous Crew Medical Officer",
        "version": "2.4-MED",
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "modules": {
            "module1_vitals": "/api/astronauts/{astronaut_id}/health",
            "module2_bodymap": "/api/astronauts/{astronaut_id}/body-map",
            "module3_triage": "/api/alerts",
            "missions": "/api/missions",
            "crew": "/api/astronauts"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
