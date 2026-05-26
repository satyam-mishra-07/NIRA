from core.orchestration.execution_context import ExecutionContext


class OrchestrationRouter:
    def __init__(self, execution_context: ExecutionContext):
        self.execution_context = execution_context

    def route(self, intent: dict, context: dict) -> str:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)
        requires_reasoning = intent.get("requires_reasoning", False)

        threshold = 0.5

        if confidence < threshold:
            return "casual_chat"

        # Tool access checks
        if intent_name == "browser_request":
            if self.execution_context.browser_allowed:
                return "browser_request"

        if intent_name == "tool_execution":
            if self.execution_context.terminal_allowed:
                return "tool_execution"

        if intent_name == "file_operation":
            return "file_operation"

        # Core cognition routing
        if requires_reasoning:
            return "reasoning"

        return "casual_chat"