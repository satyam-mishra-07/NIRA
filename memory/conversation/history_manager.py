from memory.short_term.short_term_memory import ShortTermMemory
from config.settings import MAX_CONTEXT_MESSAGES

class HistoryManager:
    def __init__(self, short_term: ShortTermMemory):
        self.short_term = short_term
        self.max_messages = MAX_CONTEXT_MESSAGES

    def get_context(self) -> list:
        messages = self.short_term.get_messages_for_llm()
        if len(messages) > self.max_messages:
            messages = messages[-self.max_messages:]
        return messages

    def should_summarize(self) -> bool:
        return len(self.short_term.messages) >= self.short_term.window_size * 0.8
