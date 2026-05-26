import json
from datetime import datetime
from pathlib import Path
from config.constants import MEMORY_DIR

PRUNE_THRESHOLD = 500      # start pruning when log exceeds this
KEEP_RECENT = 300          # keep this many recent messages after pruning
ARCHIVE_CHUNK = 200        # compress this many oldest messages into a summary


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
        if len(self.messages) > PRUNE_THRESHOLD:
            self._prune()
        self._save()

    def _prune(self):
        """
        Compress the oldest ARCHIVE_CHUNK messages into a single summary entry.
        Keep the rest as active history.
        """
        to_archive = self.messages[:ARCHIVE_CHUNK]
        self.messages = self.messages[ARCHIVE_CHUNK:]

        # Build a lightweight summary of what's being compressed
        topics = set()
        participants = set()
        for msg in to_archive:
            participants.add(msg.get("role", "unknown"))
            content = msg.get("content", "")
            if "?" in content:
                topics.add("questions")
            if "```" in content or "def " in content or "error" in content.lower():
                topics.add("coding")
            if any(w in content.lower() for w in ["file", "folder", "create", "delete"]):
                topics.add("file_operations")
            if any(w in content.lower() for w in ["plan", "task", "todo", "goal"]):
                topics.add("productivity")

        first_ts = to_archive[0].get("timestamp", "unknown")
        last_ts = to_archive[-1].get("timestamp", "unknown")

        summary_entry = {
            "role": "system",
            "content": (
                f"[ARCHIVED CONTEXT — {len(to_archive)} messages from {first_ts} to {last_ts}. "
                f"Topics covered: {', '.join(topics) if topics else 'general conversation'}. "
                f"This is a compressed summary of older history.]"
            ),
            "timestamp": datetime.now().isoformat(),
            "archived": True,
        }

        # Place the summary at the front so the LLM sees it as oldest context
        self.messages.insert(0, summary_entry)

    def get_all(self) -> list:
        return self.messages

    def get_recent(self, count: int = 20) -> list:
        return self.messages[-count:]

    def get_active(self) -> list:
        """Returns only non-archived messages — for display or analysis."""
        return [m for m in self.messages if not m.get("archived", False)]

    def clear(self):
        self.messages.clear()
        self._save()

    def _save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=2)