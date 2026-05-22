from openai import OpenAI

from config.settings import (
    OPENROUTER_API_KEY,
    PRIMARY_MODEL,
    REQUEST_TIMEOUT
)

from personality.personality_engine import (
    build_system_prompt
)


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


def chat_with_nira(user_message: str):

    system_prompt = build_system_prompt()

    completion = client.chat.completions.create(
        model=PRIMARY_MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],

        timeout=REQUEST_TIMEOUT
    )

    return completion.choices[0].message.content