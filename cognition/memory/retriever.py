from __future__ import annotations

from memory.short_term.short_term_memory import ShortTermMemory
from memory.profile.profile_manager import ProfileManager
from memory.summaries.summary_memory import SummaryMemory
from memory.conversation.conversation_store import ConversationStore
from memory.emotional.emotional_memory import EmotionalMemory


class MemoryRetriever:
    def __init__(
        self,
        profile_manager: ProfileManager,
        summary_memory: SummaryMemory,
        emotional_memory: EmotionalMemory,
        conversation_store: ConversationStore,
        short_term: ShortTermMemory,
    ):
        self.profile_manager = profile_manager
        self.summary_memory = summary_memory
        self.emotional_memory = emotional_memory
        self.conversation_store = conversation_store
        self.short_term = short_term

    def retrieve(self, context: dict) -> dict:
        short_term_ids = self._get_short_term_ids()

        profile = self._get_profile()
        mood_trend = self._get_mood_trend()
        summaries = self._get_summaries()
        episodic = self._get_episodic(context, short_term_ids)

        return {
            "profile": profile,
            "mood_trend": mood_trend,
            "summaries": summaries,
            "episodic": episodic,
        }

    def _get_short_term_ids(self) -> set:
        ids = set()
        for msg in self.short_term.messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            ids.add(hash(content + role))
        return ids

    def _get_profile(self) -> dict:
        return {
            "name": self.profile_manager.get("name", "Satyam"),
            "interests": self.profile_manager.get("interests", []),
            "tone_preference": self.profile_manager.get("preferred_tone", "casual"),
            "communication_preference": self.profile_manager.get("communication_preference", "natural"),
            "languages": self.profile_manager.get("known_languages", ["English"]),
        }

    def _get_mood_trend(self) -> str:
        trend = self.emotional_memory.get_tone_trend()
        if trend and trend.get("trend"):
            return trend["trend"]
        return "neutral"

    def _get_summaries(self) -> list:
        return [s.get("summary", "") for s in self.summary_memory.get_recent(2) if s.get("summary")]

    def _get_episodic(self, context: dict, short_term_ids: set) -> list:
        messages = self.conversation_store.get_all()

        candidates = []
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            if hash(content + role) not in short_term_ids:
                candidates.append(msg)

        if not candidates:
            return []

        recent = candidates[-10:]

        episodes = []
        i = 0
        while i < len(recent) - 1:
            if recent[i].get("role") == "user" and recent[i + 1].get("role") == "assistant":
                significance = self._score_significance(recent[i], recent[i + 1])
                episodes.append((significance, recent[i], recent[i + 1]))
                i += 2
            else:
                i += 1

        episodes.sort(key=lambda x: x[0], reverse=True)
        top = episodes[:3]

        return [self._format_episode(u, a) for _, u, a in top]

    def _score_significance(self, user_msg: dict, asst_msg: dict) -> float:
        content = user_msg.get("content", "")
        score = 0.0
        if "?" in content:
            score += 2.0
        if "```" in content or "def " in content or "class " in content:
            score += 2.0
        if any(w in content.lower() for w in ["implement", "build", "create", "fix", "debug"]):
            score += 1.5
        if any(w in content.lower() for w in ["help", "can you", "could you", "please"]):
            score += 1.0
        if len(content.split()) > 10:
            score += 0.5
        return score

    def _format_episode(self, user_msg: dict, asst_msg: dict) -> str:
        content = user_msg.get("content", "")
        if len(content) > 100:
            content = content[:97] + "..."
        return content
