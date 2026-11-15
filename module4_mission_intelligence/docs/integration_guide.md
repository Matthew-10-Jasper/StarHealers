# STARHEALERS — MODULE 4: FUTURE INTEGRATION GUIDE
## Connecting Teammate Modules (1, 2, 3, 5, 6, 7) Without Breaking Module 4

### 1. Architectural Independence Principle
During current development, source code, databases, and APIs for Modules 1, 2, and 3 are not available.
Module 4 was built to be **100% executable and testable independently**.

To connect future modules:
- Do NOT rewrite Module 4 core services.
- Use the standardized, versioned contract (`STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT`).
- Implement the abstract adapter interface `BaseModuleIntegrationAdapter`.

---

### 2. Standardized Distribution Contract Structure (`v1.0.0`)
All downstream modules receive the following canonical schema:
```json
{
  "$schema": "./mission_context_v1_schema.json",
  "contract_name": "STARHEALERS_MISSION_CONTEXT_DISTRIBUTION_CONTRACT",
  "schema_version": "1.0.0",
  "timestamp": "2026-11-15T12:00:00Z",
  "context_id": "CTX_001",
  "context_version": 2,
  "mission_id": "ARES_VOYAGER_MARS",
  "planned_profile": "ARES_VOYAGER_MARS",
  "actual_mission_phase": "HELIOCENTRIC_MARS_TRANSIT",
  "operational_state": "NOMINAL",
  "gravity_environment": "MICROGRAVITY",
  "gravity_value_g": 0.0001,
  "communication": {
    "status": "NOMINAL",
    "expected_delay_seconds": 1200.0,
    "bandwidth_mbps": 5.0,
    "earth_reachable": true,
    "queued_reports_count": 0,
    "last_contact_timestamp": "2026-11-15T11:58:30Z",
    "last_acknowledged_timestamp": "2026-11-15T11:45:00Z"
  },
  "environment": {
    "radiation_status": "NOMINAL",
    "cabin_pressure_status": "NOMINAL",
    "co2_status": "NOMINAL",
    "life_support_status": "NOMINAL",
    "habitat_status": "NOMINAL",
    "observed_parameters": {
      "cabin_pressure_kpa": 70.3,
      "co2_concentration_mmhg": 1.2,
      "radiation_msv_per_day": 1.5,
      "o2_percentage": 26.5
    }
  },
  "data_quality": {
    "overall_status": "VERIFIED",
    "unknown_parameters": [],
    "stale_parameters": [],
    "contradictory_parameters": []
  },
  "active_deviations_count": 0,
  "deviations_summary": [],
  "data_source": "SIMULATED"
}
```

---

### 3. Downstream Module Handshake Mapping

| Downstream Target | What Module 4 Provides | How It Consumes the Contract |
| :--- | :--- | :--- |
| **Module 1 (Astronaut Health)** | Gravity ($g$), operational state, cabin pressure, mission phase | Calibrates baseline cardiovascular/musculoskeletal thresholds for microgravity vs Lunar/Martian gravity. |
| **Module 2 (Body Map Interface)** | Gravity environment, physical constraints, habitat status | Adjusts body map visualization for hydrostatic fluid shifts and pressure anomalies. |
| **Module 3 (Clinical Triage Engine)** | Verified environmental evidence (radiation flares, elevated CO2, hypoxia risks, comm latency) | Factors deep-space isolation and environmental etiologies into triage differential diagnoses. |
| **Module 5 (Radiation / Sleep Sim)** | Actual flight phase, radiation flux, circadian light schedules | Synchronizes environmental simulation loops with verified mission elapsed time. |
| **Module 6 (Mission Duration)** | Trajectory phase, mission elapsed seconds, duration overruns | Adapts long-duration psychological support protocols. |
| **Module 7 (Analytics)** | Historical parameter logs, deviation frequencies | Performs multi-mission reliability trends and ECLSS maintenance forecasting. |

---

### 4. Adapter Interface Implementation Example
When teammates publish their REST or gRPC service, implement a subclass of `BaseModuleIntegrationAdapter`:

```python
# app/integrations/adapters.py
class RealModule3TriageAdapter(BaseModuleIntegrationAdapter):
    target_module_id = "MODULE_3_CLINICAL_TRIAGE_ENGINE"

    def __init__(self, triage_service_url: str):
        self.url = triage_service_url

    def deliver_mission_context(self, context_contract: Dict[str, Any]) -> Dict[str, Any]:
        response = httpx.post(f"{self.url}/api/v1/context/ingest", json=context_contract, timeout=5.0)
        return response.json()

    def query_delivery_status(self) -> Dict[str, Any]:
        response = httpx.get(f"{self.url}/health", timeout=2.0)
        return response.json()
```
Module 4's internal deviation engine, contingency state manager, and persistence logic will not require a single line of modification!

