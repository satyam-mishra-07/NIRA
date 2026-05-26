import sys

from core.runtime.lifecycle import RuntimeLifecycle
from core.cognition.cognitive_loop import CognitiveLoop
from cognition.mood.analyzer import MoodAnalyzer
from cognition.habits.observer import HabitObserver
from cognition.habits.confidence_engine import ConfidenceEngine
from cognition.habits.pattern_detector import PatternDetector
from cognition.intent.predictor import IntentPredictor
from cognition.intent.classifier import IntentClassifier
from memory.short_term.short_term_memory import ShortTermMemory
from memory.working.working_memory import WorkingMemory
from memory.profile.profile_manager import ProfileManager
from memory.habits.habit_memory import HabitMemory
from memory.emotional.emotional_memory import EmotionalMemory
from memory.summaries.summary_memory import SummaryMemory
from memory.conversation.conversation_store import ConversationStore
from personality.personality_engine import PersonalityEngine
from providers.llm.model_router import ModelRouter
from config.settings import DEBUG


def stream_token(token: str):
    print(token, end="", flush=True)


def main():
    runtime = RuntimeLifecycle()
    runtime.boot()

    short_term = ShortTermMemory()
    working_memory = WorkingMemory()
    profile = ProfileManager()
    habit_memory = HabitMemory()
    emotional_memory = EmotionalMemory()
    summary_memory = SummaryMemory()
    conversation_store = ConversationStore()
    personality = PersonalityEngine()

    confidence_engine = ConfidenceEngine()
    pattern_detector = PatternDetector()
    model_router = ModelRouter()

    mood_analyzer = MoodAnalyzer()
    habit_observer = HabitObserver(confidence_engine, pattern_detector)
    intent_predictor = IntentPredictor(IntentClassifier())

    cognitive_loop = CognitiveLoop(
        state_manager=runtime.state,
        cognitive_state=runtime.cognitive_state,
        mood_analyzer=mood_analyzer,
        habit_observer=habit_observer,
        intent_predictor=intent_predictor,
        model_router=model_router,
        short_term=short_term,
        working_memory=working_memory,
        personality=personality,
    )

    print("\nNIRA is online. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not user_input.strip():
            continue

        if user_input.lower() in ("exit", "quit"):
            print("\nNIRA: See you later, Satyam.")
            break

        profile.increment_interactions()

        print("NIRA: ", end="", flush=True)
        response = cognitive_loop.process(
            user_input,
            stream_handler=stream_token if DEBUG else None,
        )
        if response:
            print()
            conversation_store.append("user", user_input)
            conversation_store.append("assistant", response)

    runtime.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    main()
