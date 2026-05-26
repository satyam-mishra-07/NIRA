"""
core/orchestration/router.py  →  ExecutionRouter + OrchestrationRouter

WHY THE OLD ROUTER FAILED:
  The old router used `intent_name` string matching to decide model selection:
    if intent_name == "browser_request": return "browser_request"

  This is fragile because:
  1. The LLM might return "web_search" instead of "browser_request"
  2. Intent and model selection are DIFFERENT concerns — coupling them means
     changing intent categories requires changing routing logic
  3. It had no concept of "tool + reasoning simultaneously"
     (e.g. "search the web and explain why Transformers work")

THE NEW DESIGN:
  The router reads ONLY from CognitionSignal fields:
    - requires_reasoning  → which MODEL to use
    - requires_tools      → whether to activate tool planner
    - tool_type           → which tool track
    - response_depth      → passed to the model for response length control

  It does NOT read intent names for routing decisions.
  Intent names are labels for logging and memory, not routing keys.

ROUTING DECISION TABLE:
  requires_reasoning | requires_tools | Decision
  ───────────────────────────────────────────────────
  True               | False          | reasoning_model
  True               | True           | reasoning_model + tool_planner
  False              | True           | conversational_model + tool_planner
  False              | False          | conversational_model
  (confidence < 0.3) | any            | conversational_model (safe downgrade)

MODELS:
  "reasoning_model"      → DeepSeek (deep multi-step reasoning)
  "conversational_model" → Qwen (fast, lightweight, conversational)

  The router returns a RouteDecision object, not a raw string.
  This makes the contract between router and model_router explicit and typed.
"""

from dataclasses import dataclass
from typing import Optional, Literal

from cognition.intent.signal import CognitionSignal
from core.orchestration.execution_context import ExecutionContext


ModelTrack = Literal["reasoning_model", "conversational_model"]


@dataclass
class RouteDecision:
    """
    Typed output of ExecutionRouter.

    model_track         → Which LLM to use
    activate_tools      → Whether to engage the ToolPlanner
    tool_type           → Which tool (if activate_tools is True)
    response_depth      → Passed to model for response length control
    routing_reason      → Logged explanation of routing decision
    """
    model_track: ModelTrack
    activate_tools: bool
    tool_type: Optional[str]
    response_depth: str
    routing_reason: str

    def to_dict(self) -> dict:
        return {
            "model_track": self.model_track,
            "activate_tools": self.activate_tools,
            "tool_type": self.tool_type,
            "response_depth": self.response_depth,
            "routing_reason": self.routing_reason,
        }


class ExecutionRouter:
    """
    Reads a CognitionSignal and produces a RouteDecision.

    DESIGN INVARIANTS:
    - NEVER reads signal.intent for model selection
    - ALWAYS reads signal.requires_reasoning for model selection
    - ALWAYS reads signal.requires_tools for tool activation
    - Low-confidence signals are downgraded to conversational safely
    - Reasoning + tools are fully orthogonal — both can be True simultaneously
    """

    CONFIDENCE_THRESHOLD = 0.35

    def route(self, signal: CognitionSignal) -> RouteDecision:
        """
        Main routing method. Converts CognitionSignal → RouteDecision.
        Never raises. Always returns a valid RouteDecision.
        """

        if signal.confidence < self.CONFIDENCE_THRESHOLD and signal.raw_source != "regex":
            reason = (
                f"Low confidence ({signal.confidence:.2f}) — "
                f"downgrading to conversational_model. "
                f"Original intent: {signal.intent}"
            )
            print(f"[execution_router] {reason}")
            return RouteDecision(
                model_track="conversational_model",
                activate_tools=signal.requires_tools,
                tool_type=signal.tool_type,
                response_depth=signal.response_depth,
                routing_reason=reason,
            )

        if signal.requires_reasoning:
            model_track: ModelTrack = "reasoning_model"
            reason = (
                f"requires_reasoning=True → DeepSeek reasoning model. "
                f"Intent: {signal.intent}, Depth: {signal.response_depth}"
            )
        else:
            model_track = "conversational_model"
            reason = (
                f"requires_reasoning=False → Qwen conversational model. "
                f"Intent: {signal.intent}"
            )

        activate_tools = signal.requires_tools

        if activate_tools:
            reason += f" | Tool planner: {signal.tool_type}"

        print(f"[execution_router] Decision: model={model_track}, "
              f"tools={activate_tools}({signal.tool_type}), "
              f"depth={signal.response_depth}")

        return RouteDecision(
            model_track=model_track,
            activate_tools=activate_tools,
            tool_type=signal.tool_type,
            response_depth=signal.response_depth,
            routing_reason=reason,
        )


class OrchestrationRouter:
    """
    Legacy router for backwards compatibility.
    Returns string routing decisions: "reasoning", "casual_chat", "browser_request", etc.

    Used by older code paths. New code should use ExecutionRouter instead.
    """

    def __init__(self, execution_context: ExecutionContext):
        self.execution_context = execution_context

    def route(self, intent: dict, context: dict) -> str:
        intent_name = intent.get("intent", "casual_chat")
        confidence = intent.get("confidence", 0.0)
        requires_reasoning = intent.get("requires_reasoning", False)

        threshold = 0.5

        if confidence < threshold:
            return "casual_chat"

        if intent_name == "browser_request":
            if self.execution_context.browser_allowed:
                return "browser_request"

        if intent_name == "tool_execution":
            if self.execution_context.terminal_allowed:
                return "tool_execution"

        if intent_name == "file_operation":
            return "file_operation"

        if requires_reasoning:
            return "reasoning"

        return "casual_chat"
