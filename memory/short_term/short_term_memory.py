import json
from datetime import datetime
from config.settings import SHORT_TERM_WINDOW_SIZE

class ShortTermMemory:
    def __init__(self, window_size: int = None):
        self.window_size = window_size or SHORT_TERM_WINDOW_SIZE
        self.messages = []

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._trim()

    def _trim(self):
        if len(self.messages) > self.window_size:
            self.messages = self.messages[-self.window_size:]

    def get_recent_context(self, count: int = None) -> list:
        c = count or self.window_size
        return self.messages[-c:]

    def get_messages_for_llm(self) -> list:
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def clear(self):
        self.messages.clear()
