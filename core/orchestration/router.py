"""
core/orchestration/router.py  →  ExecutionRouter

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

from cognition.intent.signal import CognitionSignal  # correct location


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

    # Confidence below this threshold triggers a safe downgrade
    # to conversational model, even if requires_reasoning=True
    CONFIDENCE_THRESHOLD = 0.35

    def route(self, signal: CognitionSignal) -> RouteDecision:
        """
        Main routing method. Converts CognitionSignal → RouteDecision.
        Never raises. Always returns a valid RouteDecision.
        """

        # ── Safety gate: low confidence ───────────────────────────────────────
        # If the classifier isn't confident, we should NOT commit to
        # expensive reasoning. Downgrade but preserve tool detection.
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

        # ── Primary routing decision ──────────────────────────────────────────
        # requires_reasoning is the SOLE criterion for model selection.
        # This is intentional — decouples intent taxonomy from model routing.
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

        # ── Tool activation is fully independent of model selection ──────────
        # A reasoning request CAN also need tools (e.g. "search and explain")
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