from providers.llm.conversation_model import ConversationModel
from providers.llm.reasoning_model import ReasoningModel
from config.constants import REASONING_MODEL_TRIGGERS, CONVERSATION_MODEL_TRIGGERS
from config.settings import DEBUG

class ModelRouter:
    def __init__(self):
        self.conversation = ConversationModel()
        self.reasoning = ReasoningModel()
        self.reasoning_triggers = REASONING_MODEL_TRIGGERS
        self.conversation_triggers = CONVERSATION_MODEL_TRIGGERS

    def select(self, intent: dict) -> object:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)

        if intent_name in ("coding_help", "tool_execution") and confidence > 0.5:
            if DEBUG:
                print(f"[model_router] Routing to Reasoning model (intent: {intent_name})")
            return self.reasoning

        if DEBUG:
            print(f"[model_router] Routing to Conversation model (intent: {intent_name})")
        return self.conversation
