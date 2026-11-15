/**
 * STARHEALERS Unified API Client
 * Single consolidated API gateway connecting the unified React frontend
 * to the unified FastAPI backend running on port 8000.
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';
export const WS_BASE_URL = (import.meta.env.VITE_WS_BASE_URL as string) || 'ws://127.0.0.1:8000';

async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const err = await response.json();
      if (err.detail) errorDetail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  // System Health
  async getSystemHealth() {
    return fetchJson<any>('/health');
  },

  // Unified Overview
  async getUnifiedOverview() {
    return fetchJson<any>('/api/v1/overview');
  },

  // ==========================================
  // MODULE 1, 2, 3: SUBA ADAPTERS
  // ==========================================
  async getMissions() {
    return fetchJson<any[]>('/api/missions');
  },

  async getAstronauts(missionId?: string) {
    const url = missionId ? `/api/astronauts?mission_id=${missionId}` : '/api/astronauts';
    return fetchJson<any[]>(url);
  },

  async getAstronaut(astronautId: string) {
    return fetchJson<any>(`/api/astronauts/${astronautId}`);
  },

  async getLatestHealth(astronautId: string) {
    return fetchJson<Record<string, any>>(`/api/astronauts/${astronautId}/health`);
  },

  async getHealthHistory(astronautId: string, timeRange = '24h') {
    return fetchJson<any[]>(`/api/astronauts/${astronautId}/health/history?time_range=${timeRange}`);
  },

  async injectHealthReading(reading: any) {
    return fetchJson<any>('/api/astronauts/health/readings', {
      method: 'POST',
      body: JSON.stringify(reading),
    });
  },

  async getBodyMap(astronautId: string) {
    return fetchJson<any>(`/api/astronauts/${astronautId}/bodymap`);
  },

  async getBodyRegionDetail(astronautId: string, regionId: string) {
    return fetchJson<any>(`/api/astronauts/${astronautId}/bodymap/${regionId}`);
  },

  async getAlerts(status?: string, astronautId?: string) {
    let url = '/api/alerts';
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (astronautId) params.append('astronaut_id', astronautId);
    if (params.toString()) url += `?${params.toString()}`;
    return fetchJson<any[]>(url);
  },

  async resolveAlert(alertId: string, actionNote: string, resolvedBy: string) {
    return fetchJson<any>(`/api/alerts/${alertId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ action_note: actionNote, resolved_by: resolvedBy }),
    });
  },

  async getTriageRules() {
    return fetchJson<any[]>('/api/triage/rules');
  },

  // ==========================================
  // MODULE 4: MISSION INTELLIGENCE
  // ==========================================
  async getCurrentMissionContext() {
    return fetchJson<any>('/missions/current');
  },

  async getMissionProfiles() {
    return fetchJson<any[]>('/missions');
  },

  async selectMissionProfile(missionId: string, operatorId = 'FLIGHT_DIRECTOR') {
    return fetchJson<any>('/missions/select', {
      method: 'POST',
      body: JSON.stringify({ mission_id: missionId, operator_id: operatorId }),
    });
  },

  async requestStateTransition(targetState: string, reason: string, evidence?: Record<string, any>) {
    return fetchJson<any>('/context/state', {
      method: 'POST',
      body: JSON.stringify({
        target_state: targetState,
        reason,
        authorized_by: 'MISSION_COMMANDER',
        evidence: evidence || {},
      }),
    });
  },

  async getDeviations() {
    return fetchJson<any[]>('/missions/current/deviations');
  },

  async getMissionHistory() {
    return fetchJson<any>('/missions/history');
  },

  async runScenario(scenarioType: string) {
    return fetchJson<any>(`/scenarios/run?scenario_type=${encodeURIComponent(scenarioType)}`, {
      method: 'POST',
    });
  },

  async generateTelemetryStream() {
    return fetchJson<any>('/stream/generate', { method: 'POST' });
  },

  // ==========================================
  // MODULE 5: SPACE HAZARD SIMULATION
  // ==========================================
  async getSimulationEngines() {
    return fetchJson<any[]>('/engines');
  },

  async getSimulationScenarios() {
    return fetchJson<any[]>('/simulations/scenarios');
  },

  async runRadiationSimulation(params: {
    duration_hours: number;
    timestep_hours?: number;
    gcr_dose_rate_msv_per_day: number;
    spe_active?: boolean;
    spe_peak_multiplier?: number;
    spe_start_hour?: number;
    spe_duration_hours?: number;
    shielding_thickness_g_cm2: number;
    shielding_material?: string;
  }) {
    return fetchJson<any>('/engines/radiation/run', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  async runCO2Simulation(params: {
    duration_hours: number;
    timestep_hours?: number;
    cabin_volume_m3: number;
    crew_count: number;
    generation_rate_per_person_l_h: number;
    initial_co2_mmhg: number;
    scrubber_efficiency: number;
    scrubber_nominal_removal_l_h: number;
    scrubber_failure_active?: boolean;
  }) {
    return fetchJson<any>('/engines/co2/run', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  async runSleepSimulation(params: {
    total_days: number;
    baseline_sleep_hours?: number;
    daily_sleep_hours?: number[];
    disruption_active?: boolean;
    disruption_type?: string;
  }) {
    return fetchJson<any>('/engines/sleep/run', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  async createSimulationSession(config: any) {
    return fetchJson<any>('/simulations', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  async stepSimulation(sessionId: string) {
    return fetchJson<any>(`/simulations/${sessionId}/step`, { method: 'POST' });
  },

  async runSimulationToEnd(sessionId: string) {
    return fetchJson<any>(`/simulations/${sessionId}/run-to-end`, { method: 'POST' });
  },

  async getSimulationResults(sessionId: string) {
    return fetchJson<any>(`/simulations/${sessionId}/results`);
  },

  async exportSimulationToModule4(sessionId: string) {
    return fetchJson<any>(`/simulations/${sessionId}/export-to-module4`, { method: 'POST' });
  },

  // ==========================================
  // MODULE 6: CIRCADIAN, FATIGUE & PVT
  // ==========================================
  async getCircadianRhythm(astronautId: string) {
    return fetchJson<any>(`/astronauts/${astronautId}/circadian`);
  },

  async getFatigueAssessment(astronautId: string) {
    return fetchJson<any>(`/astronauts/${astronautId}/fatigue`);
  },

  async getSleepStatus(astronautId: string) {
    return fetchJson<any>(`/astronauts/${astronautId}/sleep-status`);
  },

  async submitPVTSession(sessionData: any) {
    return fetchJson<any>('/pvt/session', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  },

  // ==========================================
  // MODULE 7: SPACE ENVIRONMENT & RADIATION
  // ==========================================
  async getSpaceEnvironmentTelemetry() {
    return fetchJson<any>('/environment/latest');
  },

  async getAstronautDose(astronautId: string) {
    return fetchJson<any>(`/radiation/astronauts/${astronautId}/dose`);
  },

  async getLifeSupportTelemetry() {
    return fetchJson<any>('/life-support/telemetry');
  },

  async getEnvironmentAlerts() {
    return fetchJson<any[]>('/alerts');
  },
};
