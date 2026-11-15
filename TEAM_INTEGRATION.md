#  StarHealers — Team Integration & Architecture Guide

This document defines the interface contracts, database docking tables, and collaborative Git workflow between **Suba** (assigned to Modules 1, 2, and 3) and **Matthew / Teammates** (responsible for Webcam rPPG, Z-score Anomaly Detection, Explainable AI Advisor, and PVT Cognitive Tests).

---

##  Division of Module Ownership

| Module Name | Team Palette | Primary & Secondary Colors | Owner | Tech Stack | Status in `Suba` Branch |
|---|---|---|---|---|---|
| **Webcam rPPG & Contactless Pulse** | Palette 1 | Bio-Rose `#F43F5E` / Coral `#FB7185` | Matthew | OpenCV / MediaPipe | Dedicated UI Dock Ready |
| **Astronaut Health Monitoring (Module 1)** | Palette 2 | Medical Cyan `#00F0FF` / Blue `#3B82F6` | **Suba** | React / Recharts / SQLite | **Fully Implemented** |
| **Enhanced Statistical Anomaly Engine** | Palette 3 | Telemetry Violet `#8B5CF6` / Orchid `#D946EF` | Matthew | Python / NumPy (Z-Score) | **Database & UI Dock Ready** |
| **Rule-Based Alert & Triage (Module 3)** | Palette 4 | Critical Crimson `#EF4444` / Amber `#F59E0B` | **Suba** | FastAPI / Rules Engine | **Fully Implemented** |
| **Interactive Human Body Map (Module 2)** | Neutral Anatomical | Holographic Medical Cyan & Health Severity | **Suba** | SVG / React / REST API | **Fully Implemented** |
| **Explainable AI Clinical Advisor** | Palette 5 | Emerald Mint `#10B981` / Teal `#14B8A6` | Teammate | LLM / Guidelines RAG | Dedicated UI Dock Ready |
| **Circadian, Fatigue & Stress (PVT)** | Palette 6 | Nebula Indigo `#6366F1` / Periwinkle `#38BDF8` | Matthew | PVT Cognitive Task | Dedicated UI Dock Ready |
| **Space Environment & Radiation (ECLSS)** | Palette 7 | Solar Gold `#EAB308` / Orange `#F97316` | Shared | FastAPI / ECLSS Schema | **APIs Implemented** |

---

##  Teammate Anomaly Dock (Palette 3 — Matthew)

To ensure that Matthew can develop his enhanced Z-score anomaly detector without colliding with Suba's rule-based triage engine, a dedicated database table and Python hook have been established.

### 1. Database Table: `teammate_anomalies_dock`
Located in `starhealers.db`:
```sql
CREATE TABLE IF NOT EXISTS teammate_anomalies_dock (
    anomaly_id TEXT PRIMARY KEY,
    astronaut_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    z_score REAL NOT NULL,
    confidence_interval REAL NOT NULL,
    detected_at TEXT NOT NULL,
    is_integrated INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(astronaut_id) ON DELETE CASCADE
);
```

### 2. Inserting Statistical Anomalies from Matthew's Engine
Matthew can call the existing helper in `backend/crud.py`:
```python
import crud

# Insert a detected Z-score statistical anomaly:
crud.insert_statistical_anomaly(
    anomaly_id="ANOM-Z-101",
    astronaut_id="ASTRO-01",
    metric_name="hrv",
    z_score=-2.85,
    confidence_interval=0.99
)
```

### 3. Merging Rule-Based Alerts with Statistical Anomalies
In `backend/rules_engine.py`, the function `evaluate_astronaut_telemetry(...)` accepts `teammate_anomalies` as an optional parameter.
* **Suba's Module 3:** Evaluates transparent medical thresholds and combined indicator patterns.
* **Matthew's Module:** Injects rolling standard deviations and confidence bands.
* **Result:** The UI presents both transparent rule explanations AND statistical confidence bands side by side without code entanglement.

---

##  Webcam rPPG Integration (Palette 1 — Matthew)

When Matthew completes his optical pulse estimation script using OpenCV and MediaPipe:
1. He can POST his estimated pulse readings directly into the health stream:
   ```http
   POST /api/astronauts/{astronaut_id}/health/readings
   Content-Type: application/json

   {
     "metric_name": "heartRate",
     "value": 72.5,
     "unit": "bpm",
     "source": "CONNECTED SENSOR",
     "quality_status": "GOOD",
     "severity": "NORMAL"
   }
   ```
2. The frontend will immediately ingest, display, and chart Matthew's pulse telemetry under Palette 1 styling.

---

##  Collaborative Git Workflow & Branch Rules

To prevent accidental code overwrites or merge collisions:
1. **Branch Isolation:**
   * Suba commits exclusively to the `Suba` branch.
   * Matthew commits exclusively to the `Matthew` branch.
   * Never push unreviewed code directly to `main`.
2. **Merge Protocol:**
   * When integrating teammate work, submit a GitHub Pull Request from `Suba` → `main` or `Matthew` → `main`.
   * Resolve any conflicts collaboratively in the PR review.
   * Never force-push (`git push --force`).
3. **Database & Build Artifacts:**
   * `.gitignore` prevents volatile `.db` binaries, cache files, and `node_modules` from entering version control.
   * Recreate or seed the database on any fresh clone using `python backend/seed_data.py`.
