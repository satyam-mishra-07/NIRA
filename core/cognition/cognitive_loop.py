from core.state.runtime_state import RuntimeState, RuntimeStateManager
from core.cognition.state_manager import CognitiveStateManager
from core.runtime.event_bus import get_bus
from core.runtime.context_manager import ContextManager
from cognition.mood.analyzer import MoodAnalyzer
from cognition.habits.observer import HabitObserver
from cognition.intent.predictor import IntentPredictor
from providers.llm.model_router import ModelRouter
from memory.short_term.short_term_memory import ShortTermMemory
from memory.working.working_memory import WorkingMemory
from personality.personality_engine import PersonalityEngine
from config.settings import DEBUG


class CognitiveLoop:
    def __init__(
        self,
        state_manager: RuntimeStateManager,
        cognitive_state: CognitiveStateManager,
        mood_analyzer: MoodAnalyzer,
        habit_observer: HabitObserver,
        intent_predictor: IntentPredictor,
        model_router: ModelRouter,
        short_term: ShortTermMemory,
        working_memory: WorkingMemory,
        personality: PersonalityEngine,
    ):
        self.state_manager = state_manager
        self.cognitive_state = cognitive_state
        self.mood_analyzer = mood_analyzer
        self.habit_observer = habit_observer
        self.intent_predictor = intent_predictor
        self.model_router = model_router
        self.short_term = short_term
        self.working_memory = working_memory
        self.personality = personality
        self.context_manager = ContextManager(
            cognitive_state, short_term, working_memory, personality
        )
        self.bus = get_bus()

    def process(self, user_input: str, stream_handler=None):
        if not self.state_manager.can_process():
            return

        self.state_manager.transition(RuntimeState.PROCESSING)
        self.cognitive_state.increment_interaction()

        # 1. Update activity context
        self.working_memory.update_from_input(user_input)
        self.short_term.add_user_message(user_input)

        # 2. Mood analysis
        mood_result = self.mood_analyzer.analyze(user_input, self.context_manager.build())
        self.cognitive_state.update_mood(mood_result)

        # 3. Habit observation
        observations = self.habit_observer.observe(user_input, self.context_manager.build())
        self.cognitive_state.update_habits(observations)

        # 4. Intent prediction
        intent_result = self.intent_predictor.predict(user_input, self.context_manager.build())
        self.cognitive_state.update_intent(intent_result)

        # 5. Build full context
        context = self.context_manager.build()

        # 6. Route to model
        model = self.model_router.select(intent_result)

        # 7. Generate response
        self.state_manager.transition(RuntimeState.RESPONDING)
        system_prompt = self.personality.build_system_prompt(context)

        response = model.generate(
            system_prompt=system_prompt,
            user_message=user_input,
            context=context,
            stream=stream_handler is not None,
            stream_handler=stream_handler,
        )

        # 8. Store in short-term memory
        self.short_term.add_assistant_message(response)

        # 9. Emit completion event
        self.bus.emit("cognitive:complete", {
            "input": user_input,
            "response": response,
            "mood": mood_result,
            "intent": intent_result,
        })

        self.state_manager.transition(RuntimeState.IDLE)
        return response
