from __future__ import annotations

from cognition.memory.retriever import MemoryRetriever
from cognition.memory.injector import MemoryInjector


class MemoryOrchestrator:
    MIN_INTERACTIONS = 5

    def __init__(
        self,
        retriever: MemoryRetriever,
        injector: MemoryInjector,
    ):
        self.retriever = retriever
        self.injector = injector

    def retrieve(self, context: dict, interaction_count: int) -> str:
        if interaction_count < self.MIN_INTERACTIONS:
            return ""

        memories = self.retriever.retrieve(context)
        if not memories:
            return ""

        return self.injector.format(memories)
