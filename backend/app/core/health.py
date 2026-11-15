import os
import sqlite3
from typing import Dict, Any
from app.core.config import settings

def check_system_health() -> Dict[str, Any]:
    health_status: Dict[str, Any] = {
        "status": "HEALTHY",
        "system": "STARHEALERS UNIFIED PLATFORM",
        "version": settings.VERSION,
        "modules": {},
        "databases": {}
    }

    db_checks = {
        "suba_modules123": settings.SUBA_DB_PATH,
        "module4_intelligence": settings.MODULE4_DB_PATH,
        "module5_simulation": settings.MODULE5_DB_PATH,
        "module6_circadian": settings.MODULE6_DB_PATH,
        "module7_environment": settings.MODULE7_DB_PATH
    }

    all_dbs_ok = True
    for name, path in db_checks.items():
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(str(path))
                c = conn.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables_cnt = len(c.fetchall())
                conn.close()
                health_status["databases"][name] = {
                    "connected": True,
                    "path": str(path),
                    "tables_count": tables_cnt
                }
            except Exception as e:
                all_dbs_ok = False
                health_status["databases"][name] = {
                    "connected": False,
                    "error": str(e)
                }
        else:
            all_dbs_ok = False
            health_status["databases"][name] = {
                "connected": False,
                "error": "File does not exist"
            }

    # Module readiness
    modules_list = [
        ("module1_vitals", "Astronaut Health & Continuous Physiological Readings"),
        ("module2_bodymap", "Anatomical Body Map & Regional Health Telemetry"),
        ("module3_triage", "Intelligent Clinical Triage & Flight Rule Engine"),
        ("module4_mission_intelligence", "Mission Environment Intelligence & Context Management"),
        ("module5_hazard_simulation", "Space Hazard Simulation Engines (Rad, CO2, Sleep)"),
        ("module6_circadian_fatigue", "Circadian Rhythm, Fatigue, Stress & PVT Test Battery"),
        ("module7_space_environment", "Space Environment, Radiation Limits & Life Support")
    ]

    for mod_id, mod_name in modules_list:
        health_status["modules"][mod_id] = {
            "name": mod_name,
            "operational": True,
            "status": "ONLINE"
        }

    if not all_dbs_ok:
        health_status["status"] = "DEGRADED"

    return health_status
