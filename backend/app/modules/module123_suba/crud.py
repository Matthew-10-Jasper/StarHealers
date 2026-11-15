"""
StarHealers - Database CRUD & Data Access Layer
Type-safe query helpers for Missions, Astronauts, Health Readings, Triage Alerts, and Historical Telemetry
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.modules.module123_suba.database import get_db


# ==========================================
# USERS CRUD
# ==========================================

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def create_user(user_id: str, username: str, full_name: str, role: str) -> Dict[str, Any]:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (user_id, username, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, full_name, role, datetime.utcnow().isoformat() + "Z")
        )
    return get_user(user_id)


# ==========================================
# MISSIONS CRUD
# ==========================================

def get_missions() -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM missions ORDER BY name ASC").fetchall()
        return [dict(r) for r in rows]


def get_mission(mission_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,)).fetchone()
        return dict(row) if row else None


# ==========================================
# ASTRONAUTS CRUD
# ==========================================

def get_astronauts(mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db() as conn:
        if mission_id:
            rows = conn.execute(
                "SELECT * FROM astronauts WHERE mission_id = ? ORDER BY astronaut_id ASC", (mission_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM astronauts ORDER BY astronaut_id ASC").fetchall()
        return [dict(r) for r in rows]


def get_astronaut(astronaut_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM astronauts WHERE astronaut_id = ?", (astronaut_id,)).fetchone()
        return dict(row) if row else None


def update_astronaut_status(astronaut_id: str, status: str, status_reason: str) -> bool:
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE astronauts SET status = ?, status_reason = ? WHERE astronaut_id = ?",
            (status, status_reason, astronaut_id)
        )
        return cur.rowcount > 0


# ==========================================
# HEALTH READINGS CRUD (Module 1 Core Vitals)
# ==========================================

def get_latest_readings_by_astronaut(astronaut_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns the most recent reading for each of the 9 monitored parameters for an astronaut.
    """
    with get_db() as conn:
        query = """
            SELECT hr.*
            FROM health_readings hr
            INNER JOIN (
                SELECT astronaut_id, metric_name, MAX(timestamp) as max_time
                FROM health_readings
                WHERE astronaut_id = ?
                GROUP BY astronaut_id, metric_name
            ) latest ON hr.astronaut_id = latest.astronaut_id 
                    AND hr.metric_name = latest.metric_name 
                    AND hr.timestamp = latest.max_time
        """
        rows = conn.execute(query, (astronaut_id,)).fetchall()
        results = {}
        for r in rows:
            d = dict(r)
            results[d["metric_name"]] = {
                "value": d["value"],
                "secondaryValue": d["secondary_value"],
                "unit": d["unit"],
                "source": d["source"],
                "quality": d["quality_status"],
                "severity": d["severity"],
                "status": d["severity"],
                "timestamp": d["timestamp"],
            }
        return results


def insert_health_reading(
    reading_id: str,
    astronaut_id: str,
    metric_name: str,
    value: Optional[float],
    unit: str,
    source: str = "SIMULATED",
    quality_status: str = "GOOD",
    severity: str = "NORMAL",
    secondary_value: Optional[float] = None,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    ts = timestamp or (datetime.utcnow().isoformat() + "Z")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO health_readings 
            (reading_id, astronaut_id, metric_name, value, secondary_value, unit, source, quality_status, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (reading_id, astronaut_id, metric_name, value, secondary_value, unit, source, quality_status, severity, ts)
        )
    return {
        "reading_id": reading_id,
        "astronaut_id": astronaut_id,
        "metric_name": metric_name,
        "value": value,
        "secondary_value": secondary_value,
        "unit": unit,
        "source": source,
        "quality_status": quality_status,
        "severity": severity,
        "timestamp": ts,
    }


# ==========================================
# HISTORICAL TELEMETRY CRUD
# ==========================================

def get_historical_telemetry(astronaut_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT time_label as time, heart_rate as heartRate, hrv, spo2, temperature, stress, source, recorded_at
            FROM historical_telemetry 
            WHERE astronaut_id = ?
            ORDER BY entry_id ASC
            LIMIT ?
            """,
            (astronaut_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


# ==========================================
# TRIAGE ALERTS CRUD (Module 3 Rule-Based Engine)
# ==========================================

def get_alerts(
    astronaut_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None
) -> List[Dict[str, Any]]:
    with get_db() as conn:
        query = "SELECT * FROM triage_alerts WHERE 1=1"
        params = []

        if astronaut_id:
            query += " AND astronaut_id = ?"
            params.append(astronaut_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC"
        rows = conn.execute(query, params).fetchall()

        alerts = []
        for r in rows:
            d = dict(r)
            d["contributing_measurements"] = json.loads(d["contributing_measurements"])
            d["escalation_steps"] = json.loads(d["escalation_steps"])
            alerts.append(d)
        return alerts


def get_alert_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM triage_alerts WHERE alert_id = ?", (alert_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["contributing_measurements"] = json.loads(d["contributing_measurements"])
        d["escalation_steps"] = json.loads(d["escalation_steps"])
        return d


def insert_triage_alert(
    alert_id: str,
    astronaut_id: str,
    rule_id: str,
    title: str,
    severity: str,
    trigger_reason: str,
    explanation: str,
    contributing_measurements: List[Dict[str, Any]],
    escalation_steps: List[str],
    status: str = "ACTIVE",
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    ts = timestamp or (datetime.utcnow().isoformat() + "Z")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO triage_alerts
            (alert_id, astronaut_id, rule_id, title, severity, status, trigger_reason, explanation, 
             contributing_measurements, escalation_steps, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (alert_id, astronaut_id, rule_id, title, severity, status, trigger_reason, explanation,
             json.dumps(contributing_measurements), json.dumps(escalation_steps), ts)
        )
    return get_alert_by_id(alert_id)


def resolve_alert(alert_id: str, user_id: str) -> bool:
    with get_db() as conn:
        cur = conn.execute(
            """
            UPDATE triage_alerts 
            SET status = 'RESOLVED', acknowledged_by = ?, resolved_at = ?
            WHERE alert_id = ?
            """,
            (user_id, datetime.utcnow().isoformat() + "Z", alert_id)
        )
        return cur.rowcount > 0


# ==========================================
# TEAMMATE ANOMALY DOCK CRUD (Palette 3)
# ==========================================

def insert_statistical_anomaly(
    anomaly_id: str,
    astronaut_id: str,
    metric_name: str,
    z_score: float,
    confidence_interval: float = 0.95
) -> bool:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO teammate_anomalies_dock
            (anomaly_id, astronaut_id, metric_name, z_score, confidence_interval, detected_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (anomaly_id, astronaut_id, metric_name, z_score, confidence_interval, datetime.utcnow().isoformat() + "Z")
        )
        return True
