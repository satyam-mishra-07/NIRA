class UserContext:
    def __init__(self):
        self.observed_preferences = {}
        self.communication_style = {
            "avg_message_length": 0,
            "preferred_tone": "neutral",
            "uses_code": False,
        }
        self.message_count = 0
        self.total_words = 0

    def observe_message(self, message: str):
        self.message_count += 1
        self.total_words += len(message.split())
        self.communication_style["avg_message_length"] = round(
            self.total_words / self.message_count, 1
        )
        if "```" in message or "def " in message or "class " in message:
            self.communication_style["uses_code"] = True

    def get_profile(self) -> dict:
        return {
            "communication_style": self.communication_style,
            "observed_preferences": self.observed_preferences,
            "total_interactions": self.message_count,
        }
