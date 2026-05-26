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
        self._hinglish_map = {
            "kar raha": " is ", "kar rahi": " is ", "nahi": " not ",
            "kaam": " work ", "karo": " do ", "aa raha": " getting ",
            "kya": " what ", "kyu": " why ", "kaise": " how ",
            "ye": " this ", "vo": " that ", "mera": " my ",
            "chahiye": " need ", "dikhao": " show ", "banao": " build ",
            "karte hain": " let's ", "karna": " do ", "likho": " write ",
            "padho": " read ", "kholo": " open ", "dhundo": " search ",
            "batao": " tell ", "samjhao": " explain ",
        }

    def _normalize_hinglish(self, text: str) -> str:
        normalized = text.lower()
        for hing, eng in sorted(self._hinglish_map.items(), key=lambda x: -len(x[0])):
            normalized = normalized.replace(hing, eng)
        return normalized

    def _requires_reasoning(self, intent_name: str) -> bool:
        return intent_name in {
            "coding_help", "tool_execution", "browser_request",
            "file_operation", "productivity", "system",
        }

    def _classify_internal(self, text: str) -> dict:
        scores = {}
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            if score > 0:
                scores[intent] = score

        casual_score = sum(1 for p in self.casual_patterns if re.search(p, text))

        if not scores and casual_score > 0:
            return {"intent": "casual_chat", "confidence": 0.6, "sub_intent": None, "requires_reasoning": False}
        if not scores:
            return {"intent": "casual_chat", "confidence": 0.3, "sub_intent": None, "requires_reasoning": False}

        best = max(scores, key=scores.get)
        confidence = min(0.5 + (scores[best] / sum(scores.values())) * 0.4, 0.95)
        return {"intent": best, "confidence": round(confidence, 2), "sub_intent": None, "requires_reasoning": self._requires_reasoning(best)}

    def classify(self, message: str) -> dict:
        original_result = self._classify_internal(message.lower())
        normalized = self._normalize_hinglish(message)
        if normalized != message.lower():
            normalized_result = self._classify_internal(normalized)
            if normalized_result["confidence"] > original_result["confidence"]:
                return normalized_result
        return original_result
