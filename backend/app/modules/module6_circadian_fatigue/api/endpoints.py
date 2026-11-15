from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.modules.module6_circadian_fatigue.database.session import get_db
from app.modules.module6_circadian_fatigue.models.models import AstronautModel, PVTSessionModel
from app.modules.module6_circadian_fatigue.schemas.schemas import (
    AstronautSchema,
    SleepStatusResponse,
    CircadianRhythmResponse,
    FatigueAssessmentResponse,
    StressMonitoringResponse,
    CognitiveReadinessResponse,
    PVTSessionSubmitRequest,
    PVTSessionResponse,
    PVTHistoryResponse
)
from app.modules.module6_circadian_fatigue.services.circadian_service import get_circadian_rhythm
from app.modules.module6_circadian_fatigue.services.fatigue_service import compute_fatigue_assessment
from app.modules.module6_circadian_fatigue.services.stress_service import compute_stress_monitoring
from app.modules.module6_circadian_fatigue.services.pvt_service import evaluate_and_record_pvt_session, get_pvt_history
from app.modules.module6_circadian_fatigue.services.readiness_engine import calculate_cognitive_readiness

router = APIRouter()

DEFAULT_ASTRONAUTS = [
    {"astronaut_id": "ASTRO-01", "name": "Cmdr. Sarah Vance", "role": "Mission Commander", "callsign": "ARES-LEAD", "baseline_sleep_hours": 8.0, "baseline_hrv_rmssd": 55.0},
    {"astronaut_id": "ASTRO-02", "name": "Maj. Mark Robinson", "role": "Command Module Pilot", "callsign": "ARES-PILOT", "baseline_sleep_hours": 7.5, "baseline_hrv_rmssd": 50.0},
    {"astronaut_id": "ASTRO-03", "name": "Dr. Elena Rostova", "role": "Chief Science Officer", "callsign": "ARES-SCI", "baseline_sleep_hours": 8.0, "baseline_hrv_rmssd": 52.0},
    {"astronaut_id": "ASTRO-04", "name": "Lt. Chen Wei", "role": "Flight Engineer", "callsign": "ARES-ENG", "baseline_sleep_hours": 8.0, "baseline_hrv_rmssd": 48.0},
]

def seed_astronauts_if_empty(db: Session):
    count = db.query(AstronautModel).count()
    if count == 0:
        for a in DEFAULT_ASTRONAUTS:
            db.add(AstronautModel(**a))
        db.commit()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "module6_circadian_fatigue",
        "port": 8006,
        "capabilities": [
            "circadian_two_process_model",
            "fatigue_assessment",
            "stress_monitoring",
            "pvt_test_engine",
            "cognitive_readiness"
        ]
    }

@router.get("/astronauts", response_model=List[AstronautSchema])
def list_astronauts(db: Session = Depends(get_db)):
    seed_astronauts_if_empty(db)
    astronauts = db.query(AstronautModel).all()
    return [
        AstronautSchema(
            astronaut_id=a.astronaut_id,
            name=a.name,
            role=a.role,
            callsign=a.callsign,
            baseline_sleep_hours=a.baseline_sleep_hours,
            baseline_hrv_rmssd=a.baseline_hrv_rmssd
        ) for a in astronauts
    ]

