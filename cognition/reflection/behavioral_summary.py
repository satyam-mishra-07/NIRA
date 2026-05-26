from datetime import datetime

class BehavioralSummary:
    def __init__(self):
        self.snapshots = []

    def create_snapshot(self, mood: dict, habits: list, intent: dict) -> dict:
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "mood": mood,
            "active_habits": [h for h in habits if h.get("confidence", 0) > 0.5],
            "last_intent": intent,
        }
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 50:
            self.snapshots.pop(0)
        return snapshot
