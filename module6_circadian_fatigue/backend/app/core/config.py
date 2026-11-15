from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "STARHEALERS — MODULE 6: Circadian, Fatigue & Stress"
    MODULE_ID: str = "MODULE_6"
    MODULE_NAME: str = "Circadian, Fatigue & Stress"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8006

    DATABASE_URL: str = "sqlite:///./starhealers_m6.db"

    # Upstream integration endpoints
    MODULE4_API_URL: str = "http://127.0.0.1:8004"
    MODULE5_API_URL: str = "http://127.0.0.1:8005"

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

