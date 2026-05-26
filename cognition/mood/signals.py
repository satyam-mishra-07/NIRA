import re

class MoodSignals:
    @staticmethod
    def extract(message: str) -> dict:
        return {
            "exclamation_count": message.count("!"),
            "question_count": message.count("?"),
            "word_count": len(message.split()),
            "has_code": bool(re.search(r"```|def |class |function|import ", message)),
            "has_positive": any(w in message.lower() for w in ["nice", "good", "great", "thanks", "perfect", "awesome"]),
            "has_negative": any(w in message.lower() for w in ["bad", "wrong", "broken", "hate", "terrible", "awful"]),
        }
