from memory.emotional.emotional_memory import EmotionalMemory

class MoodEmotionalMemory:
    def __init__(self, emotional_memory: EmotionalMemory):
        self.emotional_memory = emotional_memory

    def store_mood(self, mood_result: dict):
        self.emotional_memory.add_entry(mood_result)

    def get_recent_tone_trend(self, count: int = 5) -> list:
        return self.emotional_memory.get_recent(count)
