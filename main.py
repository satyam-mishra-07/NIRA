import sys

from core.runtime.lifecycle import RuntimeLifecycle
from core.cognition.cognitive_loop import CognitiveLoop
from cognition.intent.signal import CognitionSignal             # typed signal contract
from core.orchestration.router import ExecutionRouter           # NEW: replaces fragile string routing
from core.orchestration.tool_planner import ToolPlanner         # NEW: separated tool execution layer

from cognition.mood.analyzer import MoodAnalyzer
from cognition.habits.observer import HabitObserver
from cognition.habits.confidence_engine import ConfidenceEngine
from cognition.habits.pattern_detector import PatternDetector
from cognition.habits.habit_store import HabitStore
from cognition.intent.predictor import IntentPredictor
from cognition.intent.classifier import CognitionAssessor       # RENAMED: was IntentClassifier
from cognition.reflection.memory_reflection import MemoryReflection
from cognition.reflection.summarizer import ConversationSummarizer

from memory.short_term.short_term_memory import ShortTermMemory
from memory.working.working_memory import WorkingMemory
from memory.profile.profile_manager import ProfileManager
from memory.habits.habit_memory import HabitMemory
from memory.emotional.emotional_memory import EmotionalMemory
from cognition.mood.emotional_memory import MoodEmotionalMemory
from memory.summaries.summary_memory import SummaryMemory
from memory.conversation.conversation_store import ConversationStore

from personality.personality_engine import PersonalityEngine
from cognition.habits.reinforcement import HabitReinforcement
from providers.llm.model_router import ModelRouter
from security.validator import InputValidator
from security.guardrails import Guardrails
from config.settings import DEBUG, STREAM_OUTPUT


def safe_print(text: str, end: str = "\n", flush: bool = False):
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        safe = text.encode("ascii", errors="replace").decode("ascii")
        print(safe, end=end, flush=flush)


def stream_token(token: str):
    safe_print(token, end="", flush=True)


def main():
    runtime = RuntimeLifecycle()
    runtime.boot()

    # ── Memory layers ─────────────────────────────────────────────────────────
    short_term = ShortTermMemory()
    working_memory = WorkingMemory()
    profile = ProfileManager()
    habit_memory = HabitMemory()
    emotional_memory = EmotionalMemory()
    mood_emotional_memory = MoodEmotionalMemory(emotional_memory)
    summary_memory = SummaryMemory()
    conversation_store = ConversationStore()
    personality = PersonalityEngine()

    # ── Habit + confidence layer ──────────────────────────────────────────────
    confidence_engine = ConfidenceEngine()
    habit_reinforcement = HabitReinforcement(confidence_engine)
    pattern_detector = PatternDetector()
    model_router = ModelRouter()

    # ── Cognition layer ───────────────────────────────────────────────────────
    mood_analyzer = MoodAnalyzer()
    habit_observer = HabitObserver(confidence_engine, pattern_detector)
    habit_store = HabitStore(habit_memory)
    validator = InputValidator()
    guardrails = Guardrails()
    summarizer = ConversationSummarizer()
    memory_reflection = MemoryReflection(summary_memory, summarizer)

    # ── NEW: Cognitive routing architecture ───────────────────────────────────
    # CognitionAssessor replaces IntentClassifier.
    # It assesses all four dimensions (intent, reasoning depth,
    # tool need, response depth) and returns a typed CognitionSignal.
    assessor = CognitionAssessor()

    # IntentPredictor still wraps the assessor for backward compatibility
    # with cognitive_loop.py. Update predictor.py to accept CognitionAssessor
    # if it type-checks the injected classifier (see note below).
    intent_predictor = IntentPredictor(assessor)

    # ExecutionRouter reads CognitionSignal and decides:
    #   - which model track (reasoning_model / conversational_model)
    #   - whether to activate the tool planner
    execution_router = ExecutionRouter()

    # ToolPlanner is a separate layer — completely independent of model selection.
    # Wire it into cognitive_loop.py so it can be called after routing.
    tool_planner = ToolPlanner()

    # ── Cognitive loop ────────────────────────────────────────────────────────
    cognitive_loop = CognitiveLoop(
        state_manager=runtime.state,
        cognitive_state=runtime.cognitive_state,
        mood_analyzer=mood_analyzer,
        habit_observer=habit_observer,
        habit_store=habit_store,
        intent_predictor=intent_predictor,
        execution_router=execution_router,      # NEW: pass router in
        tool_planner=tool_planner,              # NEW: pass tool planner in
        model_router=model_router,
        short_term=short_term,
        working_memory=working_memory,
        personality=personality,
        validator=validator,
        guardrails=guardrails,
        memory_reflection=memory_reflection,
        mood_emotional_memory=mood_emotional_memory,
        habit_reinforcement=habit_reinforcement,
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
            safe_print("\nNIRA: See you later, Satyam.")
            break

        profile.increment_interactions()

        streaming = DEBUG and STREAM_OUTPUT
        safe_print("NIRA: ", end="", flush=True)
        try:
            response = cognitive_loop.process(
                user_input,
                stream_handler=stream_token if streaming else None,
            )
        except Exception as e:
            print(f"\n[error] {e}")
            continue

        if response:
            if streaming:
                safe_print("")
            else:
                safe_print(response)
            conversation_store.append("user", user_input)
            conversation_store.append("assistant", response)

    runtime.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    main()