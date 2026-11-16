#  StarHealers — Autonomous Crew Medical Officer for Deep-Space Missions

[![Git Branch](https://img.shields.io/badge/branch-Suba-00F0FF?style=for-the-badge&logo=git)](https://github.com/Matthew-10-Jasper/StarHealers/tree/Suba)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Tailwind%20%7C%20Recharts-3B82F6?style=for-the-badge&logo=react)](https://github.com/Matthew-10-Jasper/StarHealers)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.9%20%7C%20SQLite-EF4444?style=for-the-badge&logo=fastapi)](https://github.com/Matthew-10-Jasper/StarHealers)
[![Design System](https://img.shields.io/badge/Design%20System-Dark%20Space%20%7C%2070--20--10-10B981?style=for-the-badge)](https://github.com/Matthew-10-Jasper/StarHealers)

**StarHealers** is an autonomous onboard clinical decision-support and physiological monitoring platform designed for long-duration deep-space exploration (Mars transit and lunar outposts). Because communications with Earth experience round-trip delays between 4 and 24 minutes, StarHealers operates completely offline, processing multi-channel telemetry, correlating physiological strain with anatomical systems, and executing transparent rule-based medical triage.

---

## 🛰️ Module Ownership & Architecture

This repository branch (`Suba`) houses the complete full-stack implementation of the **three foundational assigned modules**, built with clean, decoupled integration interfaces for teammate-owned features.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    STARHEALERS ARCHITECTURE                                 │
├──────────────────────────────────────────────────────────┬──────────────────────────────────┤
│             ASSIGNED MODULES (OWNED BY SUBA)             │   TEAMMATE FEATURES (MATTHEW)    │
├──────────────────────────────────────────────────────────┼──────────────────────────────────┤
│ Module 1: Astronaut Health Monitoring (Core Vitals)      │ Palette 1: Webcam rPPG           │
│   • 9 physiological parameters & Recharts historical UI  │ Palette 3: Z-Score Anomaly Dock  │
│   • Persistent SQLite storage & live telemetry streamer  │ Palette 5: Explainable AI Advisor│
│ Module 2: Interactive Holographic Body Map               │ Palette 6: Circadian & PVT Test  │
│   • Vector SVG anatomical model (Anterior & Posterior)   │ Palette 7: Environmental ECLSS   │
│   • Direct subsystem-to-biometric evidence correlation   │                                  │
│ Module 3: Intelligent Health Triage Engine               │                                  │
│   • Multi-signal compound rule evaluations               │                                  │
│   • Transparent evidence reasoning & NASA flight rules   │                                  │
└──────────────────────────────────────────────────────────┴──────────────────────────────────┘
```

---

##  Mandatory Design System & Seven-Module Color Palettes

The user interface follows a strict **Mission Control / Dark-Space** aesthetic based on the **70–20–10 rule** (70% dark surfaces, 20% primary module identity, 10% accent glow).

### Global Canvas Colors
* **Canvas Background:** `#060913`
* **Card Surfaces:** `#0F172A`
* **Inactive Borders:** `#1E293B`
* **Primary Text:** `#F8FAFC`

### Exact Team Color Palettes
| Palette | Module Focus | Primary Color | Secondary Accent | Owner |
|---|---|---|---|---|
| **Palette 1** | Webcam rPPG & Contactless Pulse | Bio-Rose `#F43F5E` | Soft Coral `#FB7185` | Teammate (Matthew) |
| **Palette 2** | **Core Vitals & Telemetry (Module 1)** | **Medical Cyan `#00F0FF`** | **Deep Electric Blue `#3B82F6`** | **Suba (Assigned)** |
| **Palette 3** | Enhanced Statistical Anomaly Engine | Telemetry Violet `#8B5CF6` | Orchid Pink `#D946EF` | Teammate (Matthew) |
| **Palette 4** | **Rule-Based Alert & Triage (Module 3)** | **Critical Crimson `#EF4444`** | **Solar Amber `#F59E0B`** | **Suba (Assigned)** |
| **Palette 5** | Explainable AI Clinical Advisor | Emerald Mint `#10B981` | Teal Aqua `#14B8A6` | Teammate |
| **Palette 6** | Circadian, Fatigue & Stress (PVT) | Nebula Indigo `#6366F1` | Sky Periwinkle `#38BDF8` | Teammate |
| **Palette 7** | Space Environment & Radiation | Solar Gold `#EAB308` | Warm Burnt Orange `#F97316` | Shared Feature |

### Health Severity Standard (Universal Invariant)
Module colors never alter clinical severity meanings:
* **GREEN (`#22C55E`):** Normal monitoring status.
* **AMBER (`#F59E0B`):** Warning advisory / closer monitoring required.
* **RED (`#EF4444`):** Critical incident requiring flight rule escalation.
* **GREY (`#64748B`):** Missing or unavailable sensor node (never defaulted to zero).

---

## 🔬 Monitored Physiological Parameters (Module 1)

Every telemetry packet stores mandatory source provenance (`SIMULATED`, `RESEARCH DATASET`, `CONNECTED SENSOR`, `MANUAL INPUT`) and data quality status:

| Parameter | Unit | Nominal Baseline | Warning Threshold | Associated Organ System |
|---|---|---|---|---|
| **Heart Rate** | bpm | 60 – 100 bpm | > 90 bpm / < 50 bpm | Cardiovascular (Heart) |
| **HRV (RMSSD)** | ms | 45 – 110 ms | < 40 ms (Vagal tone drop) | Cardiovascular (Heart) |
| **Blood Pressure** | mmHg | 90–130 / 60–85 | > 130/85 mmHg | Cardiovascular (Heart) |
| **SpO2** | % | 95 – 100% | < 94% (Critical: < 92%) | Respiratory (Lungs) |
| **Skin / Core Temp** | °C | 36.1 – 37.3 °C | > 37.5 °C | Metabolic System |
| **Blood Glucose** | mg/dL | 70 – 120 mg/dL | > 140 / < 60 mg/dL | Metabolic System |
| **Sleep Duration** | hrs | 7.0 – 9.0 hrs | < 5.5 hrs | Brain and Eyes |
| **Hydration Level** | % | 55 – 68% | < 52% | Metabolic System |
| **Stress Index** | pts | 0 – 35 pts | > 65 pts | Brain and Eyes |

---

##  Interactive Human Body Map (Module 2)

* **Holographic Medical Vector Silhouette:** Custom SVG vector geometry rendering anatomical contours, internal vertebral spinal column, ribcage, and bio-nodes.
* **Anterior & Posterior Views:** Instant toggle between front and back views.
* **6 Clickable Systems:**
  1. *Brain and Eyes:* Sleep debt, ocular fluid shift markers, stress tone.
  2. *Cardiovascular (Heart):* Pulsating cardiac silhouette, chronotropic rate, HRV parasympathetic reserve, hemodynamics.
  3. *Respiratory (Lungs):* Bronchial lobes, arterial SpO2, habitat CO2 scrubbing compensation.
  4. *Metabolic & Renal:* Glycemic equilibrium, bioimpedance hydration, core thermoregulation.
  5. *Musculoskeletal:* Deep-tissue strain, microgravity deconditioning, exercise countermeasure logs.
  6. *Immune & Hematologic:* Inflammatory markers, latent viral reactivation risk, cosmic radiation susceptibility.
* **Evidence-Based Medical Disclaimer:** Explicit notice that anatomical associations provide situational awareness and do not replace diagnostic imaging scans.

---

##  Intelligent Health Triage Engine (Module 3)

The triage engine evaluates single-signal thresholds and multi-signal compound patterns:
* **Multi-Signal Autonomic Fatigue Compound Pattern:** Correlates elevated resting HR (> 90 bpm), suppressed vagal HRV (< 40 ms), chronic sleep truncation (< 5.5 hrs), and elevated stress index (> 65 pts).
* **Acute Hypoxic Respiratory Depletion:** Detects SpO2 < 92% accompanied by compensatory tachycardia (> 105 bpm).
* **Explainable Alerts:** Every alert outputs the exact triggering criteria, a breakdown of contributing measurements (value vs threshold), medical rationale, and recommended NASA escalation actions.
* **Alert Resolution:** Medical officers can acknowledge and resolve active incidents with an immutable audit stamp.

---

##  Project Structure

```
StarHealers/
├── README.md                      # Complete system documentation
├── TEAM_INTEGRATION.md            # Decoupled integration guide for teammate features
├── .gitignore                     # Git ignore for node_modules, build dist, pycache, .db
│
├── frontend/                      # React + Vite Frontend
│   ├── index.html                 # App entry point with Space Medical typography
│   ├── package.json
│   ├── tailwind.config.js         # Exact team palette tokens and glassmorphic classes
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx                # Cockpit coordinator, live streamer & view routing
│       ├── index.css              # Custom styling, scrollbars & radar scanlines
│       ├── data/
│       │   └── mockData.js        # NASA Mars bio-baseline models & scenario injectors
│       ├── services/
│       │   └── api.js             # REST API service client with offline fallback
│       ├── components/
│       │   ├── common/            # Shared UI (Navbar, Sidebar, MetricCard, SeverityBadge, Modal)
│       │   ├── modules/
│       │   │   ├── Module1Vitals/ # VitalsDashboard, VitalsChart, MetricDetailModal
│       │   │   ├── Module2BodyMap/# BodyMapViewer, BodyAnatomySvg, RegionDetailPanel
│       │   │   └── Module3Triage/ # TriageDashboard, AlertDetailModal, RuleConfigModal
│       │   └── views/             # AstronautDashboard, MissionOverview, CrewManagement, etc.
│
└── backend/                       # FastAPI + Python Backend
    ├── main.py                    # Application entry point with CORS & exception handlers
    ├── database.py                # SQLite connection manager with strict foreign keys
    ├── schemas.py                 # Pydantic validation schemas
    ├── crud.py                    # Database data access layer
    ├── rules_engine.py            # Module 3 clinical decision support rule engine
    ├── seed_data.py               # Database seeder (Missions, Astronauts, Readings, Alerts)
    ├── test_db.py                 # SQLite integrity test suite (8/8 passed)
    ├── test_rules.py              # Rule engine 5-scenario verification test suite (5/5 passed)
    ├── test_api.py                # FastAPI REST endpoint test suite (7/7 passed)
    └── routers/
        ├── missions.py            # Mission & ECLSS habitat environmental endpoints
        ├── astronauts.py          # Crew profiles & physiological baselines
        ├── health.py              # Module 1 latest vitals & historical time-series
        ├── bodymap.py             # Module 2 anatomical subsystem endpoints
        └── triage.py              # Module 3 alert history & rule evaluation
```

---

##  Quick Start & Execution Guide

### Prerequisites
* **Node.js:** v18+ (verified on v26.7.0)
* **Python:** 3.9+ with `fastapi`, `uvicorn`, `pydantic`, `numpy` installed

### 1. Run Backend Server (FastAPI + SQLite)
```powershell
cd C:\Users\ssuba\.gemini\antigravity\scratch\StarHealers\backend

# Run FastAPI with live reload on port 8000
& "C:\Users\ssuba\AppData\Local\Programs\Python\Python39\python.exe" -m uvicorn main:app --reload --port 8000
```
* **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc API Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Run Frontend Development Server (React + Vite)
```powershell
cd C:\Users\ssuba\.gemini\antigravity\scratch\StarHealers\frontend

# Start Vite dev server on port 5173
npm run dev
```
Open your browser at **[http://localhost:5173](http://localhost:5173)**.

---

##  Automated Test Suite Execution

All test suites can be executed inside the terminal:

```powershell
# 1. Run SQLite Database Integrity Tests (8/8 Tests)
& "C:\Users\ssuba\AppData\Local\Programs\Python\Python39\python.exe" backend/test_db.py

# 2. Run Module 3 Rule Engine 5-Scenario Tests (5/5 Scenarios)
& "C:\Users\ssuba\AppData\Local\Programs\Python\Python39\python.exe" backend/test_rules.py

# 3. Run FastAPI REST Endpoint Verification Tests (7/7 Suites)
& "C:\Users\ssuba\AppData\Local\Programs\Python\Python39\python.exe" -u backend/test_api.py

# 4. Verify Frontend Production Build
cd frontend && npm run build
```

---

##  NASA Hackathon Demonstration Walkthrough

1. **Mission Selection:** Switch from *Mars Transit (Ares V)* to *Lunar Outpost* in the header. Observe communications delay update from 14 minutes to 1.3 seconds.
2. **Crew Telemetry Switching:**
   * Select **Dr. Sarah Chen (`ASTRO-01`):** Observe Warning state, elevated HR (94 bpm), depressed HRV (34 ms), and amber brain/heart indicators.
   * Select **Cmdr. Marcus Vance (`ASTRO-02`):** Observe all biometrics and body systems in Green Normal state.
   * Select **Dr. Elena Rostova (`ASTRO-03`):** Observe Critical state with SpO2 drop (90%), heart rate spike (112 bpm), and red pulsating lung/heart regions.
   * Select **Alex Tanaka (`ASTRO-04`):** Observe sensor link loss gracefully rendered in Grey `NO DATA` (never converted to 0).
3. **Module 1 (Vitals):** Click any vital metric card (e.g. Heart Rate) to open the telemetry deep-dive modal showing reference ranges and 24h trends. Change time ranges from 1h to 24h to 7d.
4. **Module 2 (Interactive Body Map):** Toggle between Anterior and Posterior views. Click on the Heart or Lungs to inspect associated biometrics, active alerts, and non-diagnostic disclaimers.
5. **Module 3 (Triage Engine):** Open Health Triage. Click on the *Multi-Signal Autonomic Fatigue* alert to inspect contributing measurements and recommended escalation actions. Click *Mark as Acknowledged / Resolved*.
6. **Scenario Injector:** Use the live demonstration injector in Module 1 to test immediate system responses to *Nominal*, *Fatigue Spike*, *Acute Hypoxia*, or *Sensor Loss*.

---

##  Medical Safety & Regulatory Disclaimers

StarHealers is an autonomous decision-support prototype developed for spaceflight demonstration purposes. All physiological reference ranges, threshold triggers, and countermeasure guidelines must be clinically validated against authoritative aerospace medical literature (e.g., NASA Human Research Program, ESA Space Medicine Office) before flight deployment. StarHealers assists crew medical officers; it does not replace certified clinical judgment.
