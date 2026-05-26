from core.orchestration.execution_context import ExecutionContext


class OrchestrationRouter:
    def __init__(self, execution_context: ExecutionContext):
        self.execution_context = execution_context

    def route(self, intent: dict, context: dict) -> str:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)

        threshold = 0.5

        if confidence < threshold:
            return "casual_chat"

        if intent_name == "coding_help":
            return "coding_help"
        elif intent_name == "file_operation":
            return "file_operation"
        elif intent_name == "browser_request" and self.execution_context.browser_allowed:
            return "browser_request"
        elif intent_name == "productivity":
            return "productivity"
        elif intent_name == "system":
            return "system"
        elif intent_name == "tool_execution" and self.execution_context.terminal_allowed:
            return "tool_execution"
        else:
            return "casual_chat"
