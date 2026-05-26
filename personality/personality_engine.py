import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

class PersonalityEngine:
    def __init__(self):
        self.templates = {}
        self._load_templates()

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

    def build_system_prompt(self, context: dict = None) -> str:
        template = self.templates.get("casual", {})
        tone = template.get("tone", ["warm", "natural"])
        speech = template.get("speech_style", ["concise"])
        avoid = template.get("avoid", [])
        relevant_habits = context.get("relevant_habits", [])
        
        habit_text = ""

        if relevant_habits:
            habit_text = "\nRelevant User Context:\n"
            
            for habit in relevant_habits[:2]:
                habit_text += f"- {habit}\n"

        mood = (context or {}).get("mood", {})
        mood_name = mood.get("mood", "neutral")

        verbosity = "concise"
        if mood_name == "stressed":
            verbosity = "very concise"
        elif mood_name == "curious":
            verbosity = "slightly detailed"

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
- Avoid unnecessary embellishment.
- Do not over-personalize every response.
- Most replies should feel casual and effortless.

CURRENT CONTEXT:
- Mood signal: {mood_name}
- Time: {datetime.now().strftime('%H:%M')}

USER IDENTITY:
- Name: Satyam
- Creator of NIRA
- Prefers natural conversation
- Speaks English, Hindi, and Hinglish

{habit_text}

"""
        return prompt.strip()

    def build_reasoning_prompt(self, context: dict = None) -> str:
        base = self.build_system_prompt(context)
        base += "\n\nREASONING MODE: Provide thorough technical explanations when needed. Code examples should be practical and runnable."
        return base
