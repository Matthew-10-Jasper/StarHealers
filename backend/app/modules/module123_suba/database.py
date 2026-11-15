"""
StarHealers - Database Engine & Connection Manager
SQLite with Foreign Key Enforcement & Safe Schema Initialization
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

# Determine database path
BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = BACKEND_DIR / "starhealers.db"


def get_db_connection():
    """Create and return a SQLite database connection with row factory and foreign keys enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db():
    """Context manager for safe transactional database sessions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(drop_existing: bool = False):
    """
    Initializes all approved StarHealers SQLite tables and indexes.
    Idempotent: Uses CREATE TABLE IF NOT EXISTS unless drop_existing is True.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        if drop_existing:
            cursor.executescript("""
                DROP TABLE IF EXISTS teammate_anomalies_dock;
                DROP TABLE IF EXISTS historical_telemetry;
                DROP TABLE IF EXISTS triage_alerts;
                DROP TABLE IF EXISTS health_readings;
                DROP TABLE IF EXISTS astronauts;
                DROP TABLE IF EXISTS missions;
                DROP TABLE IF EXISTS users;
            """)

        # 1. Users Table (Flight Surgeons & Medical Officers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Missions Table (ISS, Moon Artemis, Mars Ares)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                phase TEXT NOT NULL,
                comms_delay_sec REAL NOT NULL,
                cabin_co2 REAL NOT NULL,
                cabin_o2 REAL NOT NULL,
                cabin_pressure REAL NOT NULL,
                ambient_temp REAL NOT NULL,
                radiation_dose_rate REAL NOT NULL,
                gravity_g REAL NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'STANDBY', 'COMPLETED'))
            );
        """)

        # 3. Astronauts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS astronauts (
                astronaut_id TEXT PRIMARY KEY,
                mission_id TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                age INTEGER NOT NULL,
                blood_type TEXT NOT NULL,
                height_cm REAL NOT NULL,
                weight_kg REAL NOT NULL,
                avatar_url TEXT,
                status TEXT NOT NULL CHECK(status IN ('NORMAL', 'WARNING', 'CRITICAL', 'NO_DATA')),
                status_reason TEXT,
                baseline_resting_hr REAL NOT NULL,
                baseline_hrv REAL NOT NULL,
                baseline_bp_systolic REAL NOT NULL,
                baseline_bp_diastolic REAL NOT NULL,
                baseline_spo2 REAL NOT NULL,
                baseline_temp REAL NOT NULL,
                baseline_glucose REAL NOT NULL,
                baseline_hydration REAL NOT NULL,
                baseline_stress REAL NOT NULL,
                FOREIGN KEY (mission_id) REFERENCES missions(mission_id) ON DELETE CASCADE
            );
        """)

        # 4. Health Readings Table (Module 1 Core Vitals)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_readings (
                reading_id TEXT PRIMARY KEY,
                astronaut_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL,
                secondary_value REAL,
                unit TEXT NOT NULL,
                source TEXT NOT NULL CHECK(source IN ('SIMULATED', 'RESEARCH DATASET', 'CONNECTED SENSOR', 'MANUAL INPUT')),
                quality_status TEXT NOT NULL CHECK(quality_status IN ('EXCELLENT', 'GOOD', 'DEGRADED', 'UNAVAILABLE', 'VERIFIED', 'VALIDATED', 'HIGH')),
                severity TEXT NOT NULL CHECK(severity IN ('NORMAL', 'WARNING', 'CRITICAL', 'NO_DATA')),
                timestamp TEXT NOT NULL,
                FOREIGN KEY (astronaut_id) REFERENCES astronauts(astronaut_id) ON DELETE CASCADE
            );
        """)

        # 5. Triage Alerts Table (Module 3 Rule-Based Triage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triage_alerts (
                alert_id TEXT PRIMARY KEY,
                astronaut_id TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('NORMAL', 'WARNING', 'CRITICAL', 'NO_DATA')),
                status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'RESOLVED')),
                trigger_reason TEXT NOT NULL,
                explanation TEXT NOT NULL,
                contributing_measurements TEXT NOT NULL,
                escalation_steps TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                acknowledged_by TEXT,
                resolved_at TEXT,
                FOREIGN KEY (astronaut_id) REFERENCES astronauts(astronaut_id) ON DELETE CASCADE,
                FOREIGN KEY (acknowledged_by) REFERENCES users(user_id) ON DELETE SET NULL
            );
        """)

        # 6. Historical Telemetry Archive Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_telemetry (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                astronaut_id TEXT NOT NULL,
                time_label TEXT NOT NULL,
                heart_rate REAL,
                hrv REAL,
                spo2 REAL,
                temperature REAL,
                stress REAL,
                source TEXT NOT NULL DEFAULT 'SIMULATED',
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (astronaut_id) REFERENCES astronauts(astronaut_id) ON DELETE CASCADE
            );
        """)

        # 7. Teammate Anomalies Integration Dock Table (Palette 3 Matthew Z-Score)
        cursor.execute("""
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
        """)

        # Create Essential Performance Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_astro_metric ON health_readings(astronaut_id, metric_name, timestamp DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_astro_status ON triage_alerts(astronaut_id, status, severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_astro_time ON historical_telemetry(astronaut_id, recorded_at ASC);")

    return True


if __name__ == "__main__":
    init_db(drop_existing=False)
    print("StarHealers SQLite database initialized successfully at:", DB_PATH)
