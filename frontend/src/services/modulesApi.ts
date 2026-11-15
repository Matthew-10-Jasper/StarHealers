// Consolidated API client for Module 6 and Module 7 on Unified Backend port 8000
const M6_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';
const M7_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';

export interface Astronaut {
  astronaut_id: string;
  name: string;
  role: string;
  callsign?: string;
  baseline_sleep_hours: number;
  baseline_hrv_rmssd: number;
}

export interface SleepStatus {
  astronaut_id: string;
  total_sleep_hours_last_24h: number;
  recommended_sleep_hours: number;
  daily_deficit_hours: number;
  cumulative_sleep_debt_hours: number;
  sleep_debt_trend: string;
  sleep_disruption_active: boolean;
  data_source: string;
  last_updated: string;
}

export interface CircadianPoint {
  hour: number;
  alertness_score: number;
  biological_phase: string;
}

export interface CircadianRhythm {
  astronaut_id: string;
  mission_elapsed_hours: number;
  mission_day: number;
  local_mission_hour: number;
  current_phase: string;
  circadian_alignment_index: number;
  alertness_estimate: number;
  potential_disruption: boolean;
  disruption_notes?: string;
  alertness_curve_24h: CircadianPoint[];
  model_provenance: string;
}

export interface FatigueAssessment {
  astronaut_id: string;
  fatigue_level: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'UNRELIABLE';
  fatigue_score: number;
  heart_rate_bpm?: number;
  hrv_rmssd_ms?: number;
  sleep_deficit_hours: number;
  cumulative_debt_hours: number;
  stress_index?: number;
  reliable_data: boolean;
  assessment_notes: string;
  calculation_breakdown: Record<string, any>;
}

export interface StressTrendPoint {
  timestamp_hour: number;
  stress_score: number;
  sleep_debt_hours: number;
  hrv_rmssd?: number;
}

export interface StressMonitoring {
  astronaut_id: string;
  current_stress_score: number | null;
  stress_level: 'LOW' | 'MODERATE' | 'HIGH' | 'NO_DATA';
  historical_trend: StressTrendPoint[];
  sleep_debt_stress_correlation?: number;
  hrv_fatigue_correlation?: number;
  data_available: boolean;
}

export interface CognitiveReadiness {
  astronaut_id: string;
  overall_readiness_score: number;
  rating: 'OPTIMAL_PERFORMANCE' | 'QUALIFIED_MONITORED' | 'DEGRADED_RESTRICTED' | 'IMPAIRED';
  sleep_component: number;
  circadian_component: number;
  fatigue_component: number;
  stress_component: number;
  pvt_component: number;
  factor_weights: Record<string, number>;
  data_completeness: number;
  explanation: string;
  timestamp: string;
  non_clinical_disclaimer: string;
}

export interface PVTTrial {
  trial_number: number;
  stimulus_delay_ms: number;
  reaction_time_ms: number;
  is_lapse?: boolean;
  is_false_start?: boolean;
}

export interface PVTSession {
  session_id: string;
  astronaut_id: string;
  trials_count: number;
  avg_reaction_time_ms: number;
  median_reaction_time_ms: number;
  lapses_count: number;
  false_starts_count: number;
  slowest_reaction_ms?: number;
  fastest_reaction_ms?: number;
  performance_rating: string;
  completed_at: string;
  trials: PVTTrial[];
}

export interface PVTHistory {
  astronaut_id: string;
  total_sessions_completed: number;
  historical_avg_reaction_time_ms: number;
  sessions: PVTSession[];
}

// Module 7 interfaces
export interface RadiationPoint {
  hour: number;
  gcr_dose_msv: number;
  spe_dose_msv: number;
  total_cumulative_msv: number;
  dose_rate_msv_h: number;
}

export interface RadiationOverview {
  cumulative_dose_msv: number;
  current_dose_rate_msv_h: number;
  gcr_component_msv: number;
  spe_component_msv: number;
  career_limit_pct: number;
  thirty_day_limit_pct: number;
  active_spe_event: boolean;
  shielding_material: string;
  shielding_thickness_g_cm2: number;
  time_series: RadiationPoint[];
  provenance: string;
}

export interface CO2Point {
  hour: number;
  co2_percent: number;
  ppco2_mmhg: number;
  scrubber_efficiency_pct: number;
}

export interface CO2Overview {
  current_co2_pct: number;
  ppco2_mmhg: number;
  status: 'NOMINAL' | 'ELEVATED' | 'CRITICAL';
  scrubber_efficiency_pct: number;
  accumulated_exposure_hours: number;
  time_series: CO2Point[];
  provenance: string;
}

export interface CabinTelemetry {
  cabin_pressure_kpa: number | null;
  cabin_pressure_status: string;
  o2_percentage: number | null;
  o2_status: string;
  temperature_c: number | null;
  temperature_status: string;
  humidity_pct: number | null;
  humidity_status: string;
  mission_id: string;
  operational_state: string;
  telemetry_freshness: string;
  completeness: string;
}

