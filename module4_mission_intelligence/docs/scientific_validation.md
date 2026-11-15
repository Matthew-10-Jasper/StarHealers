# STARHEALERS MODULE 4 — SCIENTIFIC & OPERATIONAL VALIDATION
**Mission Environment Intelligence & Adaptive Context Management**

---

## 1. Aerospace Physical Telemetry & Canonical Units

Module 4 models actual spacecraft environments strictly on empirical aerospace medicine and life-support physical principles.

| Parameter | Canonical Unit | Physical Dimension | Aerospace Operational Limits | Medical / Physiological Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Cabin Pressure** | `kPa` | Pressure ($[M][L]^{-1}[T]^{-2}$) | Nominal: $95.0 - 105.0\text{ kPa}$ ($1\text{ atm} = 101.325\text{ kPa}$)<br>Critical Low: $< 70.0\text{ kPa}$ | Sub-atmospheric hypoxia, decompression sickness (nitrogen bubble formation in tissues). |
| **Carbon Dioxide ($CO_2$)** | `ppm` | Volume fraction ($10,000\text{ ppm} = 1\%$) | Nominal: $< 2,500\text{ ppm}$ ($< 1.9\text{ mmHg}$)<br>Warning: $> 4,000\text{ ppm}$<br>Critical: $> 8,000\text{ ppm}$ | Hypercapnia, headaches, impaired cognitive decision-making, visual disturbances, respiratory acidosis. |
| **Radiation Equivalent Dose Rate** | `mSv/day` | Biological Equivalent Dose Rate ($[L]^2[T]^{-3}$) | Nominal Deep Space: $0.3 - 1.2\text{ mSv/day}$<br>Solar Particle Event (SPE): $> 20.0\text{ mSv/day}$ | Acute Radiation Syndrome (ARS), hematopoietic suppression, DNA double-strand breaks, long-term carcinogenesis. |
| **Gravity Acceleration** | $g_0$ ($1 g_0 = 9.80665\text{ m/s}^2$) | Acceleration ($[L][T]^{-2}$) | Variable by mission phase:<br>Microgravity: $\approx 10^{-4} g$<br>Lunar: $0.166 g$<br>Mars: $0.38 g$ | Bone mineral density deconditioning (osteopenia), cephalad fluid redistribution, cardiovascular deconditioning, spaceflight-associated neuro-ocular syndrome (SANS). |
| **Communication Delay** | `seconds` (`s`) | Time ($[T]$) | LEO: $< 0.5\text{ s}$<br>Lunar Gateway: $1.2 - 2.5\text{ s}$<br>Mars Transit: $180 - 1,320\text{ s}$ ($3 - 22\text{ min}$) | Precludes real-time telemedicine consultation; necessitates fully autonomous onboard clinical decisions. |

---

## 2. Fundamental Radiation Physics: Absorbed Dose (Gy) vs Equivalent Dose (Sv)

A critical scientific distinction enforced in Module 4 is the non-interchangeability of Absorbed Dose and Biological Equivalent Dose:

### Physical Absorbed Dose ($D$)
- Unit: **Gray (Gy)** ($1\text{ Gy} = 1\text{ J/kg}$)
- Represents the raw physical ionizing energy deposited per unit mass of matter.
- Telemetry units: `Gy`, `mGy`, `uGy`, `rad`, `cGy`.

### Biological Equivalent Dose ($H$)
- Unit: **Sievert (Sv)**
- Represents the biological harm caused to human tissue, accounting for the Radiation Weighting Factor ($w_R$) of different radiation particles:
  $$H = \sum_R w_R \cdot D_R$$
- In deep space:
  - Gamma and beta rays: $w_R = 1$
  - High-energy solar protons: $w_R \approx 2 - 5$
  - Heavy galactic cosmic ray (GCR) HZE nuclei (e.g. Iron $^{56}\text{Fe}$): $w_R \approx 20$

### Module 4 Enforcement Rule:
Direct conversion between absorbed dose (`mGy/day`) and equivalent dose (`mSv/day`) is dimensionally invalid without an explicit $w_R$. Any telemetry stream reporting Gray directly without a radiation weighting factor is strictly rejected with a scientific validation error by Pint:
```
Incompatible radiation dimension: 'mGy/d' is an Absorbed Dose rate (Gray/rad).
Cannot convert directly to Canonical Equivalent Dose rate (mSv/day) without
an explicit Radiation Weighting Factor (w_R). Gray and Sievert are not interchangeable.
```

---

## 3. Planetary & Orbital Gravitational Environments

Spacecraft gravity is not a static constant per destination. Module 4 enforces scientific phase distinctions:

1. **LEO / Orbital Flight:** Microgravity ($\sim 0.0001 g$), even though the Earth is 400 km away.
2. **Lunar Orbit (Gateway):** Orbital microgravity ($\sim 0.0001 g$).
3. **Lunar Surface (Artemis Base):** Planetary surface gravity ($0.166 g = 1.62\text{ m/s}^2$).
4. **Mars Transit / Interplanetary Cruise:** Microgravity ($\sim 0.0001 g$).
5. **Mars Surface:** Planetary surface gravity ($0.38 g = 3.72\text{ m/s}^2$).

---

## 4. Operational State Machine Governance

The operational state machine guarantees determinism and safety gates:

```
[NOMINAL] ──────► [DEGRADED] ──────► [CONTINGENCY]
    ▲                 │                    │
    │                 ▼                    ▼
    └─────────── [RECOVERY] ◄──────────────┘
```

1. **Automatic Transitions:**
   - Critical hazards (e.g. depressurization $< 70\text{ kPa}$ or SPE $> 20\text{ mSv/day}$) automatically transition state from `NOMINAL` to `CONTINGENCY`.
2. **Safety Gates for Return to NOMINAL:**
   - State transition back to `NOMINAL` strictly requires verified evidence payload proving physical normalization.
   - Any attempt to return to `NOMINAL` while active critical deviations remain is blocked.
3. **Audit Immutability:**
   - Every state transition generates a SHA-256 indexed `StateTransitionRecord` and `AuditEvent` persisted to SQLite.

---

## 5. Development Telemetry Disclosure

All default and simulated telemetry streams generated by Module 4's simulation engine are explicitly stamped with:
```json
{
  "data_source": "SIMULATED",
  "notice": "SYNTHETIC DEVELOPMENT DATA ONLY - NOT A REAL SPACECRAFT"
}
```
Module 4 does not claim NASA flight certification or live physical spacecraft actuation.

