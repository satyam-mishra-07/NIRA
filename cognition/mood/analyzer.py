from config.constants import MOOD_KEYWORDS
import re

class MoodAnalyzer:
    def __init__(self):
        self.keywords = MOOD_KEYWORDS
        self._hinglish_map = {
            "kar raha": " ", "kar rahi": " ", "nahi": " not ",
            "kaam": " work ", "kya": " what ", "kyu": " why ",
            "kaise": " how ", "ye": " this ", "vo": " that ",
            "galat": " wrong ", "aacha": " good ", "sahi": " correct ",
            "thak gaya": " tired ", "neend": " sleepy ",
            "mazaak": " joke ", "hasi": " laugh ",
            "jaldi": " urgent ", "pressure": " stress ",
        }

    def _normalize(self, text: str) -> str:
        normalized = text.lower()
        for hing, eng in sorted(self._hinglish_map.items(), key=lambda x: -len(x[0])):
            normalized = normalized.replace(hing, eng)
        return normalized

    def analyze(self, message: str, context: dict = None) -> dict:
        target = self._normalize(message)
        scores = {}
        total_matches = 0

        for mood, words in self.keywords.items():
            score = 0
            for word in words:
                if word.lower() in target:
                    score += 1
                    total_matches += 1
            if score > 0:
                scores[mood] = score

        if not scores:
            if target.endswith("?"):
                return {"mood": "curious", "confidence": 0.35, "reason": "question detected"}
            if len(target.split()) < 3:
                return {"mood": "neutral", "confidence": 0.3, "reason": "short message"}
            return {"mood": "neutral", "confidence": 0.2, "reason": "no strong signals"}

        best_mood = max(scores, key=scores.get)
        confidence = min(0.4 + (scores[best_mood] / total_matches) * 0.5, 0.9)
        reason = f"keyword match: {best_mood}"

        return {"mood": best_mood, "confidence": round(confidence, 2), "reason": reason}
