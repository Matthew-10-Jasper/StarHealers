# STARHEALERS UNIFIED PLATFORM — CROSS-MODULE INTEGRATION GUIDE

## 1. Cross-Module Communication Architecture

STARHEALERS connects seven specialized modules without tight coupling through three primary integration patterns:
1. **Direct In-Process Integration Adapters**: High-speed, in-memory domain translators located in `backend/app/integrations/adapters/`.
2. **In-Process Pub/Sub Event Bus**: An asynchronous event dispatcher in `backend/app/integrations/event_bus.py` that broadcasts domain events (e.g., `CRITICAL_ALERT_TRIGGERED`, `HAZARD_THRESHOLD_EXCEEDED`, `MISSION_STATE_CHANGED`).
3. **Consolidated Unified API**: REST endpoints under `/api/v1` and WebSocket streams delivering synthesized platform telemetry to the unified frontend.

```
+-----------------------------------------------------------------------------------+
|                           STARHEALERS UNIFIED BACKEND                             |
|                                                                                   |
|  +--------------------+     +--------------------+     +--------------------+     |
|  | Module 1-3 Adapter |     |  Module 4 Adapter  |     |  Module 5 Adapter  |     |
|  +---------+----------+     +---------+----------+     +---------+----------+     |
|            |                          |                          |                |
|            +-------------------> [EVENT BUS] <-------------------+                |
|                                       ^                                           |
|            +--------------------------+--------------------------+                |
|            |                                                     |                |
|  +---------+----------+                               +----------+---------+      |
|  |  Module 6 Adapter  |                               |  Module 7 Adapter  |      |
|  +--------------------+                               +--------------------+      |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                     UNIFIED MISSION OVERVIEW AGGREGATOR                     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Key Data Flow Implementations

### Flow 1: Module 5 Hazard Simulation → Module 4 Context Adaptation
- **Trigger**: Operator advances Module 5 simulation (e.g., Solar Particle Event spike or Scrubber failure) and clicks **Export to Module 4 Context**.
- **Execution**:
  1. `SimulationController` computes cumulative radiation dose, cabin $\text{CO}_2$ concentration, and astronaut sleep deficit.
  2. `POST /simulations/{id}/export-to-module4` generates a normalized payload adhering to the canonical parameter names (`CO2_CONCENTRATION`, `RADIATION_DOSE_RATE`).
  3. Module 4 receives the observation via `ingest_observations` and evaluates planned vs actual envelopes.
  4. If thresholds are breached, Module 4 records an active deviation and triggers an authorized state transition from `NOMINAL` to `DEGRADED` or `CONTINGENCY`.
- **Constraint Compliance**: Module 4 does not perform physical simulations; it strictly consumes Module 5's calculated hazard state.

### Flow 2: Module 1 Biometric Readings → Module 3 Automated Clinical Triage
- **Trigger**: New physiological telemetry is ingested via `POST /api/astronauts/health/readings`.
- **Execution**:
  1. Module 1 stores the multi-signal packet in `starhealers.db`.
  2. The reading is evaluated against Module 3 flight rules (`test_rules.py` rule engine).
  3. If values cross thresholds (e.g., HR > 130 bpm for > 15m, or SpO2 < 90%), a `TriageAlert` is generated with `NASA-STD-3001` clinical protocol recommendations.
  4. The event is broadcast via the event bus to update the Mission Overview and alert badges.

### Flow 3: Module 4 Communication Delay → Autonomy Escalation
- **Trigger**: Mission profile switches to `ARES_VOYAGER_MARS` with a one-way communication latency of 840 seconds (14 minutes).
- **Execution**:
  1. Module 4 updates `communication.one_way_latency_seconds = 840.0`.
  2. Module 3 clinical protocols switch to **Autonomous Execution Mode** because round-trip consultation with Earth Flight Surgeons requires > 28 minutes.
  3. Module 6 shifts cognitive assessment recommendations to autonomous local crew schedules.

### Flow 4: Unified Mission Overview Aggregation
- **Endpoint**: `GET /api/v1/overview`
- **Execution**:
  1. `UnifiedOverviewAggregator` concurrently queries all 5 domain adapters using `asyncio.gather`.
  2. Combines crew health statuses (M1), active deviations (M4), physics simulation state (M5), cognitive readiness index (M6), and space environment alerts (M7).
  3. Returns a single comprehensive JSON payload in < 15ms.
