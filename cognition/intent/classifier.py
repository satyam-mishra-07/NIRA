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

    # ── Public API ────────────────────────────────────────────────────────────

    def assess(self, message: str, context: str = "") -> CognitionSignal:
        """
        Main entry point. Produces a full CognitionSignal for a user message.

        Flow:
          1. Run regex pre-filter → get tool_hints (non-blocking)
          2. Detect reasoning hint keywords → enrich prompt
          3. Call LLM with enriched prompt
          4. Parse response via extract_json
          5. Validate via CognitionSignal.from_dict
          6. Merge regex tool_hints into signal if LLM missed them
          7. Return signal (never raises)
        """
        tool_hint = self._detect_tool_hint(message)
        reasoning_hint = self._detect_reasoning_hints(message)

        try:
            signal = self._llm_assess(message, context, tool_hint, reasoning_hint)
        except Exception as e:
            print(f"[cognition_assessor] LLM call failed: {e}")
            signal = None

        if signal is None:
            # LLM failed entirely — build a safe fallback
            signal = self._build_safe_fallback(tool_hint, message)
            print(f"[cognition_assessor] Using fallback signal: {signal.to_dict()}")
            return signal

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

        if not scores:
            return None

        return max(scores, key=scores.get)

    def _detect_reasoning_hints(self, text: str) -> bool:
        """
        Returns True if message contains strong reasoning signal keywords.
        Used to enrich the LLM prompt — NOT used for routing directly.
        """
        text_lower = text.lower()
        return any(kw in text_lower for kw in self._reasoning_hint_keywords)

    def _llm_assess(
        self,
        message: str,
        context: str,
        tool_hint: Optional[str],
        reasoning_hint: bool,
    ) -> Optional[CognitionSignal]:
        """
        Calls the LLM and returns a parsed CognitionSignal, or None if parsing fails.
        """
        prompt = COGNITION_ASSESSMENT_PROMPT.format(
            message=message,
            context=context or "No prior context",
            tool_hint=tool_hint or "none",
            reasoning_hint="yes" if reasoning_hint else "no",
        )

        response = self.llm.generate(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a cognitive routing engine. "
                        "Respond ONLY with a single valid JSON object. "
                        "No preamble, no explanation, no markdown. "
                        "Just the JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.05,  # Near-deterministic for classification
        )

        if not response:
            return None

        parsed = extract_json(response)

        if parsed is None:
            print(f"[cognition_assessor] JSON extraction failed. Raw response: {repr(response[:200])}")
            return None

        return CognitionSignal.from_dict(parsed)

    def _build_safe_fallback(
        self,
        tool_hint: Optional[str],
        message: str,
    ) -> CognitionSignal:
        """
        Builds the best possible fallback signal when the LLM fails.
        Uses regex hints if available to avoid completely wrong routing.
        """
        if tool_hint:
            # At least route to the right tool even without LLM
            return CognitionSignal(
                intent="tool_execution",
                confidence=0.5,
                requires_reasoning=False,
                requires_tools=True,
                tool_type=tool_hint,
                response_depth="short",
                reason=f"LLM failed; regex detected tool={tool_hint}",
                raw_source="fallback",
            )

        # Completely unknown — safe neutral fallback
        return CognitionSignal.safe_fallback(
            reason="LLM assessment failed; no regex hints available"
        )