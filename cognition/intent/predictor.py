from cognition.intent.classifier import IntentClassifier

class IntentPredictor:
    def __init__(self, classifier: IntentClassifier):
        self.classifier = classifier

    def _requires_reasoning(self, intent_name: str) -> bool:
        return intent_name in {
            "coding_help", "tool_execution", "browser_request",
            "file_operation", "productivity", "system",
        }

    def predict(self, message: str, context: dict = None) -> dict:
        base = self.classifier.classify(message)

        if context:
            working = context.get("working", {})
            current_task = working.get("current_task", "")
            if "coding" in current_task.lower() and base["confidence"] < 0.6:
                base["intent"] = "coding_help"
                base["confidence"] = round(base["confidence"] + 0.15, 2)
                base["sub_intent"] = "context_biased"

        if "requires_reasoning" not in base:
            base["requires_reasoning"] = self._requires_reasoning(base["intent"])

        return base
