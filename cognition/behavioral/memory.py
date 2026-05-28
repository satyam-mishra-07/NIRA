from datetime import datetime
from typing import Optional

from cognition.behavioral.extractor import BehavioralSignal
from cognition.behavioral.reinforcer import ContextualReinforcer
from cognition.habits.confidence_engine import ConfidenceEngine
from memory.behavioral.behavioral_memory_store import BehavioralMemoryStore
from config.settings import (
    BEHAVIORAL_CONFIDENCE_CAP,
    BEHAVIORAL_DECAY_RATE,
    BEHAVIORAL_MIN_OBSERVATIONS,
    REFLECTION_DECAY_MULTIPLIER,
    CONTRADICTION_PENALTY,
)


class ContextualPreference:
    def __init__(
        self,
        context_key: str,
        preference: str,
        confidence: float = 0.0,
        last_reinforced: Optional[str] = None,
        first_observed: Optional[str] = None,
        observation_count: int = 0,
    ):
        self.context_key = context_key
        self.preference = preference
        self.confidence = max(0.0, min(BEHAVIORAL_CONFIDENCE_CAP, confidence))
        self.last_reinforced = last_reinforced
        self.first_observed = first_observed
        self.observation_count = observation_count

    def to_dict(self) -> dict:
        return {
            "context_key": self.context_key,
            "preference": self.preference,
            "confidence": self.confidence,
            "last_reinforced": self.last_reinforced,
            "first_observed": self.first_observed,
            "observation_count": self.observation_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContextualPreference":
        return cls(
            context_key=data.get("context_key", ""),
            preference=data.get("preference", "neutral"),
            confidence=data.get("confidence", 0.0),
            last_reinforced=data.get("last_reinforced"),
            first_observed=data.get("first_observed"),
            observation_count=data.get("observation_count", 0),
        )

    def is_active(self) -> bool:
        return (
            self.confidence >= 0.5
            and self.observation_count >= BEHAVIORAL_MIN_OBSERVATIONS
        )


class BehavioralMemory:
    def __init__(
        self,
        store: BehavioralMemoryStore,
        confidence_engine: ConfidenceEngine,
    ):
        self.store = store
        self.confidence_engine = confidence_engine
        self.reinforcer = ContextualReinforcer(confidence_engine)
        self._preferences: list[ContextualPreference] = []
        self._contradiction_pairs = [
            ("concise", "detailed"),
            ("playful", "supportive"),
            ("playful", "clear"),
        ]
        self._contradiction_count = 0
        self._recent_preferences = []
        self._max_recent = 10
        self._load()

    def _load(self):
        data = self.store.load()
        self._preferences = [
            ContextualPreference.from_dict(p) for p in data.get("preferences", [])
        ]

    def _save(self):
        data = {
            "preferences": [p.to_dict() for p in self._preferences],
            "version": 1,
        }
        self.store.save(data)

    def _build_context_key(self, context: dict) -> str:
        mood = context.get("mood", {})
        mood_name = mood.get("mood", "neutral")

        working = context.get("working", {})
        task = working.get("current_task", "")

        hour = datetime.now().hour
        time_period = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening" if hour < 22 else "late"

        parts = [f"mood:{mood_name}"]
        if task:
            parts.append(f"task:{task[:30]}")
        parts.append(f"time:{time_period}")
        return "|".join(parts)

    def _infer_preference(self, signal: BehavioralSignal) -> str:
        if signal.user_sentiment < -0.3:
            return "supportive"
        if signal.user_sentiment > 0.3:
            if signal.humor_appropriateness > 0.6:
                return "playful"
            return "supportive"
        if signal.repetition_score > 0.5:
            return "clear"
        if signal.verbosity_match < 0.3:
            return "concise" if signal.verbosity_match < 0.2 else "detailed"
        return "neutral"

    def _detect_contradictions(self, preference_name: str) -> bool:
        self._recent_preferences.append(preference_name)
        if len(self._recent_preferences) > self._max_recent:
            self._recent_preferences.pop(0)

        for a, b in self._contradiction_pairs:
            if preference_name in (a, b):
                for recent in self._recent_preferences[:-1]:
                    if recent in (a, b) and recent != preference_name:
                        self._contradiction_count += 1
                        return True
        return False

    def update(self, signal: BehavioralSignal, context: dict):
        if signal.signal_strength < 0.1:
            return

        context_key = self._build_context_key(context)
        preference_name = self._infer_preference(signal)
        has_contradiction = self._detect_contradictions(preference_name)

        existing = self._find_preference(context_key, preference_name)
        now = datetime.now().isoformat()

        if existing:
            delta = self.reinforcer.compute_reinforcement(
                signal.signal_strength, existing.confidence
            )
            if has_contradiction:
                delta *= CONTRADICTION_PENALTY
            existing.confidence = self.confidence_engine.update_confidence(
                existing.confidence, delta
            )
            existing.confidence = min(existing.confidence, BEHAVIORAL_CONFIDENCE_CAP)
            existing.last_reinforced = now
            existing.observation_count += 1
        else:
            initial = signal.signal_strength * 0.3
            if has_contradiction:
                initial *= CONTRADICTION_PENALTY
            pref = ContextualPreference(
                context_key=context_key,
                preference=preference_name,
                confidence=min(initial, BEHAVIORAL_CONFIDENCE_CAP),
                last_reinforced=now,
                first_observed=now,
                observation_count=1,
            )
            self._preferences.append(pref)

        self._cap_preferences()
        self._save()

    def _find_preference(
        self, context_key: str, preference: str
    ) -> Optional[ContextualPreference]:
        for p in self._preferences:
            if p.context_key == context_key and p.preference == preference:
                return p
        return None

    def get_preferences_for_context(self, context: dict) -> list[ContextualPreference]:
        context_key = self._build_context_key(context)
        mood = context.get("mood", {})
        mood_name = mood.get("mood", "neutral")

        results = []
        for p in self._preferences:
            if not p.is_active():
                continue
            if p.context_key == context_key:
                results.append(p)
                continue
            if mood_name in p.context_key and "task:" not in p.context_key:
                results.append(p)
                continue

        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:3]

    def decay(self):
        decayed_count = 0
        for pref in self._preferences:
            old = pref.confidence
            pref.confidence = self.confidence_engine.decay(pref.confidence)
            if pref.confidence != old:
                decayed_count += 1
        self._preferences = [
            p for p in self._preferences if p.confidence > 0.01
        ]
        self._save()

    def get_trends(self) -> dict:
        base = {"contradiction_count": self._contradiction_count}
        if not self._preferences:
            return {**base, "top_preference": "neutral", "stability": "stable", "active_count": 0}

        active = [p for p in self._preferences if p.is_active()]
        if not active:
            return {**base, "top_preference": "neutral", "stability": "stable", "active_count": 0}

        top = max(active, key=lambda p: p.confidence)
        avg_conf = sum(p.confidence for p in active) / len(active)

        return {
            **base,
            "top_preference": top.preference,
            "top_confidence": top.confidence,
            "top_context": top.context_key,
            "stability": "stable" if avg_conf < 0.7 else "established",
            "active_count": len(active),
            "total_preferences": len(self._preferences),
        }

    def apply_reflection_insights(self, insights: dict):
        if not insights:
            return

        actionable = insights.get("actionable", [])
        for action in actionable:
            for pref in self._preferences:
                if action == "reduce_verbosity" and pref.preference == "detailed":
                    for _ in range(REFLECTION_DECAY_MULTIPLIER):
                        pref.confidence = self.confidence_engine.decay(pref.confidence)
                elif action == "more_humorous" and pref.preference == "playful":
                    pref.confidence = self.confidence_engine.update_confidence(
                        pref.confidence, 0.05 * 0.5
                    )
        self._save()

    def _cap_preferences(self):
        MAX_PREFERENCES = 100
        if len(self._preferences) > MAX_PREFERENCES:
            self._preferences.sort(key=lambda p: p.confidence, reverse=True)
            self._preferences = self._preferences[:MAX_PREFERENCES]

    def reset_preference(self, context_key: str):
        self._preferences = [p for p in self._preferences if p.context_key != context_key]
        self._save()

    def get_all_preferences(self) -> list[ContextualPreference]:
        return list(self._preferences)
