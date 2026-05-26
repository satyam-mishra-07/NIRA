from providers.llm.openrouter_provider import get_openrouter
from config.settings import FALLBACK_MODEL, LLM_TIMEOUT, DEBUG

class ReasoningModel:
    def __init__(self):
        self.client = get_openrouter()
        self.model = FALLBACK_MODEL
        self.timeout = LLM_TIMEOUT

    def generate(self, system_prompt: str, user_message: str, context: dict = None, stream: bool = False, stream_handler=None) -> str:
        messages = [{"role": "system", "content": system_prompt}]

        if context and "recent_history" in context:
            for msg in context["recent_history"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        if DEBUG:
            print(f"[reasoning_model] Using: {self.model}")

        if stream:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=self.timeout,
                max_tokens=2048,
                temperature=0.3,
                stream=True,
            )
            full = ""
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        full += delta.content
                        if stream_handler:
                            stream_handler(delta.content)
            return full

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
            max_tokens=2048,
            temperature=0.3,
        )
        return response.choices[0].message.content
