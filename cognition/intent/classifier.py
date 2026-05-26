import re

class IntentClassifier:
    def __init__(self):
        self.patterns = {
            "coding_help": [
                r"\b(code|debug|error|function|class|implement|bug|fix|compile|syntax|refactor)\b",
                r"```", r"def |class |import ",
            ],
            "file_operation": [
                r"\b(create|delete|rename|move|copy|read|write|save|open|file|folder|directory)\b",
                r"\.py|\.js|\.ts|\.txt|\.json|\.md",
            ],
            "browser_request": [
                r"\b(search|google|browse|open website|look up|find|research|wikipedia|url)\b",
            ],
            "productivity": [
                r"\b(plan|task|todo|schedule|remind|organize|project|deadline|goal|priority)\b",
            ],
            "system": [
                r"\b(status|setting|config|update|version|restart|shutdown|what can you)\b",
            ],
            "tool_execution": [
                r"\b(run|execute|terminal|command|pip|npm|git|bash|shell)\b",
            ],
        }
        self.casual_patterns = [
            r"\b(hello|hi|hey|how are you|what's up|good morning|thanks|bye)\b",
        ]

    def classify(self, message: str) -> dict:
        message_lower = message.lower()
        scores = {}

        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                scores[intent] = score

        casual_score = sum(1 for p in self.casual_patterns if re.search(p, message_lower))

        if not scores and casual_score > 0:
            return {"intent": "casual_chat", "confidence": 0.6, "sub_intent": None}

        if not scores:
            return {"intent": "casual_chat", "confidence": 0.3, "sub_intent": None}

        best = max(scores, key=scores.get)
        confidence = min(0.5 + (scores[best] / sum(scores.values())) * 0.4, 0.95)

        return {
            "intent": best,
            "confidence": round(confidence, 2),
            "sub_intent": None,
        }
