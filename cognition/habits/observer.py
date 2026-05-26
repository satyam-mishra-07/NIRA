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

    def observe(self, message: str, context: dict = None) -> list:
        self.observation_count += 1
        message_lower = message.lower()
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
                matches = sum(1 for kw in keywords if kw in message_lower)
                if matches > 0:
                    delta = self.confidence_engine.compute_delta(pattern, 0.05 * matches)
                    observations.append({
                        "pattern": pattern,
                        "confidence_delta": delta,
                        "evidence": f"keyword matches: {matches}",
                    })

        return observations
