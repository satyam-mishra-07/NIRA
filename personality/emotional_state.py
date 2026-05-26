class NiraEmotionalState:
    def __init__(self):
        self.current_state = {
            "responsiveness": "normal",
            "verbosity": "concise",
            "warmth": "moderate",
        }

    def apply_mood_influence(self, mood: dict):
        mood_name = mood.get("mood", "neutral")
        confidence = mood.get("confidence", 0.0)

        if confidence < 0.3:
            return

        if mood_name == "stressed":
            self.current_state["verbosity"] = "minimal"
            self.current_state["warmth"] = "supportive"
        elif mood_name == "frustrated":
            self.current_state["verbosity"] = "concise"
            self.current_state["warmth"] = "patient"
        elif mood_name == "curious":
            self.current_state["verbosity"] = "detailed"
            self.current_state["warmth"] = "engaged"
        elif mood_name == "playful":
            self.current_state["verbosity"] = "normal"
            self.current_state["warmth"] = "warm"
        else:
            self.current_state["verbosity"] = "concise"
            self.current_state["warmth"] = "moderate"

    def get_style(self) -> dict:
        return dict(self.current_state)
