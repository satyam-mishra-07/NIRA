from __future__ import annotations

from typing import Any, Dict

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

    def select(self, intent: Any) -> object:
        if hasattr(intent, 'model_track'):
            return self._select_from_route_decision(intent)

        return self._select_from_dict(intent)

    def _select_from_route_decision(self, route: Any) -> object:
        model_track = getattr(route, 'model_track', 'conversational_model')

        if model_track == "reasoning_model":
            if DEBUG:
                print(f"[model_router] Routing to Reasoning model (RouteDecision: reasoning_model)")
            return self.reasoning

        if DEBUG:
            print(f"[model_router] Routing to Conversation model (RouteDecision: conversational_model)")
        return self.conversation

    def _select_from_dict(self, intent: Dict[str, Any]) -> object:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)
        requires_reasoning = intent.get("requires_reasoning", False)

        if intent_name in ("coding_help", "tool_execution") and confidence > 0.5:
            if DEBUG:
                print(f"[model_router] Routing to Reasoning model (intent: {intent_name})")
            return self.reasoning

        if requires_reasoning and confidence > 0.3:
            if DEBUG:
                print(f"[model_router] Routing to Reasoning model (requires_reasoning, intent: {intent_name})")
            return self.reasoning

        if DEBUG:
            print(f"[model_router] Routing to Conversation model (intent: {intent_name})")
        return self.conversation
