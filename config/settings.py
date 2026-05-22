import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER")

PRIMARY_MODEL = os.getenv("PRIMARY_MODEL")

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))