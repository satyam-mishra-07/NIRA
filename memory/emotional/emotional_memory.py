import json
from datetime import datetime
from pathlib import Path
from config.constants import EMOTIONAL_STATE_FILE

class EmotionalMemory:
    def __init__(self):
        self.file_path = EMOTIONAL_STATE_FILE
        self.entries = self._load()

    def _load(self) -> list:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def add_entry(self, mood_result: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mood": mood_result.get("mood", "neutral"),
            "confidence": mood_result.get("confidence", 0.0),
            "reason": mood_result.get("reason", ""),
        }
        self.entries.append(entry)
        if len(self.entries) > 50:
            self.entries = self.entries[-50:]
        self._save()

    def get_recent(self, count: int = 5) -> list:
        return self.entries[-count:]

    def get_tone_trend(self) -> dict:
        if not self.entries:
            return {"trend": "neutral", "confidence": 0.0}
        recent = self.entries[-10:]
        moods = [e["mood"] for e in recent]
        most_common = max(set(moods), key=moods.count)
        return {"trend": most_common, "confidence": round(moods.count(most_common) / len(moods), 2)}

    def _save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)
