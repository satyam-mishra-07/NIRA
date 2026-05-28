import json
from pathlib import Path
from config.constants import BEHAVIORAL_MEMORY_FILE, REFLECTION_MEMORY_FILE


class BehavioralMemoryStore:
    def __init__(self):
        self.file_path = BEHAVIORAL_MEMORY_FILE

    def load(self) -> dict:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"preferences": [], "version": 1}

    def save(self, data: dict):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


class ReflectionMemoryStore:
    def __init__(self):
        self.file_path = REFLECTION_MEMORY_FILE

    def load(self) -> dict:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"observations": [], "version": 1}

    def save(self, data: dict):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