export interface HazardAlert {
  alert_id: string;
  hazard_type: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  source_module: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
}

export interface CompositeRisk {
  overall_risk_index: number;
  operational_risk_level: 'NOMINAL' | 'MONITORING_REQUIRED' | 'CONTINGENCY' | 'EMERGENCY';
  radiation_risk_score: number;
  co2_risk_score: number;
  cabin_risk_score: number;
  active_hazards_count: number;
  summary: string;
  timestamp: string;
}

export const apiM6 = {
  async getHealth() {
    const res = await fetch(`${M6_BASE}/health`);
    if (!res.ok) throw new Error('Module 6 health check failed');
    return res.json();
  },

  async getAstronauts(): Promise<Astronaut[]> {
    const res = await fetch(`${M6_BASE}/astronauts`);
    if (!res.ok) throw new Error('Failed to fetch astronauts');
    return res.json();
  },

  async getSleep(astronautId: string, missionHour = 72): Promise<SleepStatus> {
    const res = await fetch(`${M6_BASE}/astronauts/${astronautId}/sleep?mission_hour=${missionHour}`);
    if (!res.ok) throw new Error('Failed to fetch sleep status');
    return res.json();
  },

  async getCircadian(astronautId: string, missionHour = 72): Promise<CircadianRhythm> {
    const res = await fetch(`${M6_BASE}/astronauts/${astronautId}/circadian?mission_hour=${missionHour}`);
    if (!res.ok) throw new Error('Failed to fetch circadian rhythm');
    return res.json();
  },

  async getFatigue(astronautId: string): Promise<FatigueAssessment> {
    const res = await fetch(`${M6_BASE}/astronauts/${astronautId}/fatigue`);
    if (!res.ok) throw new Error('Failed to fetch fatigue assessment');
    return res.json();
  },

  async getStress(astronautId: string): Promise<StressMonitoring> {
    const res = await fetch(`${M6_BASE}/astronauts/${astronautId}/stress`);
    if (!res.ok) throw new Error('Failed to fetch stress monitoring');
    return res.json();
  },

  async getReadiness(astronautId: string): Promise<CognitiveReadiness> {
    const res = await fetch(`${M6_BASE}/astronauts/${astronautId}/readiness`);
    if (!res.ok) throw new Error('Failed to fetch cognitive readiness');
    return res.json();
  },

  async submitPVT(payload: { astronaut_id: string; trials: { trial_number: number; stimulus_delay_ms: number; reaction_time_ms: number }[] }): Promise<PVTSession> {
    const res = await fetch(`${M6_BASE}/pvt/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to submit PVT session');
    return res.json();
  },

  async getPVTHistory(astronautId: string): Promise<PVTHistory> {
    const res = await fetch(`${M6_BASE}/pvt/${astronautId}/history`);
    if (!res.ok) throw new Error('Failed to fetch PVT history');
    return res.json();
  }
};

export const apiM7 = {
  async getHealth() {
    const res = await fetch(`${M7_BASE}/health`);
    if (!res.ok) throw new Error('Module 7 health check failed');
    return res.json();
  },

  async getOverview(): Promise<CompositeRisk> {
    const res = await fetch(`${M7_BASE}/environment/overview`);
    if (!res.ok) throw new Error('Failed to fetch composite risk overview');
    return res.json();
  },

  async getRadiation(missionHours = 72, hasActiveSpe = true): Promise<RadiationOverview> {
    const res = await fetch(`${M7_BASE}/environment/radiation?mission_hours=${missionHours}&has_active_spe=${hasActiveSpe}`);
    if (!res.ok) throw new Error('Failed to fetch radiation overview');
    return res.json();
  },

  async getCO2(missionHours = 72, scrubberDegraded = true): Promise<CO2Overview> {
    const res = await fetch(`${M7_BASE}/environment/co2?mission_hours=${missionHours}&scrubber_degraded=${scrubberDegraded}`);
    if (!res.ok) throw new Error('Failed to fetch CO2 overview');
    return res.json();
  },

  async getCabin(): Promise<CabinTelemetry> {
    const res = await fetch(`${M7_BASE}/environment/cabin`);
    if (!res.ok) throw new Error('Failed to fetch cabin telemetry');
    return res.json();
  },

  async getAlerts(acknowledged?: boolean): Promise<HazardAlert[]> {
    const url = acknowledged !== undefined ? `${M7_BASE}/alerts?acknowledged=${acknowledged}` : `${M7_BASE}/alerts`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch hazard alerts');
    return res.json();
  },

  async acknowledgeAlert(alertId: string, acknowledgedBy: string, notes?: string): Promise<HazardAlert> {
    const res = await fetch(`${M7_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ acknowledged_by: acknowledgedBy, notes })
    });
    if (!res.ok) throw new Error('Failed to acknowledge alert');
    return res.json();
  }
};

