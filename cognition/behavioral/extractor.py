import re
from datetime import datetime


class BehavioralSignal:
    def __init__(
        self,
        user_sentiment: float = 0.0,
        response_coherence: float = 0.5,
        repetition_score: float = 0.0,
        verbosity_match: float = 0.5,
        humor_appropriateness: float = 0.5,
        emotional_appropriateness: float = 0.5,
        routing_quality: float = 0.5,
        signal_strength: float = 0.0,
    ):
        self.user_sentiment = max(-1.0, min(1.0, user_sentiment))
        self.response_coherence = max(0.0, min(1.0, response_coherence))
        self.repetition_score = max(0.0, min(1.0, repetition_score))
        self.verbosity_match = max(0.0, min(1.0, verbosity_match))
        self.humor_appropriateness = max(0.0, min(1.0, humor_appropriateness))
        self.emotional_appropriateness = max(0.0, min(1.0, emotional_appropriateness))
        self.routing_quality = max(0.0, min(1.0, routing_quality))
        self.signal_strength = max(0.0, min(1.0, signal_strength))

    def __repr__(self):
        return (
            f"BehavioralSignal(sentiment={self.user_sentiment:.2f}, "
            f"coherence={self.response_coherence:.2f}, "
            f"repetition={self.repetition_score:.2f}, "
            f"verbosity_match={self.verbosity_match:.2f}, "
            f"strength={self.signal_strength:.2f})"
        )


_POSITIVE_WORDS = {
    "thanks", "thank you", "nice", "good", "great", "perfect", "awesome",
    "exactly", "correct", "right", "yes", "yeah", "works", "working",
    "helpful", "understood", "got it", "makes sense", "clear", "cool",
    "beautiful", "love", "amazing", "wonderful", "fantastic",
}

_NEGATIVE_WORDS = {
    "no", "wrong", "incorrect", "bad", "terrible", "awful", "horrible",
    "doesn't work", "not working", "broken", "hate", "useless",
    "not helpful", "confusing", "nonsense", "stupid", "that's not",
    "galat", "sahi nahi", "bakwas", "kaam nahi",
}

_CORRECTION_WORDS = {
    "no", "actually", "i meant", "not that", "that's not",
    "i said", "let me clarify", "instead", "re-read",
}

_FOLLOW_UP_INDICATORS = {
    "also", "and", "but", "what about", "how about", "then",
    "next", "furthermore", "additionally", "moreover",
}

_POSITIVE_SENTIMENT_WORDS = _POSITIVE_WORDS
_NEGATIVE_SENTIMENT_WORDS = _NEGATIVE_WORDS


class BehavioralSignalExtractor:
    def __init__(self):
        self.last_context = {}

    def extract(self, user_input: str, previous_response: str, context: dict) -> BehavioralSignal:
        user_lower = user_input.lower().strip()
        response_lower = previous_response.lower().strip()

        if not user_lower:
            return BehavioralSignal(signal_strength=0.0)

        user_sentiment = self._compute_sentiment(user_lower)
        response_coherence = self._compute_coherence(response_lower)
        repetition_score = self._compute_repetition(user_lower, response_lower)
        verbosity_match = self._compute_verbosity_match(user_input, previous_response)
        humor_appropriateness = self._compute_humor_appropriateness(user_lower, context)
        emotional_appropriateness = self._compute_emotional_appropriateness(user_lower, context)
        routing_quality = self._compute_routing_quality(context)

        signal_strength = self._compute_signal_strength(
            user_sentiment, response_coherence, repetition_score,
            verbosity_match, user_lower, previous_response
        )

        return BehavioralSignal(
            user_sentiment=user_sentiment,
            response_coherence=response_coherence,
            repetition_score=repetition_score,
            verbosity_match=verbosity_match,
            humor_appropriateness=humor_appropriateness,
            emotional_appropriateness=emotional_appropriateness,
            routing_quality=routing_quality,
            signal_strength=signal_strength,
        )

    def _compute_sentiment(self, user_lower: str) -> float:
        positive_count = sum(1 for w in _POSITIVE_SENTIMENT_WORDS if w in user_lower)
        negative_count = sum(1 for w in _NEGATIVE_SENTIMENT_WORDS if w in user_lower)

        if positive_count == 0 and negative_count == 0:
            if user_lower.endswith("?"):
                return 0.1
            if len(user_lower.split()) < 3:
                return 0.0
            return -0.05

        total = positive_count + negative_count
        net = positive_count - negative_count
        return max(-1.0, min(1.0, net / max(total, 1)))

    def _compute_coherence(self, response_lower: str) -> float:
        if not response_lower:
            return 0.0
        words = response_lower.split()
        if len(words) < 3:
            return 0.5
        unique_ratio = len(set(words)) / len(words)
        return max(0.0, min(1.0, unique_ratio))

    def _compute_repetition(self, user_lower: str, response_lower: str) -> float:
        user_words = set(user_lower.split())
        response_words = set(response_lower.split())
        if not user_words or not response_words:
            return 0.0
        overlap = len(user_words & response_words)
        ratio = overlap / max(len(user_words), 1)
        return max(0.0, min(1.0, ratio))

    def _compute_verbosity_match(self, user_input: str, previous_response: str) -> float:
        user_words = len(user_input.split())
        response_words = len(previous_response.split())

        if user_words == 0:
            return 0.5

        ratio = response_words / max(user_words, 1)

        if 0.3 <= ratio <= 3.0:
            return 1.0
        if ratio < 0.1 or ratio > 10.0:
            return 0.0
        return 0.5

    def _compute_humor_appropriateness(self, user_lower: str, context: dict) -> float:
        mood = context.get("mood", {})
        mood_name = mood.get("mood", "neutral")
        playful_signals = {"lol", "haha", "😂", "😅", "fun", "joke", "funny", "😂😂"}
        has_playful = any(s in user_lower for s in playful_signals)

        if mood_name == "stressed" or mood_name == "frustrated":
            return 0.0 if has_playful else 0.5
        if mood_name == "playful":
            return 1.0 if has_playful else 0.8
        return 0.5

    def _compute_emotional_appropriateness(self, user_lower: str, context: dict) -> float:
        mood = context.get("mood", {})
        mood_name = mood.get("mood", "neutral")

        if mood_name in ("frustrated", "stressed", "tired"):
            has_empathy = any(
                w in user_lower
                for w in ["thanks", "helpful", "ok", "fine", "understand"]
            )
            return 1.0 if has_empathy else 0.5

        return 0.7

    def _compute_routing_quality(self, context: dict) -> float:
        intent = context.get("intent", {})
        confidence = intent.get("confidence", 0.0)
        if confidence > 0.7:
            return 1.0
        if confidence > 0.4:
            return 0.7
        return 0.4

    def _compute_signal_strength(
        self,
        user_sentiment: float,
        coherence: float,
        repetition: float,
        verbosity_match: float,
        user_lower: str,
        previous_response: str,
    ) -> float:
        abs_sentiment = abs(user_sentiment)
        has_correction = any(w in user_lower for w in _CORRECTION_WORDS)
        has_follow_up = any(w in user_lower for w in _FOLLOW_UP_INDICATORS)

        strength = 0.0
        strength += abs_sentiment * 0.3
        strength += coherence * 0.1
        strength += verbosity_match * 0.15

        if has_correction:
            strength += 0.3
        if has_follow_up:
            strength += 0.2
        if not previous_response:
            strength *= 0.3

        return max(0.0, min(1.0, strength))
