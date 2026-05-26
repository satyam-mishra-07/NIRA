import time
from datetime import datetime

class ActivityContext:
    def __init__(self):
        self.last_interaction = time.time()
        self.interaction_count = 0
        self.session_start = datetime.now()

    def record_interaction(self):
        self.last_interaction = time.time()
        self.interaction_count += 1

    def idle_seconds(self) -> float:
        return time.time() - self.last_interaction

    def get_session_info(self) -> dict:
        return {
            "session_start": self.session_start.isoformat(),
            "interaction_count": self.interaction_count,
            "idle_seconds": round(self.idle_seconds(), 1),
        }
