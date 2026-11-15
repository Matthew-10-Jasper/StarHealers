import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "STARHEALERS Mission Environment Intelligence"
    MODULE_NAME: str = "MODULE 4 - ADAPTIVE MISSION CONTEXT MANAGER"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(r"E:\StarHealers\module4_mission_intelligence")
    PROFILES_DIR: Path = BASE_DIR / "mission_profiles"
    CONTRACTS_DIR: Path = BASE_DIR / "integration_contracts"
    DATABASE_PATH: Path = BASE_DIR / "backend" / "starhealers_m4.db"
    
    # SQLite Configuration
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DATABASE_PATH.as_posix()}"
    
    # Telemetry and Staleness Bounds (seconds)
    TELEMETRY_STALE_THRESHOLD_SECONDS: float = 300.0  # 5 minutes
    TELEMETRY_EXPIRED_THRESHOLD_SECONDS: float = 1800.0 # 30 minutes
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Default Mission
    DEFAULT_MISSION_ID: str = "ARES_VOYAGER_MARS"

settings = Settings()
