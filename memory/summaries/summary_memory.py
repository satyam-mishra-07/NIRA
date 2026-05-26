import json
from datetime import datetime
from pathlib import Path
from config.constants import SUMMARIES_FILE

class SummaryMemory:
    def __init__(self):
        self.file_path = SUMMARIES_FILE
        self.summaries = self._load()

    def _load(self) -> list:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def add_summary(self, summary: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
        }
        self.summaries.append(entry)
        if len(self.summaries) > 20:
            self.summaries = self.summaries[-20:]
        self._save()

    def get_recent(self, count: int = 3) -> list:
        return self.summaries[-count:]

    def _save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.summaries, f, indent=2)
