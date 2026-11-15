from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "STARHEALERS — MODULE 7: Space Environment & Radiation"
    MODULE_ID: str = "MODULE_7"
    MODULE_NAME: str = "Space Environment & Radiation"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8007

    DATABASE_URL: str = "sqlite:///E:/StarHealers/module7_environment_radiation/backend/starhealers_m7.db"

    # Upstream integration endpoints
    MODULE4_API_URL: str = "http://127.0.0.1:8004"
    MODULE5_API_URL: str = "http://127.0.0.1:8005"

    # Radiation Limits (NASA Standard 3001)
    RADIATION_30_DAY_LIMIT_MSV: float = 250.0
    RADIATION_CAREER_LIMIT_MSV: float = 1000.0

    # CO2 Limits (ISS Environmental Control)
    CO2_WARNING_THRESHOLD_MMHG: float = 3.0
    CO2_CRITICAL_THRESHOLD_MMHG: float = 5.0

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()

