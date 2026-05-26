from config.constants import MOOD_KEYWORDS
import re

class MoodAnalyzer:
    def __init__(self):
        self.keywords = MOOD_KEYWORDS

    def analyze(self, message: str, context: dict = None) -> dict:
        message_lower = message.lower()
        scores = {}
        total_matches = 0

        for mood, words in self.keywords.items():
            score = 0
            for word in words:
                if word.lower() in message_lower:
                    score += 1
                    total_matches += 1
            if score > 0:
                scores[mood] = score

        if not scores:
            if message.endswith("?"):
                return {"mood": "curious", "confidence": 0.35, "reason": "question detected"}
            if len(message.split()) < 3:
                return {"mood": "neutral", "confidence": 0.3, "reason": "short message"}
            return {"mood": "neutral", "confidence": 0.2, "reason": "no strong signals"}

        best_mood = max(scores, key=scores.get)
        confidence = min(0.4 + (scores[best_mood] / total_matches) * 0.5, 0.9)
        reason = f"keyword match: {best_mood}"

        return {"mood": best_mood, "confidence": round(confidence, 2), "reason": reason}
