from datetime import datetime

from cognition.reflection.self_reflector import ReflectionObservation
from memory.behavioral.behavioral_memory_store import ReflectionMemoryStore


class ReflectionMemory:
    def __init__(self, store: ReflectionMemoryStore):
        self._store = store
        self._observations: list[ReflectionObservation] = []
        self._load()

    def _load(self):
        data = self._store.load()
        self._observations = [
            ReflectionObservation.from_dict(o)
            for o in data.get("observations", [])
        ]

    def _save(self):
        data = {
            "observations": [o.to_dict() for o in self._observations],
            "version": 1,
        }
        self._store.save(data)

    def add_observation(self, observation: ReflectionObservation):
        self._observations.append(observation)
        if len(self._observations) > 50:
            self._compress()
        self._save()

    def _compress(self):
        if len(self._observations) <= 50:
            return
        to_compress = self._observations[:-40]
        self._observations = self._observations[-40:]

        if to_compress:
            avg_score = sum(o.overall_score for o in to_compress) / len(to_compress)
            compressed = ReflectionObservation(
                timestamp=to_compress[0].timestamp,
                dimensions={"compressed": True, "source_count": len(to_compress)},
                overall_score=avg_score,
                actionable=["compressed"],
                personality_delta={},
            )
            self._observations.insert(0, compressed)

    def get_recent(self, count: int = 5) -> list[ReflectionObservation]:
        return self._observations[-count:]

    def get_insights(self) -> dict:
        if not self._observations:
            return {"overall_trend": "stable", "actionable": [], "score_trend": "neutral"}

        recent = self._observations[-10:]
        scores = [o.overall_score for o in recent]
        avg_score = sum(scores) / len(scores)

        all_actionable = []
        for o in recent:
            all_actionable.extend(o.actionable)
        top_actionable = list(set(all_actionable))[:3]

        if len(scores) >= 3:
            trend = scores[-1] - scores[0]
            score_trend = "improving" if trend > 0.1 else "declining" if trend < -0.1 else "stable"
        else:
            score_trend = "neutral"

        return {
            "overall_trend": "good" if avg_score > 0.7 else "needs_attention" if avg_score < 0.4 else "average",
            "actionable": top_actionable,
            "score_trend": score_trend,
            "average_score": round(avg_score, 3),
            "observation_count": len(self._observations),
        }

    def get_stability_indicators(self) -> dict:
        if not self._observations:
            return {"volatility": "unknown", "total_reflections": 0}

        recent = self._observations[-10:]
        if len(recent) < 2:
            return {"volatility": "insufficient_data", "total_reflections": len(self._observations)}

        scores = [o.overall_score for o in recent]
        volatility = max(scores) - min(scores)

        return {
            "volatility": "low" if volatility < 0.2 else "medium" if volatility < 0.4 else "high",
            "volatility_score": round(volatility, 3),
            "total_reflections": len(self._observations),
            "latest_score": scores[-1],
        }

    def clear(self):
        self._observations.clear()
        self._save()
