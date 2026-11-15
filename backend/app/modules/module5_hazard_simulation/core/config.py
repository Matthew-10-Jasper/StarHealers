from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "STARHEALERS — MODULE 5: Space Hazard Simulation Engine"
    MODULE_ID: str = "MODULE_5"
    MODULE_NAME: str = "Space Hazard Simulation Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server configuration (Default port 8005 to run side-by-side with Module 4 on 8004)
    HOST: str = "127.0.0.1"
    PORT: int = 8005
    
    # Database
    DATABASE_URL: str = "sqlite:///E:/StarHealers/module5_hazard_simulation/backend/starhealers_m5.db"
    
    # Module 4 Integration
    MODULE4_API_URL: str = "http://127.0.0.1:8004"
    
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
    
    # Simulation defaults
    DEFAULT_TIMESTEP_HOURS: float = 1.0
    DEFAULT_MISSION_DURATION_HOURS: float = 168.0  # 7 days
    MAX_MISSION_DURATION_HOURS: float = 8760.0    # 1 year

settings = Settings()

