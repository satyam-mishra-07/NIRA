class RoutingContext:
    def __init__(self, intent: dict, context: dict):
        self.intent = intent
        self.context = context

    def get_model_type(self) -> str:
        intent_name = self.intent.get("intent", "casual_chat")
        if intent_name in ("coding_help", "tool_execution"):
            return "reasoning"
        return "conversation"

    def requires_streaming(self) -> bool:
        return self.intent.get("intent", "casual_chat") != "coding_help"

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "model_type": self.get_model_type(),
            "stream": self.requires_streaming(),
        }
