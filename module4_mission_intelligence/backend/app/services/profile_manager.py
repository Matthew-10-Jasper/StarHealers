import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from app.core.config import settings
from app.schemas.mission_profile import MissionProfile

logger = logging.getLogger("MissionProfileManager")

class MissionProfileManager:
    """Component A: Mission Profile Manager.
    Loads, validates, and manages structured mission profiles from configuration files.
    Allows dynamic registration of new profiles without architecture modification.
    """
    def __init__(self, profiles_dir: Optional[Path] = None):
        self.profiles_dir = profiles_dir or settings.PROFILES_DIR
        self._profiles_cache: Dict[str, MissionProfile] = {}
        self.load_all_profiles()

    def load_all_profiles(self) -> Dict[str, MissionProfile]:
        """Scans profiles directory and parses all valid JSON mission profile files."""
        if not self.profiles_dir.exists():
            logger.warning(f"Profiles directory does not exist: {self.profiles_dir}")
            return {}

        loaded = {}
        for file_path in self.profiles_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profile = MissionProfile.model_validate(data)
                    loaded[profile.mission_id] = profile
                    logger.info(f"Loaded mission profile: {profile.mission_id} from {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load profile from {file_path}: {e}")
        self._profiles_cache = loaded
        return loaded

    def get_profile(self, mission_id: str) -> Optional[MissionProfile]:
        """Retrieves a loaded mission profile by ID."""
        if mission_id not in self._profiles_cache:
            self.load_all_profiles()
        return self._profiles_cache.get(mission_id)

    def list_profiles(self) -> List[MissionProfile]:
        """Returns list of all available mission profiles."""
        if not self._profiles_cache:
            self.load_all_profiles()
        return list(self._profiles_cache.values())

    def register_profile(self, profile_data: dict) -> MissionProfile:
        """Dynamically registers or updates a mission profile, validating schema."""
        profile = MissionProfile.model_validate(profile_data)
        file_path = self.profiles_dir / f"{profile.mission_id.lower()}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile.model_dump(mode="json"), f, indent=2)
        self._profiles_cache[profile.mission_id] = profile
        return profile

