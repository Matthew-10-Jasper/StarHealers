import uuid
import statistics
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import PVTSessionModel, PVTTrialModel, AstronautModel
from app.schemas.schemas import (
    PVTTrialCreate,
    PVTSessionSubmitRequest,
    PVTSessionResponse,
    PVTTrialResponse,
    PVTHistoryResponse
)

def evaluate_and_record_pvt_session(
    db: Session,
    request: PVTSessionSubmitRequest
) -> PVTSessionResponse:
    # Ensure astronaut exists or create default
    astronaut = db.query(AstronautModel).filter(AstronautModel.astronaut_id == request.astronaut_id).first()
    if not astronaut:
        astronaut = AstronautModel(
            astronaut_id=request.astronaut_id,
            name=f"Astronaut {request.astronaut_id}",
            role="Mission Specialist"
        )
        db.add(astronaut)
        db.commit()
        db.refresh(astronaut)

    session_id = f"PVT-{uuid.uuid4().hex[:8].upper()}"
    reaction_times = [t.reaction_time_ms for t in request.trials]
    
    if not reaction_times:
        reaction_times = [280.0]

    avg_rt = round(float(statistics.mean(reaction_times)), 1)
    median_rt = round(float(statistics.median(reaction_times)), 1)
    slowest_rt = round(float(max(reaction_times)), 1)
    fastest_rt = round(float(min(reaction_times)), 1)
    
    lapses = 0
    false_starts = 0
    trial_models = []
    trial_responses = []
    
    for t in request.trials:
        is_lapse = (t.reaction_time_ms > 500.0)
        is_false_start = (t.reaction_time_ms < 100.0)
        if is_lapse:
            lapses += 1
        if is_false_start:
            false_starts += 1
            
        trial_models.append(PVTTrialModel(
            session_id=session_id,
            trial_number=t.trial_number,
            stimulus_delay_ms=t.stimulus_delay_ms,
            reaction_time_ms=t.reaction_time_ms,
            is_lapse=is_lapse,
            is_false_start=is_false_start
        ))
        
        trial_responses.append(PVTTrialResponse(
            trial_number=t.trial_number,
            stimulus_delay_ms=t.stimulus_delay_ms,
            reaction_time_ms=t.reaction_time_ms,
            is_lapse=is_lapse,
            is_false_start=is_false_start
        ))
        
    # Rating:
    if avg_rt < 260.0 and lapses == 0 and false_starts == 0:
        rating = "OPTIMAL"
    elif avg_rt < 360.0 and lapses <= 1:
        rating = "NORMAL"
    elif avg_rt < 500.0 and lapses <= 3:
        rating = "DEGRADED"
    else:
        rating = "IMPAIRED"
        
    now = datetime.now(timezone.utc)
    session_model = PVTSessionModel(
        session_id=session_id,
        astronaut_id=request.astronaut_id,
        trials_count=len(request.trials),
        avg_reaction_time_ms=avg_rt,
        median_reaction_time_ms=median_rt,
        lapses_count=lapses,
        false_starts_count=false_starts,
        slowest_reaction_ms=slowest_rt,
        fastest_reaction_ms=fastest_rt,
        performance_rating=rating,
        completed_at=now
    )
    
    db.add(session_model)
    db.flush()
    for tm in trial_models:
        db.add(tm)
    db.commit()
    
    return PVTSessionResponse(
        session_id=session_id,
        astronaut_id=request.astronaut_id,
        trials_count=len(request.trials),
        avg_reaction_time_ms=avg_rt,
        median_reaction_time_ms=median_rt,
        lapses_count=lapses,
        false_starts_count=false_starts,
        slowest_reaction_ms=slowest_rt,
        fastest_reaction_ms=fastest_rt,
        performance_rating=rating,
        completed_at=now,
        trials=trial_responses
    )

def get_pvt_history(db: Session, astronaut_id: str) -> PVTHistoryResponse:
    sessions = (
        db.query(PVTSessionModel)
        .filter(PVTSessionModel.astronaut_id == astronaut_id)
        .order_by(PVTSessionModel.completed_at.desc())
        .limit(20)
        .all()
    )
    
    if not sessions:
        return PVTHistoryResponse(
            astronaut_id=astronaut_id,
            total_sessions_completed=0,
            historical_avg_reaction_time_ms=275.0,
            sessions=[]
        )
        
    all_avgs = [s.avg_reaction_time_ms for s in sessions]
    historical_avg = round(float(statistics.mean(all_avgs)), 1)
    
    session_responses = []
    for s in sessions:
        trials = db.query(PVTTrialModel).filter(PVTTrialModel.session_id == s.session_id).all()
        tr_list = [
            PVTTrialResponse(
                trial_number=t.trial_number,
                stimulus_delay_ms=t.stimulus_delay_ms,
                reaction_time_ms=t.reaction_time_ms,
                is_lapse=t.is_lapse,
                is_false_start=t.is_false_start
            ) for t in trials
        ]
        session_responses.append(PVTSessionResponse(
            session_id=s.session_id,
            astronaut_id=s.astronaut_id,
            trials_count=s.trials_count,
            avg_reaction_time_ms=s.avg_reaction_time_ms,
            median_reaction_time_ms=s.median_reaction_time_ms,
            lapses_count=s.lapses_count,
            false_starts_count=s.false_starts_count,
            slowest_reaction_ms=s.slowest_reaction_ms,
            fastest_reaction_ms=s.fastest_reaction_ms,
            performance_rating=s.performance_rating,
            completed_at=s.completed_at,
            trials=tr_list
        ))
        
    return PVTHistoryResponse(
        astronaut_id=astronaut_id,
        total_sessions_completed=len(sessions),
        historical_avg_reaction_time_ms=historical_avg,
        sessions=session_responses
    )

