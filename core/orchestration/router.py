from core.orchestration.execution_context import ExecutionContext


class OrchestrationRouter:
    def __init__(self, execution_context: ExecutionContext):
        self.execution_context = execution_context

    def route(self, intent: dict, context: dict) -> str:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)
        requires_reasoning = intent.get("requires_reasoning", False)

        threshold = 0.45

        # fallback
        if confidence < threshold:
            if requires_reasoning:
                return "reasoning"
            return "casual_chat"

        # reasoning override
        if requires_reasoning:
            return "reasoning"

        # tool routing
        if intent_name == "browser_request":
            return "browser_request"

        if intent_name == "file_operation":
            return "file_operation"

        if intent_name == "tool_execution":
            return "tool_execution"

        return "casual_chat"