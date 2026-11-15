# STARHEALERS UNIFIED PLATFORM — PERSISTENCE & DATABASE SPECIFICATION

## 1. Multi-Database Architecture

STARHEALERS avoids destructive database mergers by retaining **five dedicated, domain-partitioned SQLite databases**. This preserves complete backwards compatibility, isolates transactions, and ensures Suba's data ownership constraints are strictly honored.

| Database Identifier | File Location | Owning Subsystem | Primary Tables | Pre-Consolidation Backup |
| :--- | :--- | :--- | :--- | :--- |
| **DB 1 (Suba Core)** | `StarHealers-Suba/backend/starhealers.db` | Modules 1, 2, 3 | `astronauts`, `health_readings`, `telemetry`, `missions`, `triage_alerts` | `starhealers_preconsolidation_backup.db` |
| **DB 2 (M4 Context)** | `module4_mission_intelligence/backend/starhealers_m4.db` | Module 4 | `mission_context`, `mission_deviations`, `state_transitions`, `audit_events` | `starhealers_m4_preconsolidation_backup.db` |
| **DB 3 (M5 Hazards)** | `module5_hazard_simulation/backend/starhealers_m5.db` | Module 5 | `simulation_sessions`, `simulation_results`, `simulation_scenarios` | `starhealers_m5_preconsolidation_backup.db` |
| **DB 4 (M6 Circadian)** | `module6_circadian_fatigue/backend/starhealers_m6.db` | Module 6 | `circadian_rhythms`, `pvt_test_sessions`, `sleep_status`, `fatigue_assessments` | `starhealers_m6_preconsolidation_backup.db` |
| **DB 5 (M7 Space Env)** | `module7_environment_radiation/backend/starhealers_m7.db` | Module 7 | `space_weather_readings`, `astronaut_radiation_doses`, `life_support_telemetry` | `starhealers_m7_preconsolidation_backup.db` |

---

## 2. Row Count Preservation Audit

During the preconsolidation phase, exact row counts across all databases were audited and verified. All existing records remain intact:

### Suba Database (`starhealers.db`)
- `astronauts`: 4 crew members (Dr. Sarah Chen, Mark Watney, Ellen Ripley, Dr. Joseph Cooper)
- `health_readings`: 36 continuous telemetry points
- `missions`: 3 operational missions (ISS, Moon Artemis, Mars Ares)
- `triage_alerts`: 3 baseline clinical alerts
- `telemetry`: 48 environmental and cabin data points

### Module 4 Database (`starhealers_m4.db`)
- `mission_context`: Current operational envelope and active flight phases
- `mission_deviations`: Historical and active deviation logs
- `state_transitions`: Immutable audit ledger of flight state changes
- `audit_events`: Timestamped operator authorizations

### Module 5 Database (`starhealers_m5.db`)
- `simulation_scenarios`: 5 predefined multi-hazard scenarios
- `simulation_sessions`: Multi-hazard controller sessions

### Module 6 Database (`starhealers_m6.db`)
- `circadian_rhythms`: 24-hour alertness curves per astronaut
- `sleep_status`: Cumulative sleep debt tracking
- `pvt_test_sessions`: Neurobehavioral reaction time records

### Module 7 Database (`starhealers_m7.db`)
- `space_weather_readings`: Solar proton and cosmic ray flux
- `astronaut_radiation_doses`: Career radiation exposure records
- `life_support_telemetry`: Cabin atmosphere gas concentrations

---

## 3. Database Safety & Integrity Guarantees

1. **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON;` is enforced on all SQLite connections to prevent orphaned telemetry records.
2. **Missing-Data Semantics**: Sensor outages report explicit `NO_DATA` or `UNKNOWN` rather than defaulting numeric columns to `0.0`, eliminating false assurances in clinical triage.
3. **Backup Recovery**: All five preconsolidation backups (`*_preconsolidation_backup.db`) are stored in their respective module backend directories for immediate zero-loss restoration if needed.
