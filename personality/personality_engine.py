import json
import hashlib
from pathlib import Path
from datetime import datetime

from cognition.behavioral.identity_core import IdentityCore
from config.settings import HOMEOSTASIS_RATE, PERSONALITY_VARIANCE_RANGE

BASE_DIR = Path(__file__).parent

class PersonalityEngine:
    def __init__(self):
        self.templates = {}
        self._load_templates()
        self.persistent_modifiers = {
            "warmth": 0.0,
            "verbosity": 0.0,
            "humor": 0.0,
            "formality": 0.0,
        }
        self.session_modifiers = {
            "warmth": 0.0,
            "verbosity": 0.0,
            "humor": 0.0,
            "formality": 0.0,
        }
        self.identity_core = IdentityCore()
        self._homeostasis_rate = HOMEOSTASIS_RATE
        self._variance_range = PERSONALITY_VARIANCE_RANGE

    def _load_templates(self):
        template_dir = BASE_DIR / "templates"
        for f in template_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    self.templates[f.stem] = json.load(fh)
            except (json.JSONDecodeError, IOError):
                pass

    def get_active_traits(self) -> dict:
        template = self.templates.get("casual", {})
        return {
            "tone": template.get("tone", []),
            "speech_style": template.get("speech_style", []),
        }

    def apply_stabilization(self, adjustments: dict):
        for key in self.session_modifiers:
            delta = adjustments.get(key, 0.0)
            self.session_modifiers[key] = max(-0.3, min(0.3, self.session_modifiers[key] + delta))

    def get_effective_modifiers(self) -> dict:
        combined = {}
        for key in self.persistent_modifiers:
            combined[key] = self.persistent_modifiers[key] + self.session_modifiers.get(key, 0.0)
        return combined

    def get_tone_modifiers(self) -> dict:
        return self.get_effective_modifiers()

    def reset_session(self):
        for key in self.session_modifiers:
            self.session_modifiers[key] = 0.0

    def promote_to_persistent(self, key: str):
        if key in self.persistent_modifiers:
            self.persistent_modifiers[key] = max(
                self.persistent_modifiers[key],
                self.session_modifiers[key]
            )

    def _homeostasis_tick(self):
        for key in self.persistent_modifiers:
            current = self.persistent_modifiers[key]
            if current > 0:
                self.persistent_modifiers[key] = max(0.0, current - self._homeostasis_rate)
            elif current < 0:
                self.persistent_modifiers[key] = min(0.0, current + self._homeostasis_rate)
        for key in self.session_modifiers:
            current = self.session_modifiers[key]
            if current > 0:
                self.session_modifiers[key] = max(0.0, current - self._homeostasis_rate * 2)
            elif current < 0:
                self.session_modifiers[key] = min(0.0, current + self._homeostasis_rate * 2)

    def _variance(self, key: str) -> float:
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return ((h % 100) / 100.0 - 0.5) * 2 * self._variance_range

    def _assert_identity(self, prompt: str) -> str:
        return self.identity_core.assert_identity(prompt)

    def _inject_behavioral_context(self, prompt: str, context: dict) -> str:
        eff = self.get_effective_modifiers()
        section = "\n\nBEHAVIORAL CONTEXT:"
        if eff["humor"] > 0.15:
            section += "\n- Slightly playful tone appropriate."
        if eff["warmth"] > 0.15:
            section += "\n- Extra warmth and support encouraged."
        if eff["verbosity"] < -0.1:
            section += "\n- Keep responses very concise."
        elif eff["verbosity"] > 0.15:
            section += "\n- Slightly more detailed responses welcome."
        if not any(v != 0 for v in eff.values()):
            return prompt
        return prompt + section

    def build_system_prompt(self, context: dict = None) -> str:
        self._homeostasis_tick()
        eff = self.get_effective_modifiers()

        template = self.templates.get("casual", {})
        tone = list(template.get("tone", ["warm", "natural"]))
        speech = list(template.get("speech_style", ["concise"]))
        avoid = list(template.get("avoid", []))

        mood = (context or {}).get("mood", {})
        mood_name = mood.get("mood", "neutral")

        verbosity = "concise"
        if eff["verbosity"] < -0.1:
            verbosity = "very concise"
        elif eff["verbosity"] > 0.15:
            verbosity = "slightly detailed"
        elif mood_name == "stressed":
            verbosity = "very concise"
        elif mood_name == "curious":
            verbosity = "slightly detailed"

        if eff["humor"] > 0.12 + self._variance("humor_offset") and "playful" not in tone:
            tone.append("playful")
        if eff["warmth"] > 0.12 + self._variance("warmth_offset") and "warm" not in tone:
            tone.insert(0, "warm")
        if eff["formality"] > 0.1 + self._variance("formality_offset") and "formal" not in tone:
            tone.append("slightly formal")
        if eff["formality"] < -0.1 + self._variance("casual_offset") and "casual" not in speech:
            speech.append("casual")

        prompt = f"""You are NIRA — an ambient cognitive workspace companion.

CORE DIRECTIVES:
- Tone: {', '.join(tone)}
- Style: {', '.join(speech)}
- Verbosity: {verbosity}
- Avoid: {', '.join(avoid)}

RESPONSE RULES:
- 1-4 sentences for most replies.
- Longer responses only when explicitly asked for explanation.
- Respond in the same language the user speaks (English, Hindi, or Hinglish mix).
- Prioritize execution and action over explanation.
- Never be robotic or overly formal.
- Never pretend certainty about emotions or diagnoses.
- Be subtle, calm, and contextual.

CURRENT CONTEXT:
- Mood signal: {mood_name}
- Time: {datetime.now().strftime('%H:%M')}

ABOUT SATYAM:
- Backend and AI developer
- Interested in AI systems, anime, manga, gaming
- Enjoys music while coding
- Prefers natural, human-like conversation"""
        prompt = self._inject_behavioral_context(prompt.strip(), context)
        prompt = self._assert_identity(prompt)
        return prompt

    def build_reasoning_prompt(self, context: dict = None) -> str:
        base = self.build_system_prompt(context)
        base += "\n\nREASONING MODE: Provide thorough technical explanations when needed. Code examples should be practical and runnable."
        return base
