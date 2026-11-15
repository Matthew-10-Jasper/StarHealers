/**
 * StarHealers - REST API Service Client
 * Connects React Frontend with FastAPI Backend & SQLite Database.
 * Features automatic fallback to local demonstration data if backend is offline.
 */

import {
  MISSIONS as FALLBACK_MISSIONS,
  ASTRONAUTS as FALLBACK_ASTRONAUTS,
  CURRENT_READINGS as FALLBACK_READINGS,
  TRIAGE_ALERTS as FALLBACK_ALERTS,
  generateHistoricalData,
} from '../data/mockData';

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Helper to fetch with timeout and error handling
 */
async function fetchWithTimeout(url, options = {}, timeoutMs = 2500) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

// ==========================================
// MISSIONS API
// ==========================================
export async function getMissions() {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/missions`);
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (e) {
    console.warn('[StarHealers API] Backend unreachable; using local mission cache.');
  }
  return FALLBACK_MISSIONS;
}

// ==========================================
// ASTRONAUTS API
// ==========================================
export async function getAstronauts(missionId = null) {
  try {
    const url = missionId ? `${API_BASE_URL}/astronauts?mission_id=${missionId}` : `${API_BASE_URL}/astronauts`;
    const res = await fetchWithTimeout(url);
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (e) {
    console.warn('[StarHealers API] Backend unreachable; using local astronaut cache.');
  }
  return FALLBACK_ASTRONAUTS;
}

export async function getAstronaut(astronautId) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn(`[StarHealers API] Backend unreachable; using fallback for ${astronautId}`);
  }
  return FALLBACK_ASTRONAUTS.find((a) => a.id === astronautId) || FALLBACK_ASTRONAUTS[0];
}

// ==========================================
// HEALTH MONITORING API (Module 1)
// ==========================================
export async function getLatestHealth(astronautId) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}/health`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn(`[StarHealers API] Using local vitals cache for ${astronautId}`);
  }
  return FALLBACK_READINGS[astronautId] || FALLBACK_READINGS['ASTRO-01'];
}

export async function getHealthHistory(astronautId, timeRange = '24h') {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}/health/history?time_range=${timeRange}`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    }
  } catch (e) {
    console.warn(`[StarHealers API] Using generated telemetry series for ${astronautId}`);
  }
  return generateHistoricalData(astronautId, timeRange);
}

export async function postHealthReading(astronautId, readingPayload) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}/health/readings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(readingPayload),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('[StarHealers API] Failed to post reading to backend; offline mode active');
  }
  return { success: false, message: 'Offline demonstration mode' };
}

// ==========================================
// BODY MAP API (Module 2)
// ==========================================
export async function getBodyMap(astronautId) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}/body-map`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Handled in component
  }
  return null;
}

export async function getBodyRegionDetail(astronautId, regionId) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/astronauts/${astronautId}/body-map/${regionId}`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Handled in component
  }
  return null;
}

// ==========================================
// TRIAGE ALERTS API (Module 3)
// ==========================================
export async function getAlerts(astronautId = null, status = null) {
  try {
    let url = `${API_BASE_URL}/alerts?`;
    if (astronautId) url += `astronaut_id=${astronautId}&`;
    if (status) url += `status=${status}&`;
    const res = await fetchWithTimeout(url);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('[StarHealers API] Using local alerts cache');
  }
  return FALLBACK_ALERTS;
}

export async function resolveAlert(alertId, userId = 'USR-MED-01') {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/alerts/${alertId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn(`[StarHealers API] Local fallback resolution for ${alertId}`);
  }
  return { success: true, status: 'RESOLVED' };
}

export async function evaluateTriage(payload) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/triage/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('[StarHealers API] Local fallback triage evaluation');
  }
  return null;
}
