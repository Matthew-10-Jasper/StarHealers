# STARHEALERS — CONSOLIDATED UNIFIED PLATFORM
### Integrated Astronaut Health & Spaceflight Monitoring System

STARHEALERS is an integrated mission monitoring and medical decision-support platform for crewed space exploration missions (LEO ISS, Lunar Artemis, and Mars Transit).

It consolidates all seven specialized subsystems into **ONE Unified FastAPI Backend** and **ONE Unified React Frontend** without duplicating physical simulation models or destroying legacy module implementations.

---

## 1. Subsystem Architecture Overview

| Module | Subsystem Name | Focus & Physical Models | Primary Accent |
| :--- | :--- | :--- | :--- |
| **Overview** | **Unified Mission Overview** | Real-time synthesis of all 7 modules, cross-module KPI cards, crew fleet telemetry | `#0EA5E9` (Cyan) |
| **Module 1** | **Continuous Vitals & Biometrics** | Continuous ECG (HR, HRV), SpO2, blood pressure, glucose, temperature, hydration | `#10B981` (Emerald) |
| **Module 2** | **Interactive Body Anatomy Map** | Front/Back 2D/3D organ systems projection with local strain & microgravity compliance | `#A855F7` (Purple) |
| **Module 3** | **Autonomous Clinical Triage** | NASA-STD-3001 automated flight rule evaluation & medical escalation advisor | `#EF4444` (Rose) |
| **Module 4** | **Mission Context & Adaptive States** | Planned vs actual environmental envelopes, operational state machine (NOMINAL/CONTINGENCY) | `#DC2626` (Red) |
| **Module 5** | **Space Hazard Simulation Engine** | GCR/SPE space radiation, cabin CO2 mass balance ODEs, discrete sleep debt kinetics | `#F59E0B` (Amber) |
| **Module 6** | **Circadian Rhythm & Psychomotor Fatigue**| 3-process sleep-wake model, alertness curves, PVT reaction time test battery | `#6366F1` (Indigo) |
| **Module 7** | **Space Environment & Radiation Limits** | Space weather, solar proton events, NASA 30-day/career radiation limits, ECLSS | `#EAB308` (Gold) |
| **Health** | **System Health & Persistence Monitor** | Live ping of all 5 SQLite databases, router status, latency diagnostics | `#14B8A6` (Teal) |

---

## 2. Quick Start: Running the Unified Application

The entire platform runs using just **two terminal commands**:

### Start the Unified Backend (Port 8000)
```powershell
# In PowerShell from workspace root:
cd E:\StarHealers\backend
$env:PYTHONPATH="E:\StarHealers\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative API Spec: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Start the Unified Frontend (Port 5173)
```powershell
# In a second PowerShell window:
cd E:\StarHealers\frontend
npm run dev
```
- Open your browser at: [http://localhost:5173](http://localhost:5173)

---

## 3. Technology Stack

- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLite3, NumPy, SciPy.
- **Frontend**: Vite 6, React 18, TypeScript, TailwindCSS, Recharts, ECharts, Lucide React.
- **Data Persistence**: 5 dedicated SQLite databases (`starhealers.db`, `starhealers_m4.db`, `starhealers_m5.db`, `starhealers_m6.db`, `starhealers_m7.db`).

---

## 4. Documentation Directory

Detailed documentation is available in `docs/`:
- [ARCHITECTURE.md](file:///E:/StarHealers/docs/ARCHITECTURE.md): Modular monolith layout, namespace isolation, and adapter topology.
- [API_CONTRACTS.md](file:///E:/StarHealers/docs/API_CONTRACTS.md): Full listing of `/api/v1/` routes, direct legacy routes, and WebSocket telemetry protocol.
- [INTEGRATION.md](file:///E:/StarHealers/docs/INTEGRATION.md): Cross-module data flows, event bus architecture, and Module 5 → Module 4 hazard adaptation.
- [DATABASE.md](file:///E:/StarHealers/docs/DATABASE.md): Multi-database preservation, row counts audit, and backup restoration strategy.
- [TEST_REPORT.md](file:///E:/StarHealers/docs/TEST_REPORT.md): 78 automated test results across all 7 modules with a 100% pass rate.
- [PRE_INTEGRATION_AUDIT.md](file:///E:/StarHealers/docs/PRE_INTEGRATION_AUDIT.md): Initial repository state and database baseline audit.

---

## 5. Automated Verification

To run the complete automated test suite across all subsystems:

```powershell
# 1. Run Unified Backend Integration Tests (7 tests):
cd E:\StarHealers\backend
$env:PYTHONPATH="E:\StarHealers\backend"
python tests\run_tests.py

# 2. Run Suba Baseline Tests (13 tests):
cd E:\StarHealers\StarHealers-Suba\backend
$env:PYTHONPATH="E:\StarHealers\StarHealers-Suba\backend"
python test_db.py
python test_rules.py

# 3. Run Module 4 Tests (12 tests):
cd E:\StarHealers\module4_mission_intelligence\backend
$env:PYTHONPATH="E:\StarHealers\module4_mission_intelligence\backend"
python tests\run_tests.py

# 4. Run Module 5 Physics Tests (19 tests):
cd E:\StarHealers\module5_hazard_simulation\backend
$env:PYTHONPATH="E:\StarHealers\module5_hazard_simulation\backend"
python -m pytest tests/test_radiation_engine.py tests/test_co2_engine.py tests/test_sleep_engine.py tests/test_simulation_controller.py tests/test_scenarios.py tests/test_module4_integration.py

# 5. Run Module 6 Circadian Tests (16 tests):
cd E:\StarHealers\module6_circadian_fatigue\backend
$env:PYTHONPATH="E:\StarHealers\module6_circadian_fatigue\backend"
python -m pytest tests

# 6. Run Module 7 Space Environment Tests (11 tests):
cd E:\StarHealers\module7_environment_radiation\backend
$env:PYTHONPATH="E:\StarHealers\module7_environment_radiation\backend"
python -m pytest tests

# 7. Verify Frontend Production Build:
cd E:\StarHealers\frontend
npm run build
```
Result: **78 / 78 tests passed (100%)** with **0 build errors**.
