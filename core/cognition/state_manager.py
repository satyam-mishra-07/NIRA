class CognitiveStateManager:
    def __init__(self):
        self.current_mood = {"mood": "neutral", "confidence": 0.0, "reason": "initial"}
        self.active_habits = []
        self.current_intent = {"intent": "casual_chat", "confidence": 0.0, "sub_intent": None}
        self.interaction_count = 0

    def update_mood(self, mood_result: dict):
        self.current_mood = mood_result

    def update_habits(self, habits: list):
        self.active_habits = habits

    def update_intent(self, intent_result: dict):
        self.current_intent = intent_result

    def increment_interaction(self):
        self.interaction_count += 1

    def get_state_snapshot(self) -> dict:
        return {
            "mood": self.current_mood,
            "habits": self.active_habits,
            "intent": self.current_intent,
            "interactions": self.interaction_count,
        }
