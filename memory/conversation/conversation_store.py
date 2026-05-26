import json
from datetime import datetime
from pathlib import Path
from config.constants import MEMORY_DIR

class ConversationStore:
    def __init__(self):
        self.file_path = MEMORY_DIR / "conversation" / "conversation_log.json"
        self.messages = self._load()

    def _load(self) -> list:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def append(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def get_all(self) -> list:
        return self.messages

    def get_recent(self, count: int = 20) -> list:
        return self.messages[-count:]

    def clear(self):
        self.messages.clear()
        self._save()

    def _save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=2)
