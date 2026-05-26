import json
import re

from config.prompts import INTENT_CLASSIFICATION_PROMPT
from providers.llm.openrouter_provider import OpenRouterClient


class IntentClassifier:
    def __init__(self):
        self.llm = OpenRouterClient()

        self.fast_patterns = {
            "file_operation": [
                r"\b(create|delete|rename|move|copy|folder|directory)\b",
            ],
            "browser_request": [
                r"\b(search|google|browse|look up|research)\b",
            ],
            "tool_execution": [
                r"\b(run|execute|terminal|command|pip|npm|git)\b",
            ],
        }

    def _fast_classify(self, text: str):
        scores = {}

        for intent, patterns in self.fast_patterns.items():
            score = 0

            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1

            if score > 0:
                scores[intent] = score

        if not scores:
            return None

        best = max(scores, key=scores.get)

        return {
            "intent": best,
            "confidence": 0.75,
            "requires_reasoning": False,
            "reason": "Fast regex classification",
        }

    def classify(self, message: str, context: str = "") -> dict:
        """
        Hybrid classification:
        1. Fast regex routing for simple actions
        2. LLM cognition classification for reasoning
        """

        fast_result = self._fast_classify(message)

        # ALWAYS use LLM for potentially cognitive requests
        reasoning_keywords = [
            "explain",
            "compare",
            "why",
            "how",
            "architecture",
            "design",
            "scale",
            "memory",
            "system",
            "implement",
            "reasoning",
            "analyze",
            "details",
            "deep",
        ]

        needs_llm = any(
            keyword in message.lower()
            for keyword in reasoning_keywords
        )

        if fast_result and not needs_llm:
            return fast_result

        try:
            prompt = INTENT_CLASSIFICATION_PROMPT.format(
                message=message,
                context=context,
            )

            response = self.llm.generate(
                messages=[
                    {
                        "role": "system",
                        "content": "Return ONLY valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
            )

            cleaned = response.strip()

            # remove markdown fences
            cleaned = re.sub(r"```json|```", "", cleaned).strip()

            # extract first json object safely
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)

            if not match:
                raise ValueError("No JSON found in model response")

            json_text = match.group()

            result = json.loads(json_text)

            print("[intent_classifier]", result)

            return result

        except Exception as e:
            print("[intent_classifier_error]", e)

            return fast_result or {
                "intent": "casual_chat",
                "confidence": 0.3,
                "requires_reasoning": False,
                "reason": "Fallback classification",
            }