"""
cognition/intent/signal.py

CognitionSignal is the typed contract that flows between:
  - CognitionAssessor (classifier)
  - ExecutionRouter (model selector)
  - ToolPlanner (tool orchestration layer)

WHY A DATACLASS INSTEAD OF A RAW DICT:
  Raw dicts are the root cause of silent failures. When the LLM returns
  unexpected keys or the JSON partially parses, a dict silently gives you
  None or KeyError. A dataclass with defaults gives you a safe, inspectable
  object where every consumer knows exactly what fields exist.

  This also makes the architecture extensible: adding emotional_state,
  memory_retrieval_needed, agent_handoff etc. is one field addition here,
  not a change scattered across classifier + router + every consumer.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal


# ── Intent categories ────────────────────────────────────────────────────────
# These are semantic labels for what the user WANTS.
# The router MUST NOT use these to decide model selection.
# Model selection is driven entirely by requires_reasoning + requires_tools.
IntentCategory = Literal[
    "casual_chat",
    "coding_help",
    "explanation_request",
    "detailed_analysis",
    "comparison_request",
    "architecture_design",
    "multi_step_reasoning",
    "browser_request",
    "file_operation",
    "tool_execution",
    "emotional_support",
    "productivity",
    "system",
    "unknown",
]

# ── Tool types ───────────────────────────────────────────────────────────────
ToolType = Literal[
    "browser",
    "file_system",
    "terminal",
    "code_execution",
    "memory_retrieval",
    None,
]

# ── Response depth ───────────────────────────────────────────────────────────
ResponseDepth = Literal["short", "normal", "deep"]


@dataclass
class CognitionSignal:
    """
    A fully typed signal produced by the CognitionAssessor.
    All consumers (router, tool planner, memory layer) read from this object.

    FIELDS:
      intent          → What the user semantically wants (label only, not routing key)
      confidence      → Classifier confidence [0.0 - 1.0]
      requires_reasoning → Whether a deep reasoning model (DeepSeek) is needed
      requires_tools  → Whether any tool execution is needed (independent of reasoning)
      tool_type       → Which tool class is needed (null if requires_tools=False)
      response_depth  → How long/detailed the response should be
      reason          → Short human-readable explanation of classification decision
      raw_source      → "llm" | "regex" | "fallback" — tracks how signal was produced
    """

    intent: IntentCategory = "unknown"
    confidence: float = 0.0
    requires_reasoning: bool = False
    requires_tools: bool = False
    tool_type: Optional[ToolType] = None
    response_depth: ResponseDepth = "normal"
    reason: str = ""
    raw_source: Literal["llm", "regex", "fallback"] = "fallback"

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "requires_reasoning": self.requires_reasoning,
            "requires_tools": self.requires_tools,
            "tool_type": self.tool_type,
            "response_depth": self.response_depth,
            "reason": self.reason,
            "raw_source": self.raw_source,
        }

    @classmethod
    def safe_fallback(cls, reason: str = "Fallback — classification failed") -> "CognitionSignal":
        """
        Returns a safe default signal when classification fails entirely.
        Defaults to casual_chat with low confidence so the system degrades
        gracefully instead of routing incorrectly with false confidence.
        """
        return cls(
            intent="casual_chat",
            confidence=0.2,
            requires_reasoning=False,
            requires_tools=False,
            tool_type=None,
            response_depth="short",
            reason=reason,
            raw_source="fallback",
        )

    @classmethod
    def from_dict(cls, data: dict) -> "CognitionSignal":
        """
        Safely constructs a CognitionSignal from a raw dict (LLM output).
        Unknown or invalid values are replaced with safe defaults.
        This is the ONLY place where dict-to-signal conversion happens.
        """
        # Validate intent — unknown is safe default
        valid_intents = {
            "casual_chat", "coding_help", "explanation_request",
            "detailed_analysis", "comparison_request", "architecture_design",
            "multi_step_reasoning", "browser_request", "file_operation",
            "tool_execution", "emotional_support", "productivity", "system",
        }
        intent = data.get("intent", "unknown")
        if intent not in valid_intents:
            intent = "unknown"

        # Clamp confidence to [0.0, 1.0]
        try:
            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
        except (TypeError, ValueError):
            confidence = 0.5

        # Boolean fields — explicit coercion, never trust raw LLM strings
        requires_reasoning = bool(data.get("requires_reasoning", False))
        requires_tools = bool(data.get("requires_tools", False))

        # tool_type — only set if requires_tools is True
        valid_tools = {"browser", "file_system", "terminal", "code_execution", "memory_retrieval"}
        tool_type = data.get("tool_type") if requires_tools else None
        if tool_type not in valid_tools:
            tool_type = None

        # response_depth
        valid_depths = {"short", "normal", "deep"}
        response_depth = data.get("response_depth", "normal")
        if response_depth not in valid_depths:
            response_depth = "normal"

        reason = str(data.get("reason", ""))[:300]  # truncate safety

        return cls(
            intent=intent,
            confidence=confidence,
            requires_reasoning=requires_reasoning,
            requires_tools=requires_tools,
            tool_type=tool_type,
            response_depth=response_depth,
            reason=reason,
            raw_source="llm",
        )