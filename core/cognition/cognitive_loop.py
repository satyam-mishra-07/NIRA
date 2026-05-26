from __future__ import annotations

from core.state.runtime_state import RuntimeState, RuntimeStateManager
from core.cognition.state_manager import CognitiveStateManager
from core.runtime.event_bus import get_bus
from core.runtime.context_manager import ContextManager
from core.orchestration.router import OrchestrationRouter, ExecutionRouter, RouteDecision
from core.orchestration.execution_context import ExecutionContext
from core.orchestration.tool_planner import ToolPlanner
from cognition.mood.analyzer import MoodAnalyzer
from cognition.habits.observer import HabitObserver
from cognition.habits.habit_store import HabitStore
from cognition.intent.predictor import IntentPredictor
from cognition.intent.signal import CognitionSignal
from cognition.reflection.memory_reflection import MemoryReflection
from cognition.mood.emotional_memory import MoodEmotionalMemory

from providers.llm.model_router import ModelRouter
from memory.short_term.short_term_memory import ShortTermMemory
from memory.working.working_memory import WorkingMemory
from personality.personality_engine import PersonalityEngine
from cognition.habits.reinforcement import HabitReinforcement
from security.validator import InputValidator
from security.guardrails import Guardrails
from config.settings import DEBUG


class CognitiveLoop:
    def __init__(
        self,
        state_manager: RuntimeStateManager,
        cognitive_state: CognitiveStateManager,
        mood_analyzer: MoodAnalyzer,
        habit_observer: HabitObserver,
        habit_store: HabitStore,
        intent_predictor: IntentPredictor,
        model_router: ModelRouter,
        short_term: ShortTermMemory,
        working_memory: WorkingMemory,
        personality: PersonalityEngine,
        validator: InputValidator,
        guardrails: Guardrails,
        memory_reflection: MemoryReflection,
        mood_emotional_memory: MoodEmotionalMemory,
        habit_reinforcement: HabitReinforcement,
        execution_router: ExecutionRouter | None = None,
        tool_planner: ToolPlanner | None = None,
    ):
        self.state_manager = state_manager
        self.cognitive_state = cognitive_state
        self.mood_analyzer = mood_analyzer
        self.habit_observer = habit_observer
        self.habit_store = habit_store
        self.intent_predictor = intent_predictor
        self.model_router = model_router
        self.short_term = short_term
        self.working_memory = working_memory
        self.personality = personality
        self.validator = validator
        self.guardrails = guardrails
        self.memory_reflection = memory_reflection
        self.mood_emotional_memory = mood_emotional_memory
        self.summarize_interval = 10
        self.habit_reinforcement = habit_reinforcement
        self.decay_interval = 50

        self.execution_router = execution_router
        self.tool_planner = tool_planner

        self.context_manager = ContextManager(
            cognitive_state, short_term, working_memory, personality
        )
        self.bus = get_bus()

        self.cognitive_state.seed_habits_from_store(self.habit_store.get_all())

        self.execution_context = ExecutionContext()
        self.orchestration_router = OrchestrationRouter(self.execution_context)

    def process(self, user_input: str, stream_handler=None):
        if not self.state_manager.can_process():
            return

        self.state_manager.transition(RuntimeState.PROCESSING)
        self.cognitive_state.increment_interaction()

        validation = self.validator.validate_message(user_input)
        if not validation["safe"]:
            msg = f"I can't process that request. [{validation['reason']}]"
            if stream_handler:
                stream_handler(msg)
            self.state_manager.transition(RuntimeState.IDLE)
            return msg

        context = self.context_manager.build()
        self.working_memory.update_from_input(user_input)
        self.short_term.add_user_message(user_input)

        mood_result = self.mood_analyzer.analyze(user_input, context)
        self.cognitive_state.update_mood(mood_result)
        self.mood_emotional_memory.store_mood(mood_result)

        observations = self.habit_observer.observe(user_input, context)
        self.cognitive_state.update_habits(observations)
        if observations:
            self.habit_store.update_from_observations(observations)

        signal: CognitionSignal = self.intent_predictor.predict(user_input, context)
        self.cognitive_state.update_intent(signal.to_dict())

        if self.execution_router is not None:
            route = self.execution_router.route(signal)

            tool_context = ""
            if self.tool_planner is not None and route.activate_tools:
                tool_result = self.tool_planner.execute(route.tool_type, user_input)
                if tool_result:
                    if tool_result.success:
                        tool_context = tool_result.to_context_string()
                    else:
                        tool_context = f"[Tool {route.tool_type} failed: {tool_result.error}]"

            model = self.model_router.select(route)
        else:
            intent_result = signal.to_dict()

            orchestration_decision = self.orchestration_router.route(intent_result, context)
            if orchestration_decision in ("reasoning", "browser_request", "tool_execution", "file_operation"):
                intent_result["requires_reasoning"] = True

            context = self.context_manager.build()

            model = self.model_router.select(intent_result)
            route = None
            tool_context = ""

        self.state_manager.transition(RuntimeState.RESPONDING)
        if model is self.model_router.reasoning:
            system_prompt = self.personality.build_reasoning_prompt(context)
        else:
            system_prompt = self.personality.build_system_prompt(context)

        if tool_context:
            context = context + f"\n\n{tool_context}"

        try:
            response = model.generate(
                system_prompt=system_prompt,
                user_message=user_input,
                context=context,
                stream=stream_handler is not None,
                stream_handler=stream_handler,
            )
        except Exception as e:
            if DEBUG:
                print(f"\n[error] {type(model).__name__} failed: {e}")
            fallback = self.model_router.conversation if model is self.model_router.reasoning else self.model_router.reasoning
            fallback_prompt = (
                self.personality.build_reasoning_prompt(context)
                if fallback is self.model_router.reasoning
                else self.personality.build_system_prompt(context)
            )
            try:
                if DEBUG:
                    print(f"[cognitive_loop] Falling back to {type(fallback).__name__}")
                response = fallback.generate(
                    system_prompt=fallback_prompt,
                    user_message=user_input,
                    context=context,
                    stream=stream_handler is not None,
                    stream_handler=stream_handler,
                )
            except Exception as e2:
                if DEBUG:
                    print(f"\n[error] Fallback also failed: {e2}")
                self.state_manager.transition(RuntimeState.IDLE)
                return "I hit a snag. Could you try rephrasing that?"

        if not response:
            response = "I'm not sure what to say to that."

        response = self.guardrails.filter_response(response)

        self.short_term.add_assistant_message(response)

        event_payload = {
            "input": user_input,
            "response": response,
            "mood": mood_result,
            "intent": signal.to_dict(),
        }
        if route is not None:
            event_payload["route"] = route.to_dict()

        self.bus.emit("cognitive:complete", event_payload)

        if self.cognitive_state.interaction_count % self.summarize_interval == 0:
            self.memory_reflection.reflect(self.short_term.messages)

        if self.cognitive_state.interaction_count % self.decay_interval == 0:
            habits = self.habit_store.get_all()
            decayed = self.habit_reinforcement.decay_habits(habits)
            self.habit_store.save(decayed)
            self.cognitive_state.seed_habits_from_store(decayed)

        self.state_manager.transition(RuntimeState.IDLE)
        return response
