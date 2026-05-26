from core.cognition.state_manager import CognitiveStateManager
from memory.short_term.short_term_memory import ShortTermMemory
from memory.working.working_memory import WorkingMemory
from personality.personality_engine import PersonalityEngine


class ContextManager:
    def __init__(
        self,
        cognitive_state: CognitiveStateManager,
        short_term: ShortTermMemory,
        working_memory: WorkingMemory,
        personality: PersonalityEngine,
    ):
        self.cognitive_state = cognitive_state
        self.short_term = short_term
        self.working_memory = working_memory
        self.personality = personality

    def build(self) -> dict:
        mood = self.cognitive_state.current_mood
        habits = self.cognitive_state.active_habits
        intent = self.cognitive_state.current_intent

        context = {
            "mood": mood,
            "habits": habits,
            "intent": intent,
            "working": {
                "current_task": self.working_memory.current_task,
                "active_file": self.working_memory.active_file,
                "goals": self.working_memory.goals,
            },
            "recent_history": self.short_term.get_recent_context(),
            "personality": self.personality.get_active_traits(),
        }

        return context
