# STARHEALERS UNIFIED PLATFORM — API CONTRACTS CATALOG

## 1. Unified Versioned Routes (`/api/v1`)

The consolidated FastAPI backend serves the versioned API under prefix `/api/v1`:

### 1.1 Overview & System Telemetry
- `GET /api/v1/overview`: Aggregates real-time summary across all 7 modules, including active crew status, operational state, hazard indexes, circadian fatigue metrics, and active deviations.
- `GET /health`: Comprehensive health audit checking status of all 5 SQLite databases and 7 internal module routers.

### 1.2 Module 1: Astronaut Health & Vitals (Suba)
- `GET /api/v1/module1/api/astronauts`: List all crew members and current status.
- `GET /api/v1/module1/api/astronauts/{id}`: Detailed astronaut profile and baselines.
- `GET /api/v1/module1/api/astronauts/{id}/health`: Latest readings across 9 physiological metrics.
- `GET /api/v1/module1/api/astronauts/{id}/health/history?time_range={1h|24h|7d}`: Historical biometric time series.
- `POST /api/v1/module1/api/astronauts/health/readings`: Ingest newly observed or simulated vitals.

### 1.3 Module 2: Anatomical Body Map (Suba)
- `GET /api/v1/module2/api/astronauts/{id}/body-map`: Overall organ system status map.
- `GET /api/v1/module2/api/astronauts/{id}/body-map/{region_id}`: Detailed regional organ telemetry (heart, brain, lungs, spine, eyes, metabolic).

### 1.4 Module 3: Autonomous Medical Triage (Suba)
- `GET /api/v1/module3/api/alerts`: List active, resolved, or all triage alerts.
- `GET /api/v1/module3/api/astronauts/{id}/alerts`: Triage alerts for specific astronaut.
- `POST /api/v1/module3/api/alerts/{id}/resolve`: Authorize resolution of clinical alert with action note.
- `GET /api/v1/module3/api/triage/rules`: Retrieve active clinical triage rules and flight rule thresholds.
- `POST /api/v1/module3/api/triage/evaluate`: Run flight rule evaluator on incoming telemetry.

### 1.5 Module 4: Mission Environment Intelligence
- `GET /api/v1/module4/missions`: List mission profiles (ISS, Artemis, Ares).
- `GET /api/v1/module4/missions/current`: Retrieve live mission context, phase, operational state, deviations.
- `POST /api/v1/module4/missions/select`: Switch planned mission profile.
- `POST /api/v1/module4/context/state`: Request operational state transition (NOMINAL, DEGRADED, CONTINGENCY, RECOVERY).
- `GET /api/v1/module4/missions/current/deviations`: List active environmental and flight phase deviations.
- `GET /api/v1/module4/missions/history`: Audit trail of flight transitions and evidence events.

### 1.6 Module 5: Space Hazard Simulation Engine
- `GET /api/v1/module5/engines`: List available simulation engines (Radiation, CO2, Sleep, Combined).
- `GET /api/v1/module5/simulations/scenarios`: Retrieve predefined space hazard scenarios.
- `POST /api/v1/module5/engines/radiation/run`: Execute standalone space radiation physical solver.
- `POST /api/v1/module5/engines/co2/run`: Execute cabin CO2 mass balance ODE simulation.
- `POST /api/v1/module5/engines/sleep/run`: Execute discrete sleep deficit/recovery model.
- `POST /api/v1/module5/simulations`: Initialize multi-hazard simulation session.
- `POST /api/v1/module5/simulations/{id}/step`: Advance simulation by one integration timestep.
- `POST /api/v1/module5/simulations/{id}/run-to-end`: Run full mission trajectory simulation.
- `POST /api/v1/module5/simulations/{id}/export-to-module4`: Export simulated hazard trajectory into Module 4.

### 1.7 Module 6: Circadian Rhythm & Psychomotor Fatigue
- `GET /api/v1/module6/astronauts/{id}/circadian`: Circadian rhythm curve and alignment index.
- `GET /api/v1/module6/astronauts/{id}/sleep-status`: 24-hour sleep duration, deficit, and cumulative debt.
- `GET /api/v1/module6/astronauts/{id}/fatigue`: Multi-signal fatigue assessment and score.
- `POST /api/v1/module6/pvt/session`: Submit Psychomotor Vigilance Test results (RT, lapses, false starts).

### 1.8 Module 7: Space Environment & Radiation Limits
- `GET /api/v1/module7/environment/latest`: Space weather readings (solar proton flux, Kp index, SPE alert).
- `GET /api/v1/module7/radiation/astronauts/{id}/dose`: Cumulative radiation dose vs 30-day and career limits.
- `GET /api/v1/module7/life-support/telemetry`: ECLSS environmental life support telemetry.
- `GET /api/v1/module7/alerts`: Space environmental threshold alerts.

---

## 2. Backward-Compatible Direct Routes

For full backward compatibility with existing frontends and scripts, all original routes are mounted directly at root on port `8000`:
- `/api/missions` → Suba mission listing
- `/api/astronauts` → Suba crew listing
- `/api/astronauts/{id}/health` → Suba latest vitals
- `/api/astronauts/{id}/bodymap` → Suba body map
- `/api/alerts` → Suba triage alerts
- `/missions/current` → Module 4 context
- `/missions` → Module 4 profiles
- `/engines` → Module 5 simulation engines
- `/simulations` → Module 5 sessions
- `/astronauts/{id}/circadian` → Module 6 circadian
- `/pvt/session` → Module 6 PVT test
- `/environment/latest` → Module 7 space weather
- `/radiation/astronauts/{id}/dose` → Module 7 radiation

---

## 3. Real-Time WebSocket Interface

- **Endpoint**: `ws://127.0.0.1:8000/ws/telemetry`
- **Protocol**: JSON-encoded events.
  - On Connect: Receives `{"event": "INITIAL_STATE", "context": { ... }}`
  - Ping/Pong: Client sends `{"type": "PING"}`, receives `{"event": "PONG", "timestamp": "..."}`
  - Telemetry Updates: Server broadcasts `{"event": "TELEMETRY_UPDATE", "context": { ... }}` on state transitions and simulator advances.
