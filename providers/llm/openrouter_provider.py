from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

class OpenRouterClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

    def get_client(self) -> OpenAI:
        return self.client

_openrouter = OpenRouterClient()

def get_openrouter() -> OpenAI:
    return _openrouter.get_client()
