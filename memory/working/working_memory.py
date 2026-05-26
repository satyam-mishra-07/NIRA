from config.settings import WORKING_MEMORY_MAX_GOALS

class WorkingMemory:
    def __init__(self):
        self.current_task = ""
        self.active_file = ""
        self.goals = []
        self.recent_tools = []
        self.max_goals = WORKING_MEMORY_MAX_GOALS

    def update_from_input(self, user_input: str):
        if not self.current_task:
            words = user_input.split()
            if len(words) > 3:
                self.current_task = " ".join(words[:5]) + "..."

    def set_task(self, task: str):
        self.current_task = task

    def add_goal(self, goal: str):
        if goal not in self.goals:
            self.goals.append(goal)
            if len(self.goals) > self.max_goals:
                self.goals.pop(0)

    def clear_task(self):
        self.current_task = ""

    def to_dict(self) -> dict:
        return {
            "current_task": self.current_task,
            "active_file": self.active_file,
            "goals": self.goals,
        }
