from memory.habits.habit_memory import HabitMemory

class HabitStore:
    def __init__(self, habit_memory: HabitMemory):
        self.habit_memory = habit_memory

    def get_all(self) -> list:
        return self.habit_memory.load()

    def save(self, habits: list):
        self.habit_memory.save(habits)

    def update_from_observations(self, observations: list):
        habits = self.get_all()
        habit_map = {h["habit"]: h for h in habits}

        for obs in observations:
            pattern = obs["pattern"]
            if pattern not in habit_map:
                habit_map[pattern] = {
                    "habit": pattern,
                    "confidence": 0.0,
                    "first_observed": None,
                    "last_reinforced": None,
                }
            delta = obs.get("confidence_delta", 0.0)
            current = habit_map[pattern]["confidence"]
            habit_map[pattern]["confidence"] = round(min(current + delta, 1.0), 4)
            habit_map[pattern]["last_reinforced"] = obs.get("evidence", "")

        self.save(list(habit_map.values()))
