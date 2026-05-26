"""
cognition/intent/classifier.py  →  CognitionAssessor

WHY THIS WAS RENAMED CONCEPTUALLY:
  "IntentClassifier" implies a single-label categorizer.
  "CognitionAssessor" better reflects that this module assesses:
    - WHAT the user wants (intent)
    - HOW HARD to think (requires_reasoning)
    - WHETHER tools are needed (requires_tools + tool_type)
    - HOW LONG to respond (response_depth)

  The name change is intentional — it signals the architectural shift from
  "classify and route" to "assess and signal."

DESIGN PRINCIPLES:
  1. LLM is the PRIMARY classification layer. Regex is a PRE-FILTER only.
  2. Regex fast-path ONLY sets requires_tools and tool_type hints.
     It NEVER suppresses the LLM call and NEVER sets requires_reasoning.
  3. The LLM response is always parsed via json_parser.extract_json(),
     which handles all known failure modes.
  4. CognitionSignal.from_dict() performs all validation and coercion.
     The assessor never touches raw dict fields directly.
  5. Fallback is a typed CognitionSignal, never a raw dict.
     This prevents silent None-key failures downstream.
  6. Hinglish support: the prompt explicitly instructs the model to handle
     mixed-language inputs without degrading classification accuracy.
"""

import re
from typing import Optional

from cognition.intent.json_parser import extract_json
from cognition.intent.signal import CognitionSignal
from config.prompts import COGNITION_ASSESSMENT_PROMPT
from providers.llm.openrouter_provider import OpenRouterClient


class CognitionAssessor:
    def __init__(self):
        self.llm = OpenRouterClient()

        # ── Regex pre-filter ──────────────────────────────────────────────────
        # PURPOSE: Detect tool-requiring signals BEFORE the LLM call.
        # This lets the prompt include tool_hint so the LLM can use it.
        # IMPORTANT: These patterns set tool hints ONLY.
        #            They do NOT set requires_reasoning.
        #            They do NOT short-circuit the LLM call.
        self._tool_patterns: dict[str, list[str]] = {
            "file_system": [
                r"\b(create|delete|rename|move|copy|mkdir|folder|directory|file)\b",
                r"\b(banao|hatao|folder|file)\b",  # Hindi/Hinglish variants
            ],
            "browser": [
                r"\b(search|google|browse|look up|open browser|web par|internet par)\b",
                r"\b(latest news|current|aaj ka|abhi ka)\b",
            ],
            "terminal": [
                r"\b(run|execute|terminal|command|pip|npm|git|bash|script)\b",
                r"\b(chalao|run karo|install karo)\b",  # Hinglish
            ],
            "code_execution": [
                r"\b(compile|test|debug|output|print result|code run)\b",
            ],
        }

        # ── Reasoning signal keywords (used for prompt enrichment only) ───────
        # These are NOT used for routing decisions.
        # They're passed to the LLM as context hints when present.
        # The LLM makes the final requires_reasoning decision.
        self._reasoning_hint_keywords = [
            "explain", "compare", "why", "how does", "architecture",
            "design", "scale", "implement", "analyze", "deep", "detail",
            "difference between", "better", "tradeoff", "vs", "versus",
            "samjhao", "batao", "kyun", "kaise", "compare karo",  # Hinglish
        ]

    def _normalize_hinglish(self, text: str) -> str:
        normalized = text.lower()
        for hing, eng in sorted(self._hinglish_map.items(), key=lambda x: -len(x[0])):
            normalized = normalized.replace(hing, eng)
        return normalized

    def _requires_reasoning(self, intent_name: str) -> bool:
        return intent_name in {
            "coding_help", "tool_execution", "browser_request",
            "file_operation", "productivity", "system",
        }

    def _classify_internal(self, text: str) -> dict:
        scores = {}
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            if score > 0:
                scores[intent] = score

        # Merge regex tool hints: if regex detected a tool need but LLM missed it,
        # trust the regex. This prevents tool requests from silently becoming chat.
        if tool_hint and not signal.requires_tools:
            print(f"[cognition_assessor] Regex override: adding tool_hint={tool_hint}")
            signal.requires_tools = True
            signal.tool_type = tool_hint

        print(f"[cognition_assessor] Signal: {signal.to_dict()}")
        return signal

    # ── Internal methods ──────────────────────────────────────────────────────

    def _detect_tool_hint(self, text: str) -> Optional[str]:
        """
        Runs regex patterns to detect the most likely tool type needed.
        Returns tool type string or None.
        This is a HINT only — the LLM can override or ignore it.
        """
        scores: dict[str, int] = {}

        for tool_type, patterns in self._tool_patterns.items():
            score = sum(
                1 for p in patterns
                if re.search(p, text, re.IGNORECASE)
            )
            if score > 0:
                scores[tool_type] = score

        if not scores and casual_score > 0:
            return {"intent": "casual_chat", "confidence": 0.6, "sub_intent": None, "requires_reasoning": False}
        if not scores:
            return {"intent": "casual_chat", "confidence": 0.3, "sub_intent": None, "requires_reasoning": False}

        best = max(scores, key=scores.get)
        confidence = min(0.5 + (scores[best] / sum(scores.values())) * 0.4, 0.95)
        return {"intent": best, "confidence": round(confidence, 2), "sub_intent": None, "requires_reasoning": self._requires_reasoning(best)}

    def classify(self, message: str) -> dict:
        original_result = self._classify_internal(message.lower())
        normalized = self._normalize_hinglish(message)
        if normalized != message.lower():
            normalized_result = self._classify_internal(normalized)
            if normalized_result["confidence"] > original_result["confidence"]:
                return normalized_result
        return original_result
