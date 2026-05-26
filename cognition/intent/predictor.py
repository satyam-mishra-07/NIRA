from cognition.intent.classifier import CognitionAssessor
from cognition.intent.signal import CognitionSignal
from typing import Dict, Any, Optional


class IntentPredictor:
    def __init__(self, classifier: CognitionAssessor):
        self.classifier = classifier

    def _requires_reasoning(self, intent_name: str) -> bool:
        return intent_name in {
            "coding_help", "tool_execution", "browser_request",
            "file_operation", "productivity", "system",
        }

    def predict(self, message: str, context: Optional[Dict[str, Any]] = None) -> CognitionSignal:
        base = self.classifier.classify(message)

        if context:
            working = context.get("working", {})
            current_task = working.get("current_task", "")
            if current_task and isinstance(current_task, str):
                if "coding" in current_task.lower() and base.get("confidence", 0.0) < 0.6:
                    base["intent"] = "coding_help"
                    base["confidence"] = round(base.get("confidence", 0.0) + 0.15, 2)
                    base["sub_intent"] = "context_biased"

        if "requires_reasoning" not in base:
            base["requires_reasoning"] = self._requires_reasoning(base.get("intent", "casual_chat"))

        base["raw_source"] = "regex"
        if "reason" not in base:
            base["reason"] = f"Intent classified as {base.get('intent', 'unknown')}"

        return CognitionSignal.from_dict(base)
