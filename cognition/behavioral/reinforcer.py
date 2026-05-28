from cognition.habits.confidence_engine import ConfidenceEngine
from config.settings import BEHAVIORAL_LEARNING_RATE


class ContextualReinforcer:
    def __init__(self, confidence_engine: ConfidenceEngine):
        self.engine = confidence_engine

    def compute_reinforcement(
        self, signal_strength: float, current_confidence: float
    ) -> float:
        if signal_strength <= 0.0:
            return 0.0

        effective_rate = BEHAVIORAL_LEARNING_RATE * signal_strength
        delta = effective_rate * (1.0 - current_confidence)
        return round(delta, 4)
