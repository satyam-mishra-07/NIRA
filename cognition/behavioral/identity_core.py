class IdentityCore:
    __slots__ = ("__traits",)

    def __init__(self):
        self.__traits = {
            "grounded": True,
            "calm": True,
            "observant": True,
            "subtle_humor": True,
            "emotionally_stable": True,
            "non_theatrical": True,
        }

    @property
    def traits(self):
        return dict(self.__traits)

    def assert_identity(self, prompt: str) -> str:
        section = "\n\nIDENTITY CORE:"
        for trait in self.__traits:
            section += f"\n- {trait.replace('_', ' ').title()}"
        return prompt + section
