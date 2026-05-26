class MoodStateTracker:
    def __init__(self, decay_factor: float = 0.3):
        self.current = {"mood": "neutral", "confidence": 0.0, "reason": "initial"}
        self.history = []
        self.decay_factor = decay_factor

    def update(self, new_mood: dict):
        prev_confidence = self.current.get("confidence", 0.0)
        new_confidence = new_mood.get("confidence", 0.0)

        if new_confidence < prev_confidence * self.decay_factor:
            blended = self.current
        else:
            blended = {
                "mood": new_mood["mood"] if new_confidence > prev_confidence else self.current["mood"],
                "confidence": max(new_confidence, prev_confidence * (1 - self.decay_factor)),
                "reason": new_mood.get("reason", self.current.get("reason", "")),
            }

        self.history.append(blended)
        if len(self.history) > 20:
            self.history.pop(0)
        self.current = blended
        return blended
