SYSTEM_PROMPT_BASE = """
You are NIRA — an ambient cognitive workspace companion created by Satyam Mishra.

CORE RULES:
- Speak briefly and naturally (1-4 sentences).
- Prioritize execution over long explanations.
- Respond in the same language the user uses (English / Hindi / Hinglish).
- Never be robotic or overly formal.
- Never diagnose mental health or pretend certainty about emotions.
"""

MOOD_ANALYSIS_PROMPT = """
Analyze the user's emotional tone from their message.

Return a JSON object:
{
  "mood": "focused|frustrated|curious|neutral|stressed|playful|tired",
  "confidence": <0.0-1.0>,
  "reason": "<brief why>"
}

Only infer what is strongly supported by the text.
Never invent emotions.
Default to "neutral" with low confidence if uncertain.

User message: {message}
Context: {context}
"""

HABIT_OBSERVATION_PROMPT = """
Based on the user's message and current context, identify any repeatable behavioral patterns.

Return a JSON array:
[
  {
    "pattern": "<pattern_name>",
    "confidence_delta": <0.0-0.2>,
    "evidence": "<what was observed>"
  }
]

Known pattern types: coding_assistance, music_while_coding, late_night_work,
concise_preference, detailed_explanation, casual_conversation, file_operation

Message: {message}
Context: {context}
"""

INTENT_CLASSIFICATION_PROMPT = """
Classify the user's intent from their message.

Categories:
- coding_help: Programming questions, debugging, code review
- casual_chat: General conversation, greetings, personal topics
- file_operation: Create/read/update/delete files
- browser_request: Web search, browsing, research
- productivity: Task management, planning, organization
- system: NIRA configuration, status, settings
- tool_execution: Run commands, execute code

Return JSON:
{
  "intent": "<category>",
  "confidence": <0.0-1.0>,
  "sub_intent": "<optional specificity>"
}

Message: {message}
"""

SUMMARIZATION_PROMPT = """
Summarize the following conversation exchange concisely.

Focus on:
- Key topics discussed
- User's expressed needs or intents
- Decisions or conclusions reached
- Emotional tone

Conversation:
{messages}

Summary:
"""
