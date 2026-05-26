from memory.summaries.summary_memory import SummaryMemory
from cognition.reflection.summarizer import ConversationSummarizer

class MemoryReflection:
    def __init__(self, summary_memory: SummaryMemory, summarizer: ConversationSummarizer):
        self.summary_memory = summary_memory
        self.summarizer = summarizer

    def reflect(self, short_term_messages: list):
        if len(short_term_messages) >= 10:
            summary = self.summarizer.summarize(short_term_messages)
            self.summary_memory.add_summary(summary)
