# STARHEALERS — MODULE 4: MISSION ENVIRONMENT INTELLIGENCE & ADAPTIVE MISSION CONTEXT MANAGER
### Autonomous Astronaut Health-Support and Deep-Space Mission Monitoring Platform

---

## 1. System Overview

**Module 4** provides autonomous mission environment intelligence and adaptive mission context management for deep-space exploration platforms. 

Because other Starhealers modules (Module 1: Astronaut Health Monitoring, Module 2: Human Body-Map Interface, Module 3: Clinical Triage Engine) are being independently built by teammates, **Module 4 is fully decoupled, independently executable, self-contained, and integration-ready**.

### Core Capabilities
1. **Planned Mission Profile Manager**: High-fidelity templates for **ISS (Low Earth Orbit)**, **Artemis (Moon)**, and **Ares (Mars)** with scientific gravity distinctions ($0g$ microgravity vs $0.166g$ lunar gravity vs $0.376g$ martian gravity).
2. **Actual Environment Manager**: Ingests, validates, and evaluates actual spacecraft sensor telemetry. Detects stale readings ($>300s$), rejects invalid physical units, flags contradictory readings, and keeps missing parameters strictly `UNKNOWN`.
3. **Mission Deviation Detection Engine**: Performs continuous differential analysis between planned flight baseline and verified actual conditions (trajectory phase mismatches, cabin pressure decays, CO2 elevations, radiation flares, ECLSS scrubbers).
4. **Deterministic Contingency State Manager**: Enforces safe transitions across 5 operational states:
   - `NOMINAL`
   - `DEGRADED`
   - `CONTINGENCY`
   - `UNKNOWN`
   - `RECOVERY`
   Transitions back to `NOMINAL` strictly require verified evidence and zero active critical hazards.
5. **Context Reconfiguration Engine**: Atomically updates affected attributes, increments context version, logs operator rationale and evidence, while preserving historical astronaut health continuity.
6. **Mission Constraints & Local-First Autonomy**: Manages deep space latency (e.g. $1200s$ Mars latency) and enforces the local-first reporting pipeline (`LOCALLY_GENERATED` $\rightarrow$ `QUEUED` $\rightarrow$ `TRANSMITTED` $\rightarrow$ `ACKNOWLEDGED`).
7. **Context History & Audit Ledger**: Immutable SQLite transaction persistence that survives crashes and application restarts.
8. **Standardized Context Distribution (`v1.0.0`)**: Emits `STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT` for seamless downstream consumption.

---

## 2. Technology Stack & Phase 2 Upgrades

- **Backend**: Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite (batch mode with foreign keys), Pytest.
- **Scientific Units Engine**: **Pint** with custom aerospace dimensional constraints, canonical unit conversions, and mathematical enforcement of the distinction between Absorbed Dose (Gy) and Equivalent Dose (Sv).
- **Database Versioning**: **Alembic** with SQLite batch migrations (`001_baseline`, `002_units_idempotency`).
- **Property-Based Testing**: **Hypothesis** invariant fuzzing across operational state graphs and physical dimensional conversions.
- **Layered Anomaly Engine**: **SciPy & Scikit-Learn** combining hardware limits, aerospace physics, rolling Z-scores, and explainable unsupervised Isolation Forest ML.
- **Frontend**: React 18, Vite 6, TypeScript, Tailwind CSS, **Apache ECharts** (multi-axis high-density telemetry with `dataZoom`), **Recharts**, **TanStack Query**, **Zod** (runtime contract validation), Lucide React.
- **Communication**: REST API + bi-directional WebSockets (`/ws/telemetry`).
- **Data Source**: Clearly labeled `SIMULATED` synthetic development telemetry.

---

## 3. Visual Design System

- **Background**: `#060913` (Deep Space Dark)
- **Card Surface**: `#0F172A` (Slate Surface)
- **Border**: `#1E293B`
- **Primary Text**: `#F8FAFC`
- **Primary Accent — Critical Crimson**: `#EF4444` (Critical deviations, emergency alerts, active contingency borders)
- **Secondary Accent — Solar Amber**: `#F59E0B` (Warnings, degraded status, attention-required indicators)
- **Visual Balance**: 70% Dark Surfaces, 20% Structural Cards, 10% Accents.

---

## 4. Project Directory Structure

