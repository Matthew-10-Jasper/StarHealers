# STARHEALERS — MODULE 4: FAILURE-RESISTANT RELIABILITY SPECIFICATION
## Fault Isolation, Graceful Degradation & Telemetry Handling

### 1. Missing Telemetry
- **Principle**: Missing telemetry must never be treated as proof of nominal operation, nor proof of a catastrophic emergency.
- **Handling**:
  - Missing parameters remain explicitly labeled `UNKNOWN`.
  - The `data_quality.unknown_parameters` list tracks all missing values.
  - The system will NOT invent or interpolate missing parameters.
  - If critical telemetry streams are absent, the operational state transitions to `UNKNOWN`.

---

### 2. Stale Telemetry
- **Threshold**: $>300\text{ seconds}$ without verified update.
- **Handling**:
  - An observation older than the stale threshold is rejected for state promotion and marked `QualityStatus.STALE`.
  - The dashboard visually displays data freshness timestamps.
  - Stale telemetry will not be used to justify returning an operational state to `NOMINAL`.

---

### 3. Contradictory Telemetry
- **Detection**: Sudden radical sensor delta ($>80\%$ instantaneous change or $>4\times$ ratio) arriving within $30\text{ seconds}$ without continuous trend data.
- **Handling**:
  - The observation is flagged as `QualityStatus.CONTRADICTORY` with `validation_status=False`.
  - It is isolated in the database audit log with previous and current conflicting readings.
  - The system maintains the last verified stable state until sensor diagnostics confirm or reject the anomaly.

---

### 4. Invalid Physical Units
- **Handling**:
  - Module 4 enforces a strict whitelist of physical units per parameter (e.g. `kPa` / `psi` for cabin pressure, `mmHg` / `ppm` for CO2, `mSv/day` for radiation).
  - Unrecognized units (e.g. `INVALID_UNIT_XYZ`) are immediately rejected with `QualityStatus.INVALID_UNIT`.
  - A structured warning is returned to the client and logged to SQLite audit trails.

---

### 5. Application Crash & Database Restart
- **Handling**:
  - All mission states, context versions, deviations, state transitions, and environmental readings are committed with SQLite ACID transactions.
  - Upon process restart, the repository retrieves the most recent active entity and reconstructs the active context version without data loss.
  - Past historical records for previous mission profiles (e.g. switching from ISS to Moon to Mars) are never purged.

---

### 6. Deep Space Communication Blackout
- **Handling**:
  - When communication link is lost (`CommStatus.BLACKOUT`), the system activates local-first autonomous constraints.
  - Alerts are stored in the local SQLite buffer with delivery status `LOCALLY_GENERATED`.
  - They are promoted to `QUEUED` in the transmission queue.
  - The system strictly forbids marking any report as delivered or acknowledged until explicit ground receipt verification is confirmed (`ReportDeliveryStatus.ACKNOWLEDGED`).
  - No autonomous decision overrides crew command or issues unverified medical procedures.

