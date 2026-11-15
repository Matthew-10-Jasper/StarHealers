from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class UnifiedSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "STARHEALERS — Unified Astronaut Health & Mission Operations Platform"
    VERSION: str = "3.0.0-UNIFIED"
    API_V1_STR: str = "/api/v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Base workspace path
    WORKSPACE_ROOT: Path = Path(r"E:\StarHealers")

    # Module database paths
    SUBA_DB_PATH: Path = Path(r"E:\StarHealers\StarHealers-Suba\backend\starhealers.db")
    MODULE4_DB_PATH: Path = Path(r"E:\StarHealers\module4_mission_intelligence\backend\starhealers_m4.db")
    MODULE5_DB_PATH: Path = Path(r"E:\StarHealers\module5_hazard_simulation\backend\starhealers_m5.db")
    MODULE6_DB_PATH: Path = Path(r"E:\StarHealers\starhealers_m6.db")
    MODULE7_DB_PATH: Path = Path(r"E:\StarHealers\module7_environment_radiation\backend\starhealers_m7.db")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = UnifiedSettings()
