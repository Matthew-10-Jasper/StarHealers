"""
StarHealers - Database Seeder
Seeds initial missions, fictional astronaut profiles, baseline physiological readings,
simulated telemetry time-series, and transparent rule-based alerts.
"""

import json
from datetime import datetime, timedelta
from database import init_db, get_db


def seed():
    # Initialize / clean schema
    init_db(drop_existing=True)

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Seed Medical Officer User
        cursor.execute(
            """
            INSERT INTO users (user_id, username, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("USR-MED-01", "suba", "Suba", "Flight Surgeon / Medical Officer", "2026-11-15T00:00:00Z")
        )

        # 2. Seed Missions (ISS, Moon, Mars)
        missions = [
            ("mission-mars-01", "Ares V — Mars Transit", "Mars", "Deep Space Cruise (Day 142)", 840.0, 0.42, 20.9, 101.3, 21.4, 1.82, 0.00, "ACTIVE"),
            ("mission-artemis-03", "Artemis IV — Lunar Outpost", "Moon", "South Pole Surface Ops", 1.3, 0.35, 21.0, 101.1, 22.0, 0.75, 0.16, "STANDBY"),
            ("mission-iss-exp72", "ISS Expedition 72", "Low Earth Orbit", "Orbital Laboratory", 0.4, 0.28, 21.2, 101.3, 22.5, 0.45, 0.00, "ACTIVE"),
        ]
        cursor.executemany(
            """
            INSERT INTO missions 
            (mission_id, name, target, phase, comms_delay_sec, cabin_co2, cabin_o2, cabin_pressure, ambient_temp, radiation_dose_rate, gravity_g, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            missions
        )

        # 3. Seed Astronauts
        astronauts = [
            (
                "ASTRO-01", "mission-mars-01", "Dr. Sarah Chen", "Commander & Astrobiologist",
                38, "A+", 168.0, 61.0,
                "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
                "WARNING", "Elevated heart rate, reduced HRV & acute cumulative sleep deficit",
                62.0, 68.0, 114.0, 74.0, 98.0, 36.6, 92.0, 62.0, 28.0
            ),
            (
                "ASTRO-02", "mission-mars-01", "Cmdr. Marcus Vance", "Pilot & Flight Systems Lead",
                42, "O+", 182.0, 79.0,
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
                "NORMAL", "All physiological telemetry within nominal baselines",
                58.0, 74.0, 118.0, 76.0, 99.0, 36.5, 95.0, 64.0, 22.0
            ),
            (
                "ASTRO-03", "mission-mars-01", "Dr. Elena Rostova", "Flight Surgeon & Medical Officer",
                36, "B+", 172.0, 64.0,
                "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
                "CRITICAL", "Acute SpO2 drop (90%) with elevated compensatory heart rate",
                60.0, 65.0, 116.0, 75.0, 98.0, 36.7, 88.0, 60.0, 25.0
            ),
            (
                "ASTRO-04", "mission-mars-01", "Alex Tanaka", "Payload & Robotics Specialist",
                31, "AB-", 175.0, 68.0,
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
                "NO_DATA", "Telemetry sensor link recalibrating; biometric data packet deferred",
                64.0, 62.0, 120.0, 78.0, 98.0, 36.6, 90.0, 59.0, 30.0
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO astronauts 
            (astronaut_id, mission_id, name, role, age, blood_type, height_cm, weight_kg, avatar_url, status, status_reason,
             baseline_resting_hr, baseline_hrv, baseline_bp_systolic, baseline_bp_diastolic, baseline_spo2, baseline_temp,
             baseline_glucose, baseline_hydration, baseline_stress)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            astronauts
        )

        # 4. Seed Health Readings for Each Astronaut
        # Dr. Sarah Chen (ASTRO-01) - Autonomic Fatigue Pattern
        sarah_readings = [
            ("R-01-HR", "ASTRO-01", "heartRate", 94.0, None, "bpm", "SIMULATED", "GOOD", "WARNING", "2026-11-15T15:45:00Z"),
            ("R-01-HRV", "ASTRO-01", "hrv", 34.0, None, "ms", "SIMULATED", "GOOD", "WARNING", "2026-11-15T15:45:00Z"),
            ("R-01-BP", "ASTRO-01", "bloodPressure", 136.0, 88.0, "mmHg", "SIMULATED", "GOOD", "WARNING", "2026-11-15T15:40:00Z"),
            ("R-01-SPO2", "ASTRO-01", "spo2", 97.0, None, "%", "SIMULATED", "GOOD", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-01-TEMP", "ASTRO-01", "temperature", 37.1, None, "°C", "SIMULATED", "GOOD", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-01-GLU", "ASTRO-01", "glucose", 104.0, None, "mg/dL", "SIMULATED", "GOOD", "NORMAL", "2026-11-15T14:30:00Z"),
            ("R-01-SLP", "ASTRO-01", "sleep", 4.8, None, "hrs", "CONNECTED SENSOR", "HIGH", "WARNING", "2026-11-15T08:00:00Z"),
            ("R-01-HYD", "ASTRO-01", "hydration", 58.0, None, "%", "SIMULATED", "GOOD", "NORMAL", "2026-11-15T15:00:00Z"),
            ("R-01-STR", "ASTRO-01", "stress", 72.0, None, "pts", "RESEARCH DATASET", "VALIDATED", "WARNING", "2026-11-15T15:30:00Z"),
        ]

        # Cmdr. Marcus Vance (ASTRO-02) - Nominal
        marcus_readings = [
            ("R-02-HR", "ASTRO-02", "heartRate", 64.0, None, "bpm", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-02-HRV", "ASTRO-02", "hrv", 76.0, None, "ms", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-02-BP", "ASTRO-02", "bloodPressure", 118.0, 76.0, "mmHg", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:40:00Z"),
            ("R-02-SPO2", "ASTRO-02", "spo2", 99.0, None, "%", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-02-TEMP", "ASTRO-02", "temperature", 36.6, None, "°C", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:45:00Z"),
            ("R-02-GLU", "ASTRO-02", "glucose", 94.0, None, "mg/dL", "MANUAL INPUT", "VERIFIED", "NORMAL", "2026-11-15T13:00:00Z"),
            ("R-02-SLP", "ASTRO-02", "sleep", 7.9, None, "hrs", "CONNECTED SENSOR", "HIGH", "NORMAL", "2026-11-15T08:00:00Z"),
            ("R-02-HYD", "ASTRO-02", "hydration", 63.0, None, "%", "CONNECTED SENSOR", "EXCELLENT", "NORMAL", "2026-11-15T15:00:00Z"),
            ("R-02-STR", "ASTRO-02", "stress", 24.0, None, "pts", "CONNECTED SENSOR", "HIGH", "NORMAL", "2026-11-15T15:30:00Z"),
        ]

        # Dr. Elena Rostova (ASTRO-03) - Critical Hypoxemia
        elena_readings = [
            ("R-03-HR", "ASTRO-03", "heartRate", 112.0, None, "bpm", "SIMULATED", "GOOD", "CRITICAL", "2026-11-15T15:45:00Z"),
            ("R-03-HRV", "ASTRO-03", "hrv", 26.0, None, "ms", "SIMULATED", "GOOD", "CRITICAL", "2026-11-15T15:45:00Z"),
            ("R-03-BP", "ASTRO-03", "bloodPressure", 142.0, 92.0, "mmHg", "SIMULATED", "GOOD", "CRITICAL", "2026-11-15T15:40:00Z"),
            ("R-03-SPO2", "ASTRO-03", "spo2", 90.0, None, "%", "SIMULATED", "GOOD", "CRITICAL", "2026-11-15T15:45:00Z"),
            ("R-03-TEMP", "ASTRO-03", "temperature", 37.4, None, "°C", "SIMULATED", "GOOD", "WARNING", "2026-11-15T15:45:00Z"),
            ("R-03-GLU", "ASTRO-03", "glucose", 110.0, None, "mg/dL", "SIMULATED", "GOOD", "NORMAL", "2026-11-15T14:30:00Z"),
            ("R-03-SLP", "ASTRO-03", "sleep", 6.2, None, "hrs", "SIMULATED", "GOOD", "WARNING", "2026-11-15T08:00:00Z"),
            ("R-03-HYD", "ASTRO-03", "hydration", 54.0, None, "%", "SIMULATED", "GOOD", "WARNING", "2026-11-15T15:00:00Z"),
            ("R-03-STR", "ASTRO-03", "stress", 84.0, None, "pts", "SIMULATED", "GOOD", "CRITICAL", "2026-11-15T15:30:00Z"),
        ]

        # Alex Tanaka (ASTRO-04) - Missing / Disconnected Sensor Node (NO DATA)
        alex_readings = [
            ("R-04-HR", "ASTRO-04", "heartRate", None, None, "bpm", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-HRV", "ASTRO-04", "hrv", None, None, "ms", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-BP", "ASTRO-04", "bloodPressure", None, None, "mmHg", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-SPO2", "ASTRO-04", "spo2", None, None, "%", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-TEMP", "ASTRO-04", "temperature", None, None, "°C", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-GLU", "ASTRO-04", "glucose", None, None, "mg/dL", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-SLP", "ASTRO-04", "sleep", None, None, "hrs", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T08:00:00Z"),
            ("R-04-HYD", "ASTRO-04", "hydration", None, None, "%", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
            ("R-04-STR", "ASTRO-04", "stress", None, None, "pts", "SIMULATED", "UNAVAILABLE", "NO_DATA", "2026-11-15T15:00:00Z"),
        ]

        all_readings = sarah_readings + marcus_readings + elena_readings + alex_readings
        cursor.executemany(
            """
            INSERT INTO health_readings 
            (reading_id, astronaut_id, metric_name, value, secondary_value, unit, source, quality_status, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            all_readings
        )

        # 5. Seed Historical Telemetry Samples (for Recharts)
        hist_records = []
        base_time = datetime(2026, 11, 15, 0, 0)
        for i in range(24):
            time_label = f"{i:02d}:00"
            rec_time = (base_time + timedelta(hours=i)).isoformat() + "Z"
            # Sarah (gradual fatigue accumulation)
            hist_records.append((
                "ASTRO-01", time_label,
                round(62 + i * 1.3),
                max(24, round(68 - i * 1.4)),
                round(98 - (0.05 * i)),
                round(36.6 + (0.02 * i), 1),
                min(90, round(28 + i * 1.8)),
                "SIMULATED", rec_time
            ))
            # Marcus (steady baseline)
            hist_records.append((
                "ASTRO-02", time_label,
                round(58 + (i % 3)),
                round(74 - (i % 2)),
                99,
                36.5,
                22,
                "SIMULATED", rec_time
            ))

        cursor.executemany(
            """
            INSERT INTO historical_telemetry 
            (astronaut_id, time_label, heart_rate, hrv, spo2, temperature, stress, source, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            hist_records
        )

        # 6. Seed Transparent Rule-Based Triage Alerts (Module 3)
        alerts = [
            (
                "ALT-2026-0891", "ASTRO-03", "RULE-HYPOXIA-ACUTE-01",
                "Acute Hypoxic Respiratory Depletion", "CRITICAL", "ACTIVE",
                "Arterial SpO2 fell below critical threshold (< 92%) with concurrent tachycardia (> 110 bpm) under microgravity environment.",
                "Hypoxemia detected. The astronaut's blood oxygen saturation has dropped significantly below acceptable deep-space physiological tolerance. Concomitant elevated heart rate indicates compensatory cardiac drive attempting to preserve peripheral perfusion. Not an automated diagnosis of pathology; rule indicates immediate respiratory protocol escalation.",
                json.dumps([
                    {"name": "SpO2", "value": "90%", "threshold": "< 92%", "unit": "%", "status": "CRITICAL"},
                    {"name": "Heart Rate", "value": "112 bpm", "threshold": "> 105 bpm", "unit": "bpm", "status": "CRITICAL"},
                    {"name": "Cabin CO2", "value": "0.42%", "threshold": "< 0.50%", "unit": "%", "status": "NORMAL"}
                ]),
                json.dumps([
                    "Immediate crew cross-check of portable O2 mask system",
                    "Verify suit/helmet air scrubbers and cabin ventilation loop",
                    "Perform bedside lung auscultation and pulse oximeter probe re-seat",
                    "Prepare autonomous Medical Kit Bravo (Bronchodilator / O2 supply)"
                ]),
                "2026-11-15T15:42:10Z", None, None
            ),
            (
                "ALT-2026-0888", "ASTRO-01", "RULE-FATIGUE-COMPOUND-03",
                "Multi-Signal Autonomic Fatigue Pattern", "WARNING", "ACTIVE",
                "Combined detection of suppressed vagal HRV (< 40 ms), chronic sleep truncation (< 5.0 hrs), and sympathetic hyper-reactivity (Stress > 70 pts).",
                "Multi-parameter autonomic imbalance. Chronic circadian disruption and sleep deprivation are producing cumulative autonomic strain. Cardiac vagal tone is suppressed by 50% relative to baseline, elevating cognitive lapse risk during critical mission maneuvers.",
                json.dumps([
                    {"name": "Heart Rate Variability", "value": "34 ms", "threshold": "< 40 ms (Baseline: 68 ms)", "unit": "ms", "status": "WARNING"},
                    {"name": "24h Sleep Duration", "value": "4.8 hrs", "threshold": "< 6.0 hrs", "unit": "hrs", "status": "WARNING"},
                    {"name": "Physiological Stress", "value": "72 pts", "threshold": "> 65 pts", "unit": "pts", "status": "WARNING"},
                    {"name": "Resting Heart Rate", "value": "94 bpm", "threshold": "> 85 bpm (Resting)", "unit": "bpm", "status": "WARNING"}
                ]),
                json.dumps([
                    "Recommend 90-minute restorative sleep block prior to EVA duties",
                    "Review cognitive workload and schedule non-critical task deferrals",
                    "Administer scheduled blue-wavelength light therapy attenuation",
                    "Log PVT (Psychomotor Vigilance Task) assessment at next duty station"
                ]),
                "2026-11-15T14:15:22Z", "USR-MED-01", None
            ),
            (
                "ALT-2026-0865", "ASTRO-04", "RULE-SENSOR-LINK-01",
                "Telemetry Signal Loss — Biometric Node 4", "NO_DATA", "ACTIVE",
                "Continuous missing data packets exceeding 30 minutes from wearable telemetry suite.",
                "Astronaut biometric hub is offline or undergoing scheduled recharging. Telemetry triage marked as NO DATA rather than normal to prevent false assurance.",
                json.dumps([
                    {"name": "Sensor Packet Loss", "value": "100%", "threshold": "> 25%", "unit": "%", "status": "NO_DATA"},
                    {"name": "Last Heartbeat", "value": "43m ago", "threshold": "> 15m", "unit": "time", "status": "NO_DATA"}
                ]),
                json.dumps([
                    "Prompt crew member to check wearable sensor power status",
                    "Verify habitat wireless transponder link"
                ]),
                "2026-11-15T15:02:11Z", None, None
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO triage_alerts
            (alert_id, astronaut_id, rule_id, title, severity, status, trigger_reason, explanation,
             contributing_measurements, escalation_steps, timestamp, acknowledged_by, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            alerts
        )

        # 7. Seed Teammate Anomalies Integration Dock Sample (Palette 3 Matthew)
        cursor.execute(
            """
            INSERT INTO teammate_anomalies_dock
            (anomaly_id, astronaut_id, metric_name, z_score, confidence_interval, detected_at, is_integrated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("ANOM-Z-001", "ASTRO-03", "heartRate", 2.84, 0.99, "2026-11-15T15:45:00Z", 1)
        )

    print("StarHealers database seeded successfully.")


if __name__ == "__main__":
    seed()
