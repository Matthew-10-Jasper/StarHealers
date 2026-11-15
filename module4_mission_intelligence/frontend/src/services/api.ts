import {
  MissionContextResponse,
  MissionProfile,
  MissionDeviation,
  MissionHistoryResponse,
  OperationalState
} from '../types/mission';

const API_BASE = 'http://localhost:8004';
const WS_BASE = 'ws://localhost:8004/ws/telemetry';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getCurrentMission(): Promise<MissionContextResponse> {
    const res = await fetch(`${API_BASE}/missions/current`);
    if (!res.ok) throw new Error('Failed to fetch current mission');
    return res.json();
  },

  async getMissions(): Promise<MissionProfile[]> {
    const res = await fetch(`${API_BASE}/missions`);
    if (!res.ok) throw new Error('Failed to fetch mission profiles');
    return res.json();
  },

  async selectMission(missionId: string): Promise<MissionContextResponse> {
    const res = await fetch(`${API_BASE}/missions/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mission_id: missionId, operator_id: 'FLIGHT_DIRECTOR' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to select mission');
    }
    return res.json();
  },

  async getDeviations(): Promise<MissionDeviation[]> {
    const res = await fetch(`${API_BASE}/missions/current/deviations`);
    if (!res.ok) throw new Error('Failed to fetch deviations');
    return res.json();
  },

  async requestStateTransition(
    targetState: OperationalState,
    reason: string,
    evidence: Record<string, any> = {}
  ): Promise<MissionContextResponse> {
    const res = await fetch(`${API_BASE}/missions/transition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_state: targetState,
        reason,
        evidence,
        operator_id: 'MISSION_CONTROLLER'
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'State transition rejected');
    }
    return res.json();
  },

  async updateContext(
    actualPhase?: string,
    reason: string = 'Manual Phase/Gravity Update',
    evidence: Record<string, any> = {}
  ): Promise<MissionContextResponse> {
    const res = await fetch(`${API_BASE}/missions/context/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actual_mission_phase: actualPhase,
        reason,
        evidence,
        operator_id: 'MISSION_CONTROLLER'
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update context');
    }
    return res.json();
  },

  async getHistory(missionId?: string, limit: number = 50, offset: number = 0): Promise<MissionHistoryResponse> {
    const params = new URLSearchParams({ limit: limit.toString(), offset: offset.toString() });
    if (missionId) params.append('mission_id', missionId);
    const res = await fetch(`${API_BASE}/missions/history?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
  },

  async runScenario(scenario: string) {
    const res = await fetch(`${API_BASE}/simulator/scenario?scenario=${encodeURIComponent(scenario)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to run scenario');
    return res.json();
  },

  async generateTelemetryStream() {
    const res = await fetch(`${API_BASE}/simulator/generate-stream`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to generate telemetry stream');
    return res.json();
  },

  async getIntegrationContract() {
    const res = await fetch(`${API_BASE}/integrations/contract`);
    if (!res.ok) throw new Error('Failed to fetch contract');
    return res.json();
  },

  async deliverMockIntegration(targetModule: string) {
    const res = await fetch(`${API_BASE}/integrations/deliver/${targetModule}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to deliver mock contract');
    return res.json();
  }
};

export class TelemetryWebSocket {
  private ws: WebSocket | null = null;
  private onMessageCallback: (data: any) => void;
  private onStatusChange: (connected: boolean) => void;
  private reconnectTimer: any = null;

  constructor(
    onMessage: (data: any) => void,
    onStatusChange: (connected: boolean) => void
  ) {
    this.onMessageCallback = onMessage;
    this.onStatusChange = onStatusChange;
  }

  connect() {
    try {
      this.ws = new WebSocket(WS_BASE);

      this.ws.onopen = () => {
        this.onStatusChange(true);
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.onMessageCallback(parsed);
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      this.ws.onclose = () => {
        this.onStatusChange(false);
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.onStatusChange(false);
        if (this.ws) this.ws.close();
      };
    } catch (e) {
      this.onStatusChange(false);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (!this.reconnectTimer) {
      this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null;
        this.connect();
      }, 3000);
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
    }
  }
}