```
module4_mission_intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & CORS
│   │   ├── api/
│   │   │   └── endpoints.py         # Complete REST & WebSocket route handlers
│   │   ├── core/
│   │   │   ├── config.py            # Settings, threshold bounds, and paths
│   │   │   └── events.py            # WebSocket pub/sub connection manager
│   │   ├── database/
│   │   │   └── session.py           # SQLite engine, sessions, foreign key pragma
│   │   ├── models/
│   │   │   └── entities.py          # SQLAlchemy ORM entities (Audit, Deviations, States)
│   │   ├── schemas/
│   │   │   ├── enums.py             # OperationalState, QualityStatus, CommStatus, etc.
│   │   │   ├── mission_profile.py   # Pydantic schemas for mission configuration
│   │   │   ├── observation.py       # EnvironmentalObservation and batch ingestion
│   │   │   ├── deviation.py         # MissionDeviation and severity classification
│   │   │   ├── context.py           # Planned, Actual, and Response schemas
│   │   │   └── history.py           # AuditEvent, StateTransitionRecord, QueuedReport
│   │   ├── services/
│   │   │   ├── profile_manager.py   # Component A: Profile configuration loader
│   │   │   ├── environment_manager.py# Component B: Actual environment & quality evaluator
│   │   │   ├── deviation_engine.py  # Component C: Differential deviation detector
│   │   │   ├── contingency_manager.py# Component D: 5-state safety transition engine
│   │   │   ├── reconfiguration_engine.py# Component E: Atomic versioned context updater
│   │   │   ├── constraints_manager.py# Component F: Comm delay & local-first pipeline
│   │   │   ├── history_manager.py   # Component G: Persistent SQLite audit ledger
│   │   │   └── simulator.py         # Component H: Development telemetry simulator
│   │   ├── repositories/
│   │   │   └── mission_repository.py# Database repository with transaction safety
│   │   └── integrations/
│   │       ├── contracts.py         # Canonical JSON distribution contract generator
│   │       ├── adapters.py          # Abstract adapter interfaces for downstream modules
│   │       └── mock_consumers.py    # Mock adapters for Modules 1, 3, and 5
│   ├── tests/
│   │   ├── test_mission_intelligence.py # 28 Pytest tests covering all components & APIs
│   │   └── run_tests.py             # Standalone 12-stage integration test runner
│   └── requirements.txt             # Python backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx           # Mission MET timer, state pill, WS indicator
│   │   │   ├── MissionOverview.tsx  # Section A: Mission parameters & trajectory phase
│   │   │   ├── PlannedVsActual.tsx  # Section B: Side-by-side differential matrix
│   │   │   ├── OperationalStatePanel.tsx # Section C: 5-State contingency transition tool
│   │   │   ├── DeviationMonitor.tsx # Section D: Active deviations list with evidence
│   │   │   ├── EnvironmentMonitor.tsx# Section E: Telemetry cards & Recharts graphs
│   │   │   ├── CommunicationMonitor.tsx # Section F: Latency, reachability, local-first queue
│   │   │   ├── MissionTimeline.tsx  # Section G: Persistent SQLite chronological audit
│   │   │   ├── ProfileSelector.tsx  # Section H: Template switcher (ISS, Moon, Mars)
│   │   │   ├── SimulatorControls.tsx# Section I: Synthetic failure injectors
│   │   │   └── IntegrationInspector.tsx # Section J: Real-time contract JSON inspector
│   │   ├── services/
│   │   │   └── api.ts               # REST API client & WebSocket client with auto-reconnect
│   │   ├── types/
│   │   │   └── mission.ts           # TypeScript interfaces matching backend models
│   │   ├── styles/
│   │   │   └── index.css            # Tailwind directives and space scrollbars
│   │   ├── App.tsx                  # Master responsive mission dashboard
│   │   └── main.tsx                 # React DOM mount point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── mission_profiles/
│   ├── iss.json                     # ISS / Low Earth Orbit configuration template
│   ├── moon.json                    # Artemis Basecamp lunar surface configuration template
│   └── mars.json                    # Ares Voyager deep-space Mars transit template
│
├── integration_contracts/
│   ├── mission_context_v1.json      # Sample distribution contract payload
│   └── mission_context_v1_schema.json # JSON Schema (Draft-07) definition
│
├── docs/
│   ├── architecture.md              # Detailed architecture, state graphs, data flow
│   ├── api_documentation.md         # Full endpoint catalog, request/response models
│   ├── integration_guide.md         # Contract consumption guide for Modules 1, 2, 3, 5, 6, 7
│   └── failure_handling.md          # Fault tolerance, staleness, and blackout handling
│
└── README.md
```

