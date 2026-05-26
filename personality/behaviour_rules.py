class BehaviourRules:
    MAX_SENTENCES_DEFAULT = 4
    MAX_SENTENCES_DETAILED = 12

    @staticmethod
    def apply_verbosity(response: str, verbosity: str) -> str:
        if verbosity == "very concise":
            sentences = response.split(".")
            return ".".join(sentences[:2]) + ("." if not response.endswith(".") else "")
        elif verbosity == "concise":
            sentences = response.split(".")
            return ".".join(sentences[:BehaviourRules.MAX_SENTENCES_DEFAULT]) + ("." if not response.endswith(".") else "")
        return response

    @staticmethod
    def should_be_detailed(intent: dict) -> bool:
        return intent.get("intent") in ("coding_help", "tool_execution") and intent.get("confidence", 0) > 0.6
