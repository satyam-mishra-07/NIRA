import json
from datetime import datetime

class ConversationSummarizer:
    def __init__(self):
        self.summary_history = []

    def summarize(self, messages: list) -> str:
        if not messages:
            return ""
        topics = set()
        for msg in messages[-10:]:
            content = msg.get("content", "")
            if "?" in content:
                topics.add("questions")
            if "```" in content or "def " in content:
                topics.add("coding")
            if len(content.split()) < 5:
                topics.add("short_replies")

        summary = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
            "topics": list(topics),
            "compressed": f"Conversation over {len(messages)} messages. Topics: {', '.join(topics) if topics else 'general chat'}.",
        }
        return json.dumps(summary)
