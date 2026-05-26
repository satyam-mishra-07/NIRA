class PatternDetector:
    def __init__(self):
        self.patterns = {}

    def register(self, name: str, requires: list):
        self.patterns[name] = {"requires": requires, "active": False}

    def detect(self, observations: list) -> list:
        detected = []
        observed_patterns = {o["pattern"] for o in observations}

        for name, config in self.patterns.items():
            if all(r in observed_patterns for r in config.get("requires", [])):
                detected.append(name)

        return detected
