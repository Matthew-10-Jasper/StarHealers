# STARHEALERS — MODULE 4: API SPECIFICATION
## Comprehensive REST & WebSocket Endpoints Reference

All Module 4 endpoints are independent of Modules 1–3 and run locally on `http://localhost:8004`.

---

### 1. System Health & Readiness
- **Endpoint**: `GET /health`
- **Description**: Returns the readiness and operational status of Module 4.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "MODULE 4 - ADAPTIVE MISSION CONTEXT MANAGER",
  "version": "1.0.0",
  "database": "CONNECTED",
  "mode": "STANDALONE_INDEPENDENT",
  "timestamp": "2026-11-15T12:00:00Z"
}
```

---

### 2. Mission Profile Catalog
- **Endpoint**: `GET /missions`
- **Description**: Lists all registered mission configuration templates (ISS, Moon, Mars).
- **Response**: Array of `MissionProfile` objects.

- **Endpoint**: `GET /missions/{mission_id}`
- **Description**: Retrieves full specification for a specific mission configuration.

- **Endpoint**: `POST /missions/select`
- **Description**: Switches the active mission profile while preserving historical audit continuity.
- **Request Body**:
```json
{
  "mission_id": "ARTEMIS_BASECAMP_LUNAR",
  "operator_id": "FLIGHT_DIRECTOR",
  "preserve_previous_observations": true
}
```

---

### 3. Active Mission Context & Deviations
- **Endpoint**: `GET /missions/current`
- **Description**: Returns the active planned profile, verified actual environment, deviations, and operational state.

- **Endpoint**: `GET /missions/current/deviations`
- **Description**: Lists all active detected discrepancies between planned baseline and verified actual conditions.

- **Endpoint**: `POST /missions/observations`
- **Description**: Ingests sensor readings, validates physical units and staleness, rejects contradictory data, and updates environmental status.
- **Request Body**:
```json
{
  "observations": [
    {
      "parameter": "CABIN_PRESSURE",
      "value": 70.3,
      "unit": "kPa",
      "source": "SIMULATED"
    },
    {
      "parameter": "CO2_CONCENTRATION",
      "value": 1.4,
      "unit": "mmHg",
      "source": "SIMULATED"
    }
  ]
}
```

---

### 4. Operational State Transitions
- **Endpoint**: `POST /missions/transition`
- **Description**: Requests a controlled transition across the 5 operational states (`NOMINAL`, `DEGRADED`, `CONTINGENCY`, `UNKNOWN`, `RECOVERY`).
- **Validation Rules**: Direct jumps from `CONTINGENCY` to `NOMINAL` are rejected. Transition to `NOMINAL` requires verified evidence.
- **Request Body**:
```json
{
  "target_state": "DEGRADED",
  "reason": "Scrubber bed 2 elevated flow resistance",
  "evidence": { "sensor": "CDRA-DELTA-P", "val": 3.8 }
}
```

---

### 5. Context Reconfiguration
- **Endpoint**: `POST /missions/context/update`
- **Description**: Atomically updates context attributes (e.g. flight phase or gravity environment) while preserving astronaut historical records and incrementing context version.
- **Request Body**:
```json
{
  "actual_mission_phase": "OFF_NOMINAL_ABORT_TRAJECTORY",
  "reason": "Engine burn deviation detected",
  "evidence": { "delta_v_divergence": -4.2 }
}
```

---

### 6. Audit History & Hazards
- **Endpoint**: `GET /missions/history`
- **Description**: Returns chronological audit trail and state transitions persisted in SQLite. Survives backend restarts.

- **Endpoint**: `GET /missions/{mission_id}/hazards`
- **Description**: Lists active environmental hazards, nominal parameter thresholds, and active deviations.

---

### 7. Future Integration Contracts
- **Endpoint**: `GET /integrations/contract`
- **Description**: Returns the standardized JSON contract (`STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT`) for downstream consumption.

- **Endpoint**: `POST /integrations/deliver/{target_module}`
- **Description**: Simulates dispatch to mock adapters for Modules 1, 3, or 5.

---

### 8. Development Simulator
- **Endpoint**: `POST /simulator/scenario?scenario={SCENARIO}`
- **Supported Scenarios**: `COMM_LOSS`, `LIFE_SUPPORT`, `CABIN_DEPRESSURIZATION`, `RADIATION_SPIKE`, `RESTORE_NOMINAL`.
- **Notice**: All injected data is labeled `SIMULATED`.

- **Endpoint**: `POST /simulator/generate-stream`
- **Description**: Emits a batch of nominal synthetic telemetry for testing.

---

### 9. Real-Time WebSocket Telemetry
- **Endpoint**: `ws://localhost:8004/ws/telemetry`
- **Protocol**: JSON-encoded event streams:
  - `INITIAL_STATE`: Sent upon successful connection.
  - `TELEMETRY_UPDATED`: Broadcast when sensor observations are ingested.
  - `STATE_TRANSITION`: Broadcast when operational state changes.
  - `CONTEXT_RECONFIGURED`: Broadcast when context attributes update.

