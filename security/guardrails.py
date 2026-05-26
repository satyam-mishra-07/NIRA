class Guardrails:
    def __init__(self):
        self.blocked_topics = [
            "self-harm", "suicide", "illegal drugs",
            "weapons manufacturing", "exploits for illegal access",
        ]

    def check_output(self, text: str) -> dict:
        text_lower = text.lower()
        for topic in self.blocked_topics:
            if topic in text_lower:
                return {
                    "allowed": False,
                    "reason": f"response references blocked topic: {topic}",
                }
        return {"allowed": True, "reason": None}

    def filter_response(self, text: str) -> str:
        result = self.check_output(text)
        if not result["allowed"]:
            return "I cannot provide information on that topic."
        return text
