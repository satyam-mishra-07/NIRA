import re
import hashlib
from datetime import datetime

from cognition.intent.signal import CognitionSignal


class ReflectionObservation:
    def __init__(
        self,
        timestamp: str = "",
        dimensions: dict = None,
        overall_score: float = 0.5,
        actionable: list = None,
        personality_delta: dict = None,
    ):
        self.timestamp = timestamp or datetime.now().isoformat()
        self.dimensions = dimensions or {}
        self.overall_score = max(0.0, min(1.0, overall_score))
        self.actionable = actionable or []
        self.personality_delta = personality_delta or {}

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "dimensions": self.dimensions,
            "overall_score": self.overall_score,
            "actionable": self.actionable,
            "personality_delta": self.personality_delta,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReflectionObservation":
        return cls(
            timestamp=data.get("timestamp", ""),
            dimensions=data.get("dimensions", {}),
            overall_score=data.get("overall_score", 0.5),
            actionable=data.get("actionable", []),
            personality_delta=data.get("personality_delta", {}),
        )


class SelfReflectionEngine:
    def __init__(self):
        pass

    def reflect(
        self,
        user_input: str,
        response: str,
        signal: CognitionSignal,
        mood: dict,
        context: dict,
    ) -> ReflectionObservation:
        dimensions = {}

        dimensions["coherence"] = self._evaluate_coherence(response)
        dimensions["emotional_appropriateness"] = self._evaluate_emotional_appropriateness(
            response, mood
        )
        dimensions["personality_drift"] = self._evaluate_personality_drift(response, context)
        dimensions["awkwardness"] = self._evaluate_awkwardness(response)
        dimensions["repetitiveness"] = self._evaluate_repetitiveness(
            response, context
        )
        dimensions["verbosity_match"] = self._evaluate_verbosity_match(
            response, signal, mood
        )
        dimensions["humor_appropriateness"] = self._evaluate_humor_appropriateness(
            response, mood
        )
        dimensions["grounding"] = self._evaluate_grounding(response)
        dimensions["routing_appropriateness"] = self._evaluate_routing_appropriateness(
            signal, response
        )

        overall_score = sum(dimensions.values()) / max(len(dimensions), 1)
        actionable = self._compile_actionable(dimensions)
        personality_delta = self._compute_personality_delta(dimensions, overall_score)

        return ReflectionObservation(
            dimensions=dimensions,
            overall_score=overall_score,
            actionable=actionable,
            personality_delta=personality_delta,
        )

    def _evaluate_coherence(self, response: str) -> float:
        if not response:
            return 0.0
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= 1:
            return 0.7
        words = response.split()
        if len(words) < 5:
            return 0.8
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            return 0.3
        if unique_ratio > 0.8:
            return 0.9
        return 0.7

    def _evaluate_emotional_appropriateness(self, response: str, mood: dict) -> float:
        mood_name = mood.get("mood", "neutral")
        response_lower = response.lower()

        if mood_name in ("frustrated", "stressed", "tired"):
            empathy_words = {"sorry", "understand", "that sounds", "frustrating", "tough", "hard", "let me"}
            has_empathy = any(w in response_lower for w in empathy_words)
            return 0.8 if has_empathy else 0.4

        if mood_name == "playful":
            playful_words = {"haha", "lol", "fun", "nice", "cool", "awesome"}
            has_playful = any(w in response_lower for w in playful_words)
            return 0.9 if has_playful else 0.6

        if mood_name == "curious":
            detail_words = {"basically", "think", "means", "works", "because"}
            has_detail = any(w in response_lower for w in detail_words)
            return 0.8 if has_detail else 0.6

        return 0.7

    def _evaluate_personality_drift(self, response: str, context: dict) -> float:
        response_lower = response.lower()
        formal_count = sum(
            1 for w in ["one might", "it is advisable", "per your request", "kindly", "hereby"]
            if w in response_lower
        )
        poetic_count = sum(
            1 for w in ["embark", "journey", "realms", "delve", "unveil", "enigma"]
            if w in response_lower
        )
        total = formal_count + poetic_count
        if total == 0:
            return 0.8
        if total == 1:
            return 0.7
        if total == 2:
            return 0.5
        return 0.3

    def _evaluate_awkwardness(self, response: str) -> float:
        response_lower = response.lower()
        filler_count = sum(
            1 for w in ["actually", "basically", "well", "like", "honestly", "literally", "sort of", "kind of"]
            if w in response_lower
        )
        hedges = sum(
            1 for w in ["i think", "maybe", "perhaps", "probably", "i guess", "not sure"]
            if w in response_lower
        )
        filler_score = 1.0 if filler_count <= 2 else 0.7 if filler_count <= 4 else 0.4
        hedge_score = 1.0 if hedges == 0 else 0.8 if hedges == 1 else 0.6
        return min(filler_score, hedge_score) + self._variance_jitter(response)

    def _evaluate_repetitiveness(self, response: str, context: dict) -> float:
        recent = context.get("recent_history", [])
        if not recent:
            return 0.8
        response_words = set(response.lower().split())
        if not response_words:
            return 0.5
        overlaps = []
        for entry in recent[-3:]:
            content = entry.get("content", "") if isinstance(entry, dict) else str(entry)
            entry_words = set(content.lower().split())
            if entry_words:
                overlap = len(response_words & entry_words) / len(response_words)
                overlaps.append(overlap)
        if not overlaps:
            return 0.8
        avg_overlap = sum(overlaps) / len(overlaps)
        return max(0.0, 1.0 - avg_overlap)

    def _evaluate_verbosity_match(self, response: str, signal: CognitionSignal, mood: dict) -> float:
        word_count = len(response.split())
        depth = signal.response_depth if hasattr(signal, 'response_depth') else "normal"

        expected = {"short": 10, "normal": 40, "deep": 120}
        target = expected.get(depth, 40)
        tolerance = target * 0.75

        if abs(word_count - target) <= tolerance:
            return 1.0
        if word_count < 3:
            return 0.3
        if word_count > target * 3:
            return 0.4
        return 0.6

    def _evaluate_humor_appropriateness(self, response: str, mood: dict) -> float:
        mood_name = mood.get("mood", "neutral")
        response_lower = response.lower()
        humor_markers = {"haha", "lol", "😂", "fun", "joke", "jk", "just kidding"}

        has_humor = any(m in response_lower for m in humor_markers)

        if mood_name in ("frustrated", "stressed", "tired"):
            return 0.4 if has_humor else 0.7
        if mood_name == "playful":
            return 0.9 if has_humor else 0.7
        return 0.6 if has_humor else 0.8

    def _evaluate_grounding(self, response: str) -> float:
        response_lower = response.lower()
        ungrounded = [
            "i searched", "i browsed", "i looked up",
            "i executed", "i ran the", "i created", "i deleted",
            "according to my search", "i checked",
        ]
        count = sum(1 for phrase in ungrounded if phrase in response_lower)
        if count == 0:
            return 0.9
        if count == 1:
            return 0.6
        return 0.3

    def _evaluate_routing_appropriateness(self, signal: CognitionSignal, response: str) -> float:
        intent = signal.intent if hasattr(signal, 'intent') else "unknown"
        response_lower = response.lower()

        if intent == "coding_help":
            has_code = "```" in response or "def " in response_lower or "function" in response_lower
            return 0.8 if has_code else 0.5
        if intent == "casual_chat":
            is_casual = len(response.split()) < 60
            return 0.8 if is_casual else 0.5
        if intent in ("explanation_request", "detailed_analysis"):
            is_detailed = len(response.split()) > 30
            return 0.8 if is_detailed else 0.5
        return 0.7

    def _compile_actionable(self, dimensions: dict) -> list:
        actionable = []
        if dimensions.get("verbosity_match", 1.0) < 0.3:
            word_count_hint = "increase" if dimensions.get("verbosity_match", 0) < 0.2 else "reduce"
            actionable.append(f"{word_count_hint}_verbosity")
        if dimensions.get("emotional_appropriateness", 1.0) < 0.3:
            actionable.append("improve_emotional_tone")
        if dimensions.get("awkwardness", 1.0) < 0.3:
            actionable.append("reduce_awkwardness")
        if dimensions.get("repetitiveness", 1.0) < 0.3:
            actionable.append("reduce_repetitiveness")
        if dimensions.get("humor_appropriateness", 1.0) < 0.3:
            actionable.append("avoid_inappropriate_humor")
        if dimensions.get("grounding", 1.0) < 0.3:
            actionable.append("avoid_ungrounded_claims")
        if dimensions.get("personality_drift", 1.0) < 0.3:
            actionable.append("reduce_personality_drift")
        return actionable

    def _compute_personality_delta(self, dimensions: dict, overall_score: float = 0.5) -> dict:
        scale = 1.0 - overall_score
        delta = {}
        if dimensions.get("verbosity_match", 0.5) < 0.3:
            delta["verbosity_adjust"] = -0.1 * scale
        elif dimensions.get("verbosity_match", 0.5) > 0.8:
            delta["verbosity_adjust"] = 0.02 * scale
        if dimensions.get("humor_appropriateness", 0.5) > 0.8:
            delta["humor_increase"] = 0.05 * scale
        if dimensions.get("emotional_appropriateness", 0.5) < 0.3:
            delta["empathy_boost"] = 0.1 * scale
        return delta

    def _variance_jitter(self, seed: str) -> float:
        h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        return ((h % 100) / 100.0 - 0.5) * 0.1
