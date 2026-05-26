import uuid
from datetime import datetime


class Task:
    def __init__(self, intent: str, goal: str):
        self.id = str(uuid.uuid4())[:8]
        self.intent = intent
        self.goal = goal
        self.created_at = datetime.now()
        self.steps = []
        self.completed = False

    def add_step(self, step: str):
        self.steps.append({"step": step, "done": False})

    def complete_step(self, index: int):
        if 0 <= index < len(self.steps):
            self.steps[index]["done"] = True

    def is_complete(self):
        return all(s["done"] for s in self.steps) and len(self.steps) > 0


class TaskManager:
    def __init__(self):
        self.active_tasks = []
        self.completed_tasks = []

    def create_task(self, intent: str, goal: str) -> Task:
        task = Task(intent, goal)
        self.active_tasks.append(task)
        return task

    def complete_task(self, task_id: str):
        for task in self.active_tasks:
            if task.id == task_id:
                task.completed = True
                self.active_tasks.remove(task)
                self.completed_tasks.append(task)
                return task
        return None

    def current_task(self):
        return self.active_tasks[0] if self.active_tasks else None
