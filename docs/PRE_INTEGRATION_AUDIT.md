# STARHEALERS UNIFIED PLATFORM — PRE-INTEGRATION AUDIT (PHASE 0)

Date: 2026-11-15  
Status: COMPLETE  

---

## 1. Inventory of Existing Codebases & Locations

### Modules 1–3: Astronaut Health, Anatomical Body Map & Clinical Triage
- **Source of Record**: `E:\Users\HP\Downloads\StarHealers-Suba\StarHealers-Suba` (Untouched, read-only outside workspace)
- **Integration Copy in Workspace**: `E:\StarHealers\StarHealers-Suba`
- **Owner**: Teammate Suba (Strictly preserved; no logic changes or file overwrites)
- **Backend Stack**: Python 3.13, FastAPI, SQLite (`starhealers.db`), Pydantic, pure Python clinical rule engine.
- **Frontend Stack**: React 19 / Vite, Tailwind CSS, Lucide React, Recharts.
- **Database**: `starhealers.db` (4 astronauts, 36 health readings, 48 telemetry points, 3 missions, 3 triage alerts, 1 user).
- **Backend Baseline Test Status**:
  - `test_db.py`: 8 / 8 tests PASSED (100%)
  - `test_rules.py`: 5 / 5 clinical triage scenarios PASSED (100%)
  - API endpoint testing verified.

### Module 4: Mission Environment Intelligence & Adaptive Context
- **Location**: `E:\StarHealers\module4_mission_intelligence`
- **Owner**: Mission Environment Intelligence Team
- **Backend Stack**: Python, FastAPI, SQLite (`starhealers_m4.db`), SQLAlchemy, Pydantic V2, Scientific Units.
- **Frontend Stack**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, ECharts, Lucide React.
- **Database**: `starhealers_m4.db` (Mission profiles, deviations, environmental observations, state transitions, audit log).
- **Baseline Test Status**: 12 / 12 backend API & persistence tests PASSED (100%).

### Module 5: Space Hazard Simulation Engine
- **Location**: `E:\StarHealers\module5_hazard_simulation`
- **Owner**: Space Hazard Simulation Subsystem
- **Backend Stack**: Python, FastAPI, SQLite (`starhealers_m5.db`), SQLAlchemy, NumPy / SciPy numerical integrators.
- **Core Engines**:
  - Radiation Engine: GCR background exposure & Solar Particle Event (SPE) Weibull spike dynamics.
  - CO2 Accumulation Engine: Dual-bed scrubber efficiency and metabolic balance.
  - Sleep & Homeostasis Engine: 2-process circadian sleep debt modeling.
  - Combined Simulation Controller: Multi-hazard scenario runner and Module 4 dispatcher.
- **Baseline Test Status**: 17 / 17 engine & controller tests PASSED (100%).

### Module 6: Circadian, Fatigue & Psychomotor Stress
- **Location**: `E:\StarHealers\module6_circadian_fatigue`
- **Database**: `starhealers_m6.db`
- **Visual Palette**: Nebula Indigo (`#6366F1`) & Sky Periwinkle (`#38BDF8`)
- **Core Engines**: Two-process circadian alignment, NumPy vectorized cognitive readiness, 5-trial interactive PVT test battery.
- **Baseline Test Status**: 16 / 16 tests PASSED (100%).

### Module 7: Space Environment, Radiation & Life Support
- **Location**: `E:\StarHealers\module7_environment_radiation`
- **Database**: `starhealers_m7.db`
- **Visual Palette**: Solar Gold (`#EAB308`) & Warm Burnt Orange (`#F97316`)
- **Core Engines**: Composite environmental risk index ($0.40 \text{Rad} + 0.35 \text{CO}_2 + 0.25 \text{Cabin}$), 30-day/career radiation limits, M4 cross-verification, hazard alert triage.
- **Baseline Test Status**: 11 / 11 tests PASSED (100%).

---

## 2. Database Inventory & Preservation Strategy

| Module | Database Path | Tables | Strategy |
| :--- | :--- | :--- | :--- |
| **Modules 1–3** | `StarHealers-Suba/backend/starhealers.db` | `astronauts`, `health_readings`, `historical_telemetry`, `missions`, `triage_alerts`, `users`, `teammate_anomalies_dock` | Preserved as Suba clinical SQLite store; queried directly via Suba DAO/CRUD layer. |
| **Module 4** | `module4_mission_intelligence/backend/starhealers_m4.db` | `mission_state`, `mission_deviations`, `environmental_observations`, `audit_log`, `state_transitions` | Preserved as Mission Context Intelligence store. |
| **Module 5** | `module5_hazard_simulation/backend/starhealers_m5.db` | `simulation_sessions`, `simulation_readings`, `simulation_scenarios` | Preserved as Hazard Simulation history store. |
| **Module 6** | `starhealers_m6.db` | `astronauts`, `pvt_sessions`, `pvt_trials`, `readiness_records`, `stress_records` | Preserved as Circadian & Psychomotor store. |
| **Module 7** | `starhealers_m7.db` | `hazard_alerts`, `environmental_snapshots` | Preserved as Space Environment & Hazard Alert store. |

**Safety Rule**: No destructive migrations or table mergers. The unified backend provides unified access to these modules while preserving their dedicated schemas and historical integrity.

---

## 3. Port & Service Topology Consolidation Plan

- **Current Decentralized Setup**:
  - Module 1–3 Backend: `8001`
  - Module 4 Backend: `8004`
  - Module 5 Backend: `8005`
  - Module 6 Backend: `8006`
  - Module 7 Backend: `8007`
  - Multiple frontend dev servers.
- **Consolidated Target**:
  - **ONE Unified FastAPI Backend**: `http://127.0.0.1:8000` (serving `/`, `/health`, `/api/v1/...`, and backward-compatible module routes).
  - **ONE Unified React/Vite Frontend**: `http://localhost:5173` (hosting unified navigation across all 7 modules + Mission Overview).

---

## 4. Cross-Module Data-Flow Dependencies

```text
[Module 1: Vitals] ───────> [Module 3: Triage Alerts] ───────> [Module 6: Fatigue & Stress]
        │                                                               ▲
        ▼                                                               │ (Sleep Debt)
[Module 2: Body Map]                                                    │
                                                                        │
[Module 4: Mission Context] ──> [Module 5: Hazard Simulation] ──────────┘
        │                               │
        │                               ▼ (Radiation, CO2)
        └─────────────────────────> [Module 7: Environment & Radiation]
                                                │
                                                ▼
                                    [Unified Mission Overview]
```
