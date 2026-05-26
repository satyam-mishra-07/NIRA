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
    "frustrated": ["damn", "why isn't", "broken", "not working", "error", "bug", "annoying", "stupid", "wtf"],
    "curious": ["how", "why", "what if", "wonder", "curious", "experiment", "try", "explore"],
    "stressed": ["deadline", "overwhelmed", "too much", "running late", "behind", "stress", "urgent"],
    "playful": ["lol", "haha", "😂", "😅", "fun", "joke", "just kidding", "lol"],
    "focused": ["let's", "going to", "working on", "implement", "build", "create", "fix", "solve"],
    "tired": ["tired", "exhausted", "sleepy", "long day", "burned out", "late"]
}

HABIT_PATTERNS = {
    "music_while_coding": ["music", "playlist", "song", "lofi", "instrumental"],
    "late_night_work": [],
    "concise_preference": [],
    "coding_assistance": ["function", "class", "code", "debug", "error", "implement"],
    "casual_conversation": ["hey", "how are you", "what's up", "tell me", "think about"]
}
