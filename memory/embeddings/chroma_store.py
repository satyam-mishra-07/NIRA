class ChromaStore:
    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.initialized = True

    def store(self, text: str, metadata: dict = None):
        pass

    def search(self, query: str, n: int = 5) -> list:
        return []
