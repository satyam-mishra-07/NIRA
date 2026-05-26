import json
from pathlib import Path
from config.constants import HABITS_FILE

class HabitMemory:
    def __init__(self):
        self.file_path = HABITS_FILE

    def load(self) -> list:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def save(self, habits: list):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(habits, f, indent=2)
