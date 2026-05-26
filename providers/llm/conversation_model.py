from providers.llm.openrouter_provider import get_openrouter
from config.settings import PRIMARY_MODEL, REQUEST_TIMEOUT, DEBUG, STREAM_OUTPUT

class ConversationModel:
    def __init__(self):
        self.client = get_openrouter()
        self.model = PRIMARY_MODEL
        self.timeout = REQUEST_TIMEOUT

    def generate(self, system_prompt: str, user_message: str, context: dict = None, stream: bool = False, stream_handler=None) -> str:
        messages = [{"role": "system", "content": system_prompt}]

        if context and "recent_history" in context:
            for msg in context["recent_history"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        if DEBUG:
            print(f"[conversation_model] Using: {self.model}")
            print(f"[conversation_model] Stream: {stream}")

        kwargs = {
            "model": self.model,
            "messages": messages,
            "timeout": self.timeout,
            "max_tokens": 512,
            "temperature": 0.7,
        }

        if stream and STREAM_OUTPUT:
            kwargs["stream"] = True
            response = self.client.chat.completions.create(**kwargs)
            full = ""
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content = delta.content
                        full += content
                        if stream_handler:
                            stream_handler(content)
            return full
        else:
            kwargs["stream"] = False
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
