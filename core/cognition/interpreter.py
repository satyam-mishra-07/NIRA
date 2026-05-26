import re


class Interpreter:
    def __init__(self):
        self.tool_pattern = re.compile(r"\[TOOL_CALL:(\w+):(.*)\]")

    def interpret(self, raw_response: str) -> dict:
        tool_match = self.tool_pattern.search(raw_response)
        clean_response = self.tool_pattern.sub("", raw_response).strip()

        result = {
            "response": clean_response,
            "tool_call": None,
            "requires_tool": tool_match is not None,
        }

        if tool_match:
            result["tool_call"] = {
                "tool": tool_match.group(1),
                "args": tool_match.group(2).strip(),
            }

        return result
