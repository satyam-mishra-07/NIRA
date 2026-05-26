from config.settings import HABIT_LEARNING_RATE, HABIT_DECAY_RATE, HABIT_CONFIDENCE_THRESHOLD

class ConfidenceEngine:
    def __init__(self):
        self.learning_rate = HABIT_LEARNING_RATE
        self.decay_rate = HABIT_DECAY_RATE
        self.threshold = HABIT_CONFIDENCE_THRESHOLD

    def compute_delta(self, pattern: str, signal_strength: float) -> float:
        return round(signal_strength * self.learning_rate, 4)

    def update_confidence(self, current: float, delta: float) -> float:
        updated = current + delta
        return round(min(max(updated, 0.0), 1.0), 4)

    def decay(self, current: float) -> float:
        return round(max(current - self.decay_rate, 0.0), 4)

    def is_confirmed(self, confidence: float) -> bool:
        return confidence >= self.threshold
