import re

class InputValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r"rm\s+-rf", r"format\s+", r":\(\)\s*\{", r"sudo\s+",
            r"eval\(", r"exec\(", r"__import__\(", r"system\(",
            r"DROP\s+TABLE", r"DELETE\s+FROM",
        ]

    def sanitize(self, text: str) -> str:
        return text.strip()

    def is_safe(self, text: str) -> bool:
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True

    def validate_message(self, message: str) -> dict:
        clean = self.sanitize(message)
        safe = self.is_safe(clean)
        return {
            "clean": clean,
            "safe": safe,
            "reason": None if safe else "potentially dangerous pattern detected",
        }
