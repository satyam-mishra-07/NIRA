from cognition.habits.confidence_engine import ConfidenceEngine

class HabitReinforcement:
    def __init__(self, confidence_engine: ConfidenceEngine):
        self.engine = confidence_engine

    def reinforce(self, habit: dict, observation: dict) -> dict:
        delta = observation.get("confidence_delta", 0.0)
        new_confidence = self.engine.update_confidence(
            habit.get("confidence", 0.0), delta
        )
        habit["confidence"] = new_confidence
        habit["last_reinforced"] = observation.get("evidence", "")
        return habit

    def decay_habits(self, habits: list) -> list:
        for habit in habits:
            habit["confidence"] = self.engine.decay(habit["confidence"])
        return habits
