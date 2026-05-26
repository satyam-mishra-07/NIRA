import json
from pathlib import Path
from config.constants import PROFILE_FILE

class ProfileManager:
    def __init__(self):
        self.file_path = PROFILE_FILE
        self.profile = self._load_default()

    def _load_default(self) -> dict:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "name": "Satyam",
            "interests": ["backend development", "AI", "anime", "gaming", "music"],
            "communication_preference": "natural",
            "preferred_tone": "casual",
            "known_languages": ["English", "Hindi"],
            "interaction_count": 0,
        }

    def get(self, key: str, default=None):
        return self.profile.get(key, default)

    def set(self, key: str, value):
        self.profile[key] = value
        self._save()

    def increment_interactions(self):
        self.profile["interaction_count"] = self.profile.get("interaction_count", 0) + 1
        self._save()

    def _save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2)
