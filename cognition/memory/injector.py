from __future__ import annotations


class MemoryInjector:
    MAX_TOKENS = 300
    CHARS_PER_TOKEN = 4

    def format(self, memories: dict) -> str:
        items = []

        profile = memories.get("profile", {})
        profile_line = self._format_profile(profile)
        if profile_line:
            items.append(profile_line)

        mood_trend = memories.get("mood_trend", "")
        if mood_trend and mood_trend != "neutral":
            items.append(f"Mood trend: {mood_trend}")

        for summary in memories.get("summaries", []):
            line = self._truncate_sentence(summary, 80)
            if line:
                items.append(f"Previous session: {line}")

        for snippet in memories.get("episodic", []):
            line = self._truncate_sentence(snippet, 100)
            if line:
                items.append(f"Recall: {line}")

        if not items:
            return ""

        result = "PRIOR MEMORIES:\n" + "\n".join(f"- {item}" for item in items)
        return self._enforce_budget(result)

    def _enforce_budget(self, text: str) -> str:
        max_chars = self.MAX_TOKENS * self.CHARS_PER_TOKEN
        if len(text) <= max_chars:
            return text

        truncated = text[:max_chars]
        last_boundary = max(
            truncated.rfind(". "),
            truncated.rfind("? "),
            truncated.rfind("! "),
            truncated.rfind("\n- "),
        )
        if last_boundary > max_chars * 0.5:
            truncated = truncated[:last_boundary + 1]

        return truncated.strip()

    def _truncate_sentence(self, text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        truncated = text[:max_len]
        boundary = truncated.rfind(". ")
        if boundary > 0:
            return truncated[:boundary + 1]
        return truncated.rstrip() + "..."

    def _format_profile(self, profile: dict) -> str:
        parts = []
        interests = profile.get("interests", [])
        tone = profile.get("tone_preference")
        comm = profile.get("communication_preference")
        languages = profile.get("languages", [])

        if interests:
            parts.append(f"User interests: {', '.join(interests[:4])}")
        if tone or comm:
            parts.append(f"Prefers {tone or 'casual'}, {comm or 'natural'} conversation")
        if languages:
            parts.append(f"Languages: {', '.join(languages)}")

        return "; ".join(parts) if parts else ""
