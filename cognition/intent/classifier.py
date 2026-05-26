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
  1. Regex provides a STABLE, FAST baseline that works offline
  2. LLM classification is an enhancement layer (not yet wired)
  3. Output dict format is compatible with CognitionSignal.from_dict()
  4. Hinglish support: mixed-language inputs normalized before matching
"""

import re
from typing import Optional, Dict, Any

from cognition.intent.json_parser import extract_json
from cognition.intent.signal import CognitionSignal
from config.prompts import COGNITION_ASSESSMENT_PROMPT
from providers.llm.openrouter_provider import OpenRouterClient


class CognitionAssessor:
    def __init__(self):
        self.llm = OpenRouterClient()

        self.patterns: Dict[str, list] = {
            "coding_help": [
                r"\b(code|debug|error|function|class|implement|bug|fix|compile|syntax|refactor)\b",
                r"```", r"def |class |import ",
            ],
            "file_operation": [
                r"\b(create|delete|rename|move|copy|read|write|save|open|file|folder|directory)\b",
                r"\.py|\.js|\.ts|\.txt|\.json|\.md",
            ],
            "browser_request": [
                r"\b(search|google|browse|open website|look up|find|research|wikipedia|url)\b",
            ],
            "productivity": [
                r"\b(plan|task|todo|schedule|remind|organize|project|deadline|goal|priority)\b",
            ],
            "system": [
                r"\b(status|setting|config|update|version|restart|shutdown|what can you)\b",
            ],
            "tool_execution": [
                r"\b(run|execute|terminal|command|pip|npm|git|bash|shell)\b",
            ],
        }

        self.casual_patterns: list = [
            r"\b(hello|hi|hey|how are you|what's up|good morning|thanks|bye)\b",
        ]

        self._hinglish_map: Dict[str, str] = {
            "kar raha": " is ", "kar rahi": " is ", "nahi": " not ",
            "kaam": " work ", "karo": " do ", "aa raha": " getting ",
            "kya": " what ", "kyu": " why ", "kaise": " how ",
            "ye": " this ", "vo": " that ", "mera": " my ",
            "chahiye": " need ", "dikhao": " show ", "banao": " build ",
            "karte hain": " let's ", "karna": " do ", "likho": " write ",
            "padho": " read ", "kholo": " open ", "dhundo": " search ",
            "batao": " tell ", "samjhao": " explain ",
        }

        self._tool_patterns: Dict[str, list] = {
            "file_system": [
                r"\b(create|delete|rename|move|copy|mkdir|folder|directory|file)\b",
                r"\b(banao|hatao|folder|file)\b",
            ],
            "browser": [
                r"\b(search|google|browse|look up|open browser|web par|internet par)\b",
                r"\b(latest news|current|aaj ka|abhi ka)\b",
            ],
            "terminal": [
                r"\b(run|execute|terminal|command|pip|npm|git|bash|script)\b",
                r"\b(chalao|run karo|install karo)\b",
            ],
            "code_execution": [
                r"\b(compile|test|debug|output|print result|code run)\b",
            ],
        }

        self._reasoning_hint_keywords: list = [
            "explain", "compare", "why", "how does", "architecture",
            "design", "scale", "implement", "analyze", "deep", "detail",
            "difference between", "better", "tradeoff", "vs", "versus",
            "samjhao", "batao", "kyun", "kaise", "compare karo",
        ]

        self._explanation_keywords = [
            "explain", "what is", "how does", "how do", "what are",
            "internally", "internals", "mechanism", "works", "concept",
            "samjhao", "batao", "kaise",
        ]

        self._comparison_keywords = [
            "compare", "difference between", "vs", "versus", "better",
            "compare with", "compared to", "tradeoff", "pros and cons",
            "compare karo",
        ]

        self._technical_terms = [
            "transformer", "attention", "neural network", "model", "architecture",
            "system", "algorithm", "memory", "vector", "graph", "database",
            "api", "framework", "library", "protocol",
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

    def _detect_tool_type_from_intent(self, intent_name: str) -> Optional[str]:
        mapping = {
            "browser_request": "browser",
            "file_operation": "file_system",
            "tool_execution": "terminal",
        }
        return mapping.get(intent_name)

    def _has_keyword(self, text: str, keywords: list) -> bool:
        text_lower = text.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                return True
        return False

    def _count_keywords(self, text: str, keywords: list) -> int:
        text_lower = text.lower()
        count = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                count += 1
        return count

    def _classify_internal(self, text: str) -> Dict[str, Any]:
        scores: Dict[str, int] = {}
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            if score > 0:
                scores[intent] = score

        casual_score = sum(1 for p in self.casual_patterns if re.search(p, text))

        has_reasoning = self._has_keyword(text, self._reasoning_hint_keywords)
        has_explanation = self._has_keyword(text, self._explanation_keywords)
        has_comparison = self._has_keyword(text, self._comparison_keywords)
        has_technical = self._count_keywords(text, self._technical_terms)

        if not scores and casual_score > 0:
            return {
                "intent": "casual_chat",
                "confidence": 0.6,
                "sub_intent": None,
                "requires_reasoning": False,
                "requires_tools": False,
                "tool_type": None,
                "response_depth": "short",
            }

        if not scores:
            if has_comparison and has_technical >= 1:
                return {
                    "intent": "comparison_request",
                    "confidence": 0.55,
                    "sub_intent": None,
                    "requires_reasoning": True,
                    "requires_tools": False,
                    "tool_type": None,
                    "response_depth": "deep",
                }
            elif has_explanation and has_technical >= 1:
                return {
                    "intent": "explanation_request",
                    "confidence": 0.55,
                    "sub_intent": None,
                    "requires_reasoning": True,
                    "requires_tools": False,
                    "tool_type": None,
                    "response_depth": "deep",
                }
            elif has_reasoning and has_technical >= 1:
                return {
                    "intent": "detailed_analysis",
                    "confidence": 0.5,
                    "sub_intent": None,
                    "requires_reasoning": True,
                    "requires_tools": False,
                    "tool_type": None,
                    "response_depth": "deep",
                }
            elif has_reasoning:
                return {
                    "intent": "casual_chat",
                    "confidence": 0.35,
                    "sub_intent": None,
                    "requires_reasoning": True,
                    "requires_tools": False,
                    "tool_type": None,
                    "response_depth": "normal",
                }

            return {
                "intent": "casual_chat",
                "confidence": 0.3,
                "sub_intent": None,
                "requires_reasoning": False,
                "requires_tools": False,
                "tool_type": None,
                "response_depth": "normal",
            }

        best = max(scores, key=scores.get)
        confidence = min(0.5 + (scores[best] / sum(scores.values())) * 0.4, 0.95)
        requires_reasoning = self._requires_reasoning(best)

        if not requires_reasoning:
            if has_comparison and has_technical >= 1:
                requires_reasoning = True
            elif has_explanation and has_technical >= 1:
                requires_reasoning = True
            elif has_reasoning and has_technical >= 1:
                requires_reasoning = True

        tool_type = self._detect_tool_type_from_intent(best)
        requires_tools = tool_type is not None

        response_depth = "deep" if requires_reasoning else "normal"

        return {
            "intent": best,
            "confidence": round(confidence, 2),
            "sub_intent": None,
            "requires_reasoning": requires_reasoning,
            "requires_tools": requires_tools,
            "tool_type": tool_type,
            "response_depth": response_depth,
        }

    def classify(self, message: str) -> Dict[str, Any]:
        original_result = self._classify_internal(message.lower())
        normalized = self._normalize_hinglish(message)
        if normalized != message.lower():
            normalized_result = self._classify_internal(normalized)
            if normalized_result["confidence"] > original_result["confidence"]:
                return normalized_result
        return original_result
