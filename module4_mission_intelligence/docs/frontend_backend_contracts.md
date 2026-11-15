# STARHEALERS MODULE 4 — FRONTEND & BACKEND INTEGRATION CONTRACTS
**Deterministic Mission Context Envelopes & Runtime Validation**

---

## 1. Overview & Architectural Philosophy

Module 4 acts as the mission environment intelligence source of truth for the entire STARHEALERS deep-space platform. To eliminate divergence between server-side telemetry logic and client-side dashboards, Module 4 implements a three-tier end-to-end type safety architecture:

```
[FastAPI / Pydantic v2 Models]
           │
           ▼ (scripts/generate_openapi.py)
[OpenAPI 3.1 JSON Specification] (integration_contracts/openapi.json)
           │
           ▼ (Runtime Validation via Zod)
[Frontend Zod Contracts] (frontend/src/schemas/contracts.ts)
           │
           ▼ (Compile-time Type Safety via TypeScript)
[React / TanStack Query Components] (frontend/src/types/mission.ts)
```

---

## 2. Mission Context Envelope Specification (`mission_context_v1.json`)

All downstream modules (Module 1 Astronaut Health, Module 3 Clinical Triage, Module 5 Simulation) and the frontend receive standardized mission context envelopes:

| Field | Type | Description |
| :--- | :--- | :--- |
| `context_id` | String (UUID) | Unique identifier for this discrete mission environment state snapshot |
| `context_version` | Integer | Strictly monotonic incrementing sequence number ($V_{t+1} > V_t$) |
| `mission_id` | String | Planned mission identifier (e.g., `ARES_VOYAGER_MARS`, `ARTEMIS_BASE_LUNAR`) |
| `planned_profile` | String | Reference ID to active planned trajectory configuration |
| `actual_mission_phase`| String | Current verified flight phase (e.g. `MARS_TRANSIT`, `LUNAR_DESCENT`) |
| `operational_state` | Enum | `NOMINAL`, `DEGRADED`, `CONTINGENCY`, `UNKNOWN`, `RECOVERY` |
| `gravity_environment` | Enum | `MICROGRAVITY`, `LUNAR_GRAVITY`, `MARTIAN_GRAVITY`, `EARTH_STANDARD` |
| `gravity_value_g` | Float | Measured physical gravity ($g_0$) |
| `communication` | Object | Deep-space delay, Earth reachability, queue buffer status |
| `environment` | Object | Cabin pressure, CO2 concentration, radiation dose rate, life-support |
| `data_quality` | Object | Freshness, unverified parameters, contradictory sensor alerts |
| `active_deviations` | Array | Array of active confirmed deviations with severity and physical evidence |
| `data_source` | Enum | Explicitly tagged `SIMULATED` for synthetic dev streams |
| `last_updated` | ISO 8601 String | UTC timestamp of last envelope evaluation |

---

## 3. Runtime Verification with Zod

Static TypeScript types disappear after compilation. Deep-space telemetry ingestion demands runtime defense against corrupted packets, network relay dropouts, or version mismatches.

`frontend/src/schemas/contracts.ts` implements `parseMissionContext()`:
```typescript
const result = MissionContextResponseSchema.safeParse(rawData);
if (!result.success) {
  console.warn('MissionContext runtime contract validation warning:', result.error.format());
  return rawData as MissionContextResponse;
}
return result.data;
```
If an unexpected schema violation occurs (e.g. unknown operational state or missing gravity field), the client logs a structured warning with the exact field divergence without hard-crashing the user interface.

---

## 4. Contract Generation Workflow

Whenever backend Pydantic models are modified or new endpoints are added:

1. Run the OpenAPI generator:
```bash
python backend/scripts/generate_openapi.py
```
2. Verify the output at `integration_contracts/openapi.json`.
3. Re-run frontend type checking and production build:
```bash
cd frontend
npm run build
```

