import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
MEMORY_DIR = PROJECT_ROOT / "memory"

PROFILE_FILE = MEMORY_DIR / "profile" / "user_profile.json"
HABITS_FILE = MEMORY_DIR / "habits" / "habits.json"
EMOTIONAL_STATE_FILE = MEMORY_DIR / "emotional" / "emotional_state.json"
SUMMARIES_FILE = MEMORY_DIR / "summaries" / "summaries.json"
BEHAVIORAL_MEMORY_FILE = MEMORY_DIR / "behavioral" / "behavioral_memory.json"
REFLECTION_MEMORY_FILE = MEMORY_DIR / "behavioral" / "reflection_memory.json"
PERSONALITY_STABILITY_FILE = MEMORY_DIR / "behavioral" / "personality_stability.json"

MAX_RESPONSE_SENTENCES = 4
MAX_RESPONSE_SENTENCES_DETAILED = 12

REASONING_MODEL_TRIGGERS = [
    "debug", "explain", "why does", "how does", "analyze",
    "refactor", "optimize", "complex", "architecture",
    "design pattern", "algorithm", "data structure"
]

CONVERSATION_MODEL_TRIGGERS = [
    "hello", "hi", "hey", "how are you", "what's up",
    "good morning", "good evening", "thanks", "thank you"
]

MOOD_KEYWORDS = {
    "frustrated": ["damn", "why isn't", "broken", "not working", "error", "bug",
                    "annoying", "stupid", "wtf", "kaam nahi", "galat", "kya bakwas",
                    "sahi nahi", "problem", "issue", "fail"],
    "curious": ["how", "why", "what if", "wonder", "curious", "experiment",
                "try", "explore", "kaise", "kya hai", "kyu", "ise kaise",
                "kya hua", "batana", "samjhana"],
    "stressed": ["deadline", "overwhelmed", "too much", "running late", "behind",
                 "stress", "urgent", "time nahi", "bahut kaam", "pressure", "jaldi"],
    "playful": ["lol", "haha", "😂", "😅", "fun", "joke", "just kidding",
                "mazaak", "hasi", "cool", "nice"],
    "focused": ["let's", "going to", "working on", "implement", "build",
                "create", "fix", "solve", "karte hain", "karna hai", "focus"],
    "tired": ["tired", "exhausted", "sleepy", "long day", "burned out",
              "late", "thak gaya", "neend", "aaram", "break"],
}

HABIT_PATTERNS = {
    "music_while_coding": ["music", "playlist", "song", "lofi", "instrumental",
                           "gaana", "music laga", "beat", "melody"],
    "late_night_work": [],
    "concise_preference": [],
    "coding_assistance": ["function", "class", "code", "debug", "error",
                          "implement", "program", "fix karo", "code likho",
                          "syntax", "compile", "terminal"],
    "casual_conversation": ["hey", "how are you", "what's up", "tell me",
                            "think about", "kaise ho", "kya chal raha"],
}
