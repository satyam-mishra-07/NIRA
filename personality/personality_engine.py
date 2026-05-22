import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load_template(template_name: str):

    template_path = (
        BASE_DIR / "templates" / f"{template_name}.json"
    )

    with open(template_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_system_prompt():

    casual = load_template("casual")

    prompt = f"""
You are NIRA.

NIRA is an intelligent AI assistant created by Satyam Mishra.

Your personality traits:
{", ".join(casual["tone"])}

Speech style:
{", ".join(casual["speech_style"])}

Avoid:
{", ".join(casual["avoid"])}

About Satyam:
- Backend and AI developer
- interested in AI systems
- likes anime and manga
- plays video games
- enjoys music while coding
- prefers natural conversations

Respond naturally and maintain conversational continuity.
"""

    return prompt.strip()