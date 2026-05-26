from datetime import datetime
from cognition.habits.confidence_engine import ConfidenceEngine
from cognition.habits.pattern_detector import PatternDetector
from config.constants import HABIT_PATTERNS

class HabitObserver:
    def __init__(self, confidence_engine: ConfidenceEngine, pattern_detector: PatternDetector):
        self.confidence_engine = confidence_engine
        self.pattern_detector = pattern_detector
        self.pattern_keywords = HABIT_PATTERNS
        self.observation_count = 0
        self._hinglish_map = {
            "kar raha": " ", "karo": " do ", "likho": " write ",
            "code": " code ", "gaana": " music ", "music": " music ",
            "function": " function ", "error": " error ", "debug": " debug ",
            "kaise ho": " how are you ", "kya chal raha": " what's up ",
        }

    def _normalize(self, text: str) -> str:
        normalized = text.lower()
        for hing, eng in sorted(self._hinglish_map.items(), key=lambda x: -len(x[0])):
            normalized = normalized.replace(hing, eng)
        return normalized

    def observe(self, message: str, context: dict = None) -> list:
        self.observation_count += 1
        target = self._normalize(message)
        hour = datetime.now().hour
        observations = []

        for pattern, keywords in self.pattern_keywords.items():
            if pattern == "late_night_work":
                if hour >= 22 or hour <= 5:
                    delta = self.confidence_engine.compute_delta(pattern, 0.12)
                    observations.append({
                        "pattern": pattern,
                        "confidence_delta": delta,
                        "evidence": f"active at {hour}:00",
                    })
            else:
                matches = sum(1 for kw in keywords if kw in target)
                if matches > 0:
                    delta = self.confidence_engine.compute_delta(pattern, 0.05 * matches)
                    observations.append({
                        "pattern": pattern,
                        "confidence_delta": delta,
                        "evidence": f"keyword matches: {matches}",
                    })

        return observations
