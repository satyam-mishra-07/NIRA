class Scheduler:
    def __init__(self):
        self.tasks = []

    def register(self, interval_seconds: float, callback):
        self.tasks.append((interval_seconds, callback))

    def start(self):
        pass

    def stop(self):
        pass
