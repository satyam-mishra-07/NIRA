import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
CONVERSATION_MODEL = os.getenv("CONVERSATION_MODEL") or os.getenv("PRIMARY_MODEL", "qwen/qwen3-32b")
REASONING_MODEL = os.getenv("REASONING_MODEL") or os.getenv("FALLBACK_MODEL", "deepseek/deepseek-chat-v3-0324")
PRIMARY_MODEL = CONVERSATION_MODEL
FALLBACK_MODEL = REASONING_MODEL
LOCAL_FALLBACK_MODEL = os.getenv("LOCAL_FALLBACK_MODEL", "phi3:mini")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# --- Memory ---
MEMORY_DB = os.getenv("MEMORY_DB", "chromadb")
MEMORY_PATH = os.getenv("MEMORY_PATH", "./memory/chroma")
USER_PROFILE_PATH = os.getenv("USER_PROFILE_PATH", "./memory/profiles/user_profile.json")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "15"))

# --- Voice ---
WAKE_WORD = os.getenv("WAKE_WORD", "hey nira")
STT_PROVIDER = os.getenv("STT_PROVIDER", "whisper")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "piper")

# --- Browser ---
BROWSER_PROVIDER = os.getenv("BROWSER_PROVIDER", "playwright")
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
ALLOW_BROWSER_AUTOMATION = os.getenv("ALLOW_BROWSER_AUTOMATION", "true").lower() == "true"

# --- Security ---
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"
CONFIRM_FILE_DELETE = os.getenv("CONFIRM_FILE_DELETE", "true").lower() == "true"
ALLOW_TERMINAL_EXECUTION = os.getenv("ALLOW_TERMINAL_EXECUTION", "false").lower() == "true"
ALLOWED_DIRECTORIES = [d.strip() for d in os.getenv("ALLOWED_DIRECTORIES", "./workspace,./projects").split(",") if d.strip()]

# --- Paths ---
SAFE_WORKSPACE = os.getenv("SAFE_WORKSPACE", "./workspace")
LOG_PATH = os.getenv("LOG_PATH", "./logs")

# --- Debug ---
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
STREAM_OUTPUT = os.getenv("STREAM_OUTPUT", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Derived ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# --- Cognitive thresholds ---
HABIT_CONFIDENCE_THRESHOLD = 0.6
HABIT_LEARNING_RATE = 0.15
HABIT_DECAY_RATE = 0.02
MOOD_CONFIDENCE_THRESHOLD = 0.4
INTENT_CONFIDENCE_THRESHOLD = 0.5
SHORT_TERM_WINDOW_SIZE = 20
WORKING_MEMORY_MAX_GOALS = 3