---

## 5. Quick Start & Execution Guide (Windows PowerShell)

Open two Windows PowerShell terminal tabs:

### Terminal 1: Backend Service
```powershell
# Navigate to backend directory
cd E:\StarHealers\module4_mission_intelligence\backend

# Install python dependencies (if needed)
pip install -r requirements.txt

# Start FastAPI backend server on port 8004
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```
Backend API will be accessible at:
- **API URL**: `http://localhost:8004`
- **Interactive Swagger Docs**: `http://localhost:8004/docs`
- **Health Check**: `http://localhost:8004/health`
- **WebSocket Stream**: `ws://localhost:8004/ws/telemetry`

---

### Terminal 2: Frontend Mission Control Dashboard
```powershell
# Navigate to frontend directory
cd E:\StarHealers\module4_mission_intelligence\frontend

# Start Vite development server
npm run dev
```
Frontend Mission Control Dashboard will be live at:
- `http://localhost:5173`

---

## 6. Automated Testing & Verification

### Run Complete Pytest Suites (47 Tests Across 4 Suites)
```powershell
cd E:\StarHealers\module4_mission_intelligence\backend
# Runs core tests, scientific unit tests, and anomaly tests
python -m pytest tests/test_mission_intelligence.py tests/test_scientific_units.py tests/test_anomaly_detector.py -p no:anyio -v

# Runs Hypothesis property-based fuzz tests
python -m pytest tests/test_properties.py -p no:anyio -v
```
**Expected Result**: `47 passed (100% SUCCESS)`.

### Run Standalone Integration Test Script (12 Stages)
```powershell
cd E:\StarHealers\module4_mission_intelligence\backend
python tests\run_tests.py
```
**Expected Result**: `ALL 12 BACKEND API & PERSISTENCE TESTS PASSED SUCCESSFULLY!`.

### Run Alembic Database Migrations Check
```powershell
cd E:\StarHealers\module4_mission_intelligence\backend
python -m alembic current
```
**Expected Result**: `002_units_idempotency (head)`.

### Run Frontend Production Build & TypeScript Verification
```powershell
cd E:\StarHealers\module4_mission_intelligence\frontend
npm run build
```
**Expected Result**: `✓ built in ~2m` (Zero TypeScript errors, complete production bundle in `dist/`).

---

## 7. Technical Documentation Index

Detailed engineering documentation is available in the `docs/` directory:
- [Phase 2 Technical Audit Report](docs/phase2_technical_audit.md): Baseline verification, defects resolved, and technology evaluation.
- [Phase 2 Upgrade Completion Report](docs/phase2_upgrade_report.md): Full engineering summary of all Phase 2 upgrades.
- [Database Migration Guide](docs/database_migrations.md): Alembic batch migrations and SQLite integrity rules.
- [Frontend-Backend Contracts](docs/frontend_backend_contracts.md): OpenAPI 3.1 specification, Zod runtime validation, and envelope structures.
- [Scientific Validation Guide](docs/scientific_validation.md): Deep-space physical telemetry, Gy vs Sv dimensional rules, and gravity modeling.
- [Testing Strategy Guide](docs/testing_strategy.md): Test taxonomy, property-based testing, and verification procedures.

---

## 7. Development Telemetry Simulator Guide

The dashboard includes a dedicated **Section I • Development Telemetry Simulator**:
1. **Nominal Stream**: Emits baseline sensor readings for the active destination.
2. **ECLSS Degradation**: Injects CO2 scrubber bed degradation, elevating CO2 partial pressure to $4.6\text{ mmHg}$ and triggering a `WARNING`.
3. **Comm Blackout**: Simulates Deep Space Network high-gain antenna failure, entering `COMMUNICATION_BLACKOUT` and activating local-first autonomy constraints.
4. **SPE Radiation Flare**: Injects a Solar Particle Event with dose rate rising to $4.8\text{ mSv/day}$, triggering a `CRITICAL` deviation.
5. **Trajectory Abort**: Changes the verified flight phase to `OFF_NOMINAL_ABORT_TRAJECTORY` while preserving baseline flight plan, incrementing context version.
6. **Restore Nominal**: Safely clears simulated hazards and transitions operational state back to `NOMINAL` with verified evidence.

---

## 8. Disclaimer

This system is an engineering simulation developed for the **STARHEALERS** mission architecture project. All telemetry streams are clearly labeled **`SIMULATED`** and do not claim NASA flight qualification or real spacecraft operation.

