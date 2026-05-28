from typing import Optional
from datetime import datetime

from personality.personality_engine import PersonalityEngine
from config.settings import PERSONALITY_STABILIZE_INTERVAL, PERSONALITY_MAX_ADJUSTMENT


class PersonalityStabilizer:
    def __init__(self, personality: Optional[PersonalityEngine] = None):
        self.personality = personality
        self._interval = PERSONALITY_STABILIZE_INTERVAL
        self._max_adjustment = PERSONALITY_MAX_ADJUSTMENT
        self._history = []
        self._max_history = 100

    def compute_personality_adjustments(self, preferences: list) -> dict:
        warmth = 0.0
        verbosity = 0.0
        humor = 0.0
        count = 0

        for pref in preferences:
            if pref.confidence < 0.5 or pref.observation_count < 3:
                continue
            weight = pref.confidence * (min(pref.observation_count, 10) / 10.0)
            if pref.preference == "supportive":
                warmth += 0.1 * weight
            elif pref.preference == "concise":
                verbosity -= 0.1 * weight
            elif pref.preference == "detailed":
                verbosity += 0.07 * weight
            elif pref.preference == "playful":
                humor += 0.1 * weight
            elif pref.preference == "clear":
                verbosity -= 0.05 * weight
            count += 1

        if count == 0:
            return {"warmth": 0.0, "verbosity": 0.0, "humor": 0.0, "formality": 0.0}

        adjustments = {
            "warmth": max(-self._max_adjustment, min(self._max_adjustment, warmth / count)),
            "verbosity": max(-self._max_adjustment, min(self._max_adjustment, verbosity / count)),
            "humor": max(0.0, min(self._max_adjustment, humor / count)),
            "formality": 0.0,
        }
        return adjustments

    def stabilize(self, adjustments: dict) -> dict:
        total_drift = sum(abs(v) for v in adjustments.values())
        if total_drift > 0.8:
            return {"warmth": 0.0, "verbosity": 0.0, "humor": 0.0, "formality": 0.0}
        return adjustments

    def _snapshot(self):
        if self.personality is None:
            return
        modifiers = self.personality.get_effective_modifiers()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "modifiers": dict(modifiers),
            "total_drift": sum(abs(v) for v in modifiers.values()),
        }
        self._history.append(entry)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def apply(self, preferences: list):
        if self.personality is None:
            return
        adjustments = self.compute_personality_adjustments(preferences)
        stabilized = self.stabilize(adjustments)
        self.personality.apply_stabilization(stabilized)

        _preference_to_modifier = {
            "supportive": "warmth",
            "concise": "verbosity",
            "detailed": "verbosity",
            "playful": "humor",
            "clear": "verbosity",
        }
        for pref in preferences:
            if pref.observation_count >= 10 and pref.confidence >= 0.7:
                modifier_key = _preference_to_modifier.get(pref.preference)
                if modifier_key:
                    self.personality.promote_to_persistent(modifier_key)

        self._snapshot()

    def get_stability_report(self) -> dict:
        if self.personality is None:
            return {"error": "No personality engine attached"}
        modifiers = self.personality.get_tone_modifiers()
        total_drift = sum(abs(v) for v in modifiers.values())
        return {
            "modifiers": modifiers,
            "total_drift": round(total_drift, 3),
            "drift_warning": total_drift > 0.6,
        }

    def get_meta_report(self, contradiction_count: int = 0, behavioral_trends: dict = None) -> dict:
        if not self._history:
            return {"status": "no_data", "snapshot_count": 0}

        recent = self._history[-20:]
        drifts = [h["total_drift"] for h in recent]
        avg_drift = sum(drifts) / len(drifts)
        drift_trend = "increasing" if len(drifts) > 5 and drifts[-1] > drifts[0] * 1.2 else "stable"

        return {
            "status": "healthy" if avg_drift < 0.3 else "warn" if avg_drift < 0.6 else "critical",
            "average_drift": round(avg_drift, 3),
            "drift_trend": drift_trend,
            "contradiction_count": contradiction_count,
            "adaptation_intensity": round(avg_drift / 0.3, 3),
            "snapshot_count": len(self._history),
            "behavioral_trends": behavioral_trends or {},
        }
