"""
cognition/intent/json_parser.py

WHY THIS EXISTS AS A SEPARATE MODULE:
  The original classifier.py had inline JSON cleaning with a single regex.
  This worked for well-formed responses but failed for:

  1. Trailing garbage:     { "intent": "chat" } Some explanation text
  2. Leading text:         Sure! Here's the JSON: { "intent": ... }
  3. Partial output:       { "intent": "chat"\n  ← model was cut off
  4. Escaped markdown:     ```json\n{ ... }\n```
  5. Unicode/Hinglish in reason field breaking JSON string escaping
  6. Double-encoded JSON:  "{\\"intent\\": \\"chat\\"}"  (LLM stringified it)

  By isolating parsing here, we can:
  - Improve extraction without touching classifier logic
  - Log failure modes for analysis
  - Add new extraction strategies without risk

STRATEGY (in order of attempt):
  1. Strip markdown fences
  2. Find outermost balanced { } block (not just first match)
  3. Attempt direct parse
  4. Attempt repair for common truncation patterns
  5. Return None on total failure (caller decides fallback)
"""

import json
import re
from typing import Optional


def extract_json(raw: str) -> Optional[dict]:
    """
    Robustly extracts the first valid JSON object from a raw LLM response.
    Returns a dict on success, None on failure.
    Never raises.
    """
    if not raw or not isinstance(raw, str):
        return None

    text = raw.strip()

    # ── Step 1: Strip markdown code fences ───────────────────────────────────
    # Handles: ```json\n{...}\n``` and ```\n{...}\n```
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.replace("```", "").strip()

    # ── Step 2: Strip common LLM preamble patterns ───────────────────────────
    # "Here is the JSON:", "Sure!", "Classification:", etc.
    text = re.sub(r"^[A-Za-z !:,\-]+\n", "", text).strip()

    # ── Step 3: Find balanced outermost { } block ────────────────────────────
    # re.search(r"\{.*\}", re.DOTALL) is WRONG for nested objects.
    # It finds the FIRST { and the LAST } which can span unrelated content.
    # We need the OUTERMOST balanced block.
    json_str = _extract_balanced_braces(text)

    if not json_str:
        return None

    # ── Step 4: Attempt direct parse ─────────────────────────────────────────
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # ── Step 5: Attempt repair for common truncation ─────────────────────────
    repaired = _attempt_repair(json_str)
    if repaired:
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    # ── Step 6: Total failure ─────────────────────────────────────────────────
    return None


def _extract_balanced_braces(text: str) -> Optional[str]:
    """
    Finds the first outermost balanced { } block.
    Uses a counter-based approach, not regex, because regex cannot count nesting.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start=start):
        if escape_next:
            escape_next = False
            continue

        if ch == "\\" and in_string:
            escape_next = True
            continue

        if ch == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    # Truncated — return what we have so repair can try
    return text[start:] if depth > 0 else None


def _attempt_repair(fragment: str) -> Optional[str]:
    """
    Attempts to close a truncated JSON object.
    Handles the most common LLM truncation pattern:
      { "intent": "chat", "confidence": 0.8
    by closing open strings and braces.
    """
    if not fragment:
        return None

    text = fragment.rstrip().rstrip(",")  # trailing comma before truncation

    # Count unclosed braces
    depth = 0
    in_string = False
    escape_next = False

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1

    if in_string:
        text += '"'  # close open string

    text += "}" * max(depth, 0)  # close open braces

    return text if depth > 0 or in_string else None