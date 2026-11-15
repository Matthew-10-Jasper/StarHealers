# STARHEALERS MODULE 4 — TESTING & RELIABILITY STRATEGY
**Comprehensive Verification Architecture for Mission Environment Intelligence**

---

## 1. Testing Philosophy & Multi-Layered Quality Pyramid

Module 4 employs a defense-in-depth verification strategy designed to guarantee zero runtime failures, physical dimensional consistency, and deterministic state evolution in deep-space operational conditions.

```
                    ┌─────────────────────────┐
                    │  Mock Consumer Delivery │
                    │   & Integration Tests   │
                    ├─────────────────────────┤
                    │ Property-Based Testing  │
                    │       (Hypothesis)      │
                    ├─────────────────────────┤
                    │   Layered Anomaly & ML  │
                    │      Verification       │
                    ├─────────────────────────┤
                    │ Scientific Units (Pint) │
                    │   & Invariant Bounds    │
                    ├─────────────────────────┤
                    │  Deterministic Pytest   │
                    │  API & Service Suites   │
                    └─────────────────────────┘
```

---

## 2. Test Suites Summary

| Test Suite File | Framework / Engine | Tests Count | Scope / Key Invariants Tested |
| :--- | :--- | :--- | :--- |
| **`tests/test_mission_intelligence.py`** | Pytest | 28 Tests | Baseline core: Profile validation, gravity distinctions, deviations, state engine, audit trail, context envelopes |
| **`tests/test_scientific_units.py`** | Pytest + Pint | 10 Tests | Pressure conversions, non-physical negative pressures, CO2 partial pressures, Gy vs Sv dimensional separation, w_R scaling |
| **`tests/test_properties.py`** | Hypothesis | 5 Property Suites (190+ fuzzed samples) | State machine graph invariant, pressure round-trip invariance, telemetry idempotency invariant, CO2 percentage-ppm invariant |
| **`tests/test_anomaly_detector.py`**| Pytest + SciPy + Scikit-Learn | 4 Tests | Layer 1 sensor bounds, Layer 3 engineering physics, Layer 4 statistical Z-scores, Layer 5 Isolation Forest explainability |
| **`tests/run_tests.py`** | Standalone Python Monolith Runner | 12 E2E Stages | Full end-to-end integration: DB persistence across restarts, simulator scenario ingestion, mock module delivery |
| **Frontend Production Build** | TypeScript (`tsc`) + Vite | Build & Typecheck | 0 TypeScript errors, production chunk compilation, ECharts & Recharts integration |

---

## 3. How to Run Verification Suites

### 1. Run Complete Pytest Suite
```bash
cd module4_mission_intelligence/backend
python -m pytest tests/test_mission_intelligence.py tests/test_scientific_units.py tests/test_properties.py tests/test_anomaly_detector.py -p no:anyio -v
```

### 2. Run Standalone Integration Runner
```bash
cd module4_mission_intelligence/backend
python tests/run_tests.py
```

### 3. Verify Database Migration Status
```bash
cd module4_mission_intelligence/backend
python -m alembic current
```

### 4. Run Frontend Typecheck & Production Build
```bash
cd module4_mission_intelligence/frontend
npm run build
```

