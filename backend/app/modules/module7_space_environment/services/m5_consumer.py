import math
from typing import List, Tuple
from app.modules.module7_space_environment.core.config import settings
from app.modules.module7_space_environment.schemas.schemas import (
    RadiationSeriesPoint,
    RadiationOverviewResponse,
    CO2SeriesPoint,
    CO2OverviewResponse
)

def get_radiation_overview(
    mission_hours: float = 72.0,
    has_active_spe: bool = True
) -> RadiationOverviewResponse:
    # Generate realistic simulated timeline reflecting Module 5 Weibull / GCR profiles
    series: List[RadiationSeriesPoint] = []
    gcr_hourly_rate = 0.075  # mSv/h baseline
    cum_gcr = 0.0
    cum_spe = 0.0
    
    # 24 timeline steps for graph display
    step_size = max(1.0, mission_hours / 24.0)
    for i in range(25):
        h = round(i * step_size, 1)
        # GCR accumulation
        cum_gcr = round(h * gcr_hourly_rate, 3)
        
        # Simulated SPE event starting around hour 36 peaking at hour 48
        current_rate = gcr_hourly_rate
        spe_step = 0.0
        if has_active_spe and h >= 30.0:
            # Weibull shaped spike
            t_rel = (h - 30.0) / 10.0
            spe_rate = max(0.0, 1.4 * (t_rel ** 1.8) * math.exp(-t_rel))
            current_rate += spe_rate
            cum_spe += spe_rate * step_size
            
        total_cum = round(cum_gcr + cum_spe, 3)
        series.append(RadiationSeriesPoint(
            hour=h,
            gcr_dose_msv=cum_gcr,
            spe_dose_msv=round(cum_spe, 3),
            total_cumulative_msv=total_cum,
            dose_rate_msv_h=round(current_rate, 4)
        ))
        
    last_pt = series[-1]
    total_dose = last_pt.total_cumulative_msv
    thirty_day_pct = round((total_dose / settings.RADIATION_30_DAY_LIMIT_MSV) * 100.0, 2)
    career_pct = round((total_dose / settings.RADIATION_CAREER_LIMIT_MSV) * 100.0, 2)
    
    return RadiationOverviewResponse(
        cumulative_dose_msv=total_dose,
        current_dose_rate_msv_h=last_pt.dose_rate_msv_h,
        gcr_component_msv=last_pt.gcr_dose_msv,
        spe_component_msv=last_pt.spe_dose_msv,
        career_limit_pct=career_pct,
        thirty_day_limit_pct=thirty_day_pct,
        active_spe_event=has_active_spe,
        shielding_material="ALUMINUM_COMPOSITE",
        shielding_thickness_g_cm2=15.0,
        time_series=series,
        provenance="SIMULATED_MODULE5_ENGINE"
    )

def get_co2_overview(
    mission_hours: float = 72.0,
    scrubber_degraded: bool = True
) -> CO2OverviewResponse:
    series: List[CO2SeriesPoint] = []
    step_size = max(1.0, mission_hours / 24.0)
    
    # 70.3 kPa ambient pressure ~ 527.3 mmHg total
    total_pressure_mmhg = 527.3
    
    for i in range(25):
        h = round(i * step_size, 1)
        if scrubber_degraded and h >= 24.0:
            # Gradual accumulation due to partial scrubber saturation
            t_rel = (h - 24.0) / 48.0
            efficiency = max(40.0, 95.0 - (t_rel * 50.0))
            co2_pct = min(0.85, 0.04 + (t_rel * 0.65))
        else:
            efficiency = 96.0
            co2_pct = 0.05
            
        ppco2 = round((co2_pct / 100.0) * total_pressure_mmhg, 2)
        series.append(CO2SeriesPoint(
            hour=h,
            co2_percent=round(co2_pct, 3),
            ppco2_mmhg=ppco2,
            scrubber_efficiency_pct=round(efficiency, 1)
        ))
        
    latest = series[-1]
    if latest.ppco2_mmhg >= settings.CO2_CRITICAL_THRESHOLD_MMHG:
        status = "CRITICAL"
    elif latest.ppco2_mmhg >= settings.CO2_WARNING_THRESHOLD_MMHG:
        status = "ELEVATED"
    else:
        status = "NOMINAL"
        
    return CO2OverviewResponse(
        current_co2_pct=latest.co2_percent,
        ppco2_mmhg=latest.ppco2_mmhg,
        status=status,
        scrubber_efficiency_pct=latest.scrubber_efficiency_pct,
        accumulated_exposure_hours=24.0 if scrubber_degraded else 0.0,
        time_series=series,
        provenance="SIMULATED_MODULE5_ENGINE"
    )