@router.post("/astronauts", response_model=AstronautSchema)
def register_astronaut(payload: AstronautSchema, db: Session = Depends(get_db)):
    existing = db.query(AstronautModel).filter(AstronautModel.astronaut_id == payload.astronaut_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Astronaut {payload.astronaut_id} already registered.")
    
    astro = AstronautModel(
        astronaut_id=payload.astronaut_id,
        name=payload.name,
        role=payload.role,
        callsign=payload.callsign,
        baseline_sleep_hours=payload.baseline_sleep_hours,
        baseline_hrv_rmssd=payload.baseline_hrv_rmssd
    )
    db.add(astro)
    db.commit()
    db.refresh(astro)
    return payload

@router.get("/astronauts/{astronaut_id}/sleep", response_model=SleepStatusResponse)
def get_sleep_status(
    astronaut_id: str,
    mission_hour: float = Query(72.0, ge=0.0),
    db: Session = Depends(get_db)
):
    seed_astronauts_if_empty(db)
    # Simulated sleep status connected to Module 5 profile dynamics
    # Variance depending on astronaut_id
    debt_map = {
        "ASTRO-01": (6.5, 1.5, 2.8, "ACCUMULATING", False),
        "ASTRO-02": (5.0, 2.5, 5.2, "ACCUMULATING", True),
        "ASTRO-03": (7.8, 0.2, 0.8, "STABLE", False),
        "ASTRO-04": (7.0, 1.0, 1.5, "RECOVERING", False)
    }
    sleep_info = debt_map.get(astronaut_id, (6.8, 1.2, 2.0, "STABLE", False))
    
    return SleepStatusResponse(
        astronaut_id=astronaut_id,
        total_sleep_hours_last_24h=sleep_info[0],
        recommended_sleep_hours=8.0,
        daily_deficit_hours=sleep_info[1],
        cumulative_sleep_debt_hours=sleep_info[2],
        sleep_debt_trend=sleep_info[3],
        sleep_disruption_active=sleep_info[4],
        data_source="SIMULATED_MODULE5"
    )

@router.get("/astronauts/{astronaut_id}/circadian", response_model=CircadianRhythmResponse)
def get_circadian(
    astronaut_id: str,
    mission_hour: float = Query(72.0, ge=0.0),
    db: Session = Depends(get_db)
):
    seed_astronauts_if_empty(db)
    # Derive debt based on astronaut profile
    debt_val = 5.2 if astronaut_id == "ASTRO-02" else (2.8 if astronaut_id == "ASTRO-01" else 1.2)
    shift_val = 4.0 if astronaut_id == "ASTRO-02" else 0.0
    return get_circadian_rhythm(
        astronaut_id=astronaut_id,
        mission_elapsed_hours=mission_hour,
        sleep_debt_hours=debt_val,
        local_shift_hours=shift_val
    )

@router.get("/astronauts/{astronaut_id}/fatigue", response_model=FatigueAssessmentResponse)
def get_fatigue(
    astronaut_id: str,
    db: Session = Depends(get_db)
):
    seed_astronauts_if_empty(db)
    astro = db.query(AstronautModel).filter(AstronautModel.astronaut_id == astronaut_id).first()
    baseline_hrv = astro.baseline_hrv_rmssd if astro else 52.0
    
    # Specific realistic profile metrics
    if astronaut_id == "ASTRO-02":
        return compute_fatigue_assessment(
            astronaut_id=astronaut_id,
            sleep_deficit_hours=2.5,
            cumulative_debt_hours=5.2,
            hrv_rmssd_ms=36.0,
            heart_rate_bpm=78.0,
            baseline_hrv=baseline_hrv
        )
    elif astronaut_id == "ASTRO-01":
        return compute_fatigue_assessment(
            astronaut_id=astronaut_id,
            sleep_deficit_hours=1.5,
            cumulative_debt_hours=2.8,
            hrv_rmssd_ms=49.0,
            heart_rate_bpm=70.0,
            baseline_hrv=baseline_hrv
        )
    else:
        return compute_fatigue_assessment(
            astronaut_id=astronaut_id,
            sleep_deficit_hours=0.5,
            cumulative_debt_hours=1.0,
            hrv_rmssd_ms=52.0,
            heart_rate_bpm=65.0,
            baseline_hrv=baseline_hrv
        )

@router.get("/astronauts/{astronaut_id}/stress", response_model=StressMonitoringResponse)
def get_stress(
    astronaut_id: str,
    db: Session = Depends(get_db)
):
    seed_astronauts_if_empty(db)
    astro = db.query(AstronautModel).filter(AstronautModel.astronaut_id == astronaut_id).first()
    baseline_hrv = astro.baseline_hrv_rmssd if astro else 52.0
    
    if astronaut_id == "ASTRO-02":
        return compute_stress_monitoring(
            astronaut_id=astronaut_id,
            current_hrv_rmssd=36.0,
            current_heart_rate=78.0,
            sleep_debt_hours=5.2,
            baseline_hrv=baseline_hrv,
            data_available=True
        )
    elif astronaut_id == "ASTRO-01":
        return compute_stress_monitoring(
            astronaut_id=astronaut_id,
            current_hrv_rmssd=49.0,
            current_heart_rate=70.0,
            sleep_debt_hours=2.8,
            baseline_hrv=baseline_hrv,
            data_available=True
        )
    else:
        return compute_stress_monitoring(
            astronaut_id=astronaut_id,
            current_hrv_rmssd=52.0,
            current_heart_rate=65.0,
            sleep_debt_hours=1.0,
            baseline_hrv=baseline_hrv,
            data_available=True
        )

@router.get("/astronauts/{astronaut_id}/readiness", response_model=CognitiveReadinessResponse)
def get_cognitive_readiness(
    astronaut_id: str,
    db: Session = Depends(get_db)
):
    seed_astronauts_if_empty(db)
    # Check if there is latest PVT session in DB
    latest_pvt = (
        db.query(PVTSessionModel)
        .filter(PVTSessionModel.astronaut_id == astronaut_id)
        .order_by(PVTSessionModel.completed_at.desc())
        .first()
    )
    
    pvt_rt = latest_pvt.avg_reaction_time_ms if latest_pvt else (340.0 if astronaut_id == "ASTRO-02" else 265.0)
    pvt_lapses = latest_pvt.lapses_count if latest_pvt else (2 if astronaut_id == "ASTRO-02" else 0)
    
    if astronaut_id == "ASTRO-02":
        return calculate_cognitive_readiness(
            astronaut_id=astronaut_id,
            sleep_debt_hours=5.2,
            circadian_alertness=62.0,
            circadian_alignment=0.68,
            fatigue_score=68.0,
            stress_score=62.0,
            pvt_avg_rt_ms=pvt_rt,
            pvt_lapses=pvt_lapses
        )
    elif astronaut_id == "ASTRO-01":
        return calculate_cognitive_readiness(
            astronaut_id=astronaut_id,
            sleep_debt_hours=2.8,
            circadian_alertness=78.0,
            circadian_alignment=0.88,
            fatigue_score=38.0,
            stress_score=36.0,
            pvt_avg_rt_ms=pvt_rt,
            pvt_lapses=pvt_lapses
        )
    else:
        return calculate_cognitive_readiness(
            astronaut_id=astronaut_id,
            sleep_debt_hours=1.0,
            circadian_alertness=92.0,
            circadian_alignment=0.96,
            fatigue_score=15.0,
            stress_score=22.0,
            pvt_avg_rt_ms=pvt_rt,
            pvt_lapses=pvt_lapses
        )

@router.post("/pvt/submit", response_model=PVTSessionResponse)
def submit_pvt(payload: PVTSessionSubmitRequest, db: Session = Depends(get_db)):
    if not payload.trials:
        raise HTTPException(status_code=400, detail="PVT session must contain at least 1 trial.")
    return evaluate_and_record_pvt_session(db, payload)

@router.get("/pvt/{astronaut_id}/history", response_model=PVTHistoryResponse)
def get_astronaut_pvt_history(astronaut_id: str, db: Session = Depends(get_db)):
    seed_astronauts_if_empty(db)
    return get_pvt_history(db, astronaut_id)

