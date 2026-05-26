from cognition.intent.classifier import CognitionAssessor       # renamed from IntentClassifier
from cognition.intent.signal import CognitionSignal             # typed signal, replaces raw dict


class IntentPredictor:
    def __init__(self, classifier: CognitionAssessor):
        self.classifier = classifier

    def predict(self, message: str, context: dict = None) -> CognitionSignal:
        """
        Runs CognitionAssessor and returns a typed CognitionSignal.

        Context biasing is preserved from the original: if the working memory
        indicates an active coding task and confidence is low, we nudge toward
        coding_help. This now mutates the signal fields directly instead of
        patching a raw dict, which keeps the signal contract intact.
        """
        signal = self.classifier.assess(message)

        if context:
            working = context.get("working", {})
            current_task = working.get("current_task", "")

            # Context bias: active coding task + low confidence → nudge to coding_help
            if "coding" in current_task.lower() and signal.confidence < 0.6:
                signal.intent = "coding_help"
                signal.confidence = round(min(signal.confidence + 0.15, 1.0), 2)
                signal.reason = f"context_biased from task='{current_task}'; original: {signal.reason}"

        return signal