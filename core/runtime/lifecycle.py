from core.state.runtime_state import RuntimeStateManager, RuntimeState
from core.runtime.event_bus import get_bus
from core.cognition.state_manager import CognitiveStateManager
from core.orchestration.execution_context import ExecutionContext
from config.settings import DEBUG


class RuntimeLifecycle:
    def __init__(self):
        self.state = RuntimeStateManager()
        self.bus = get_bus()
        self.cognitive_state = CognitiveStateManager()
        self.execution_context = ExecutionContext()

    def boot(self):
        if DEBUG:
            print("[runtime] NIRA cognitive runtime booting...")
        self.state.transition(RuntimeState.BOOTING)
        self.bus.emit("runtime:boot", {"status": "starting"})
        self.execution_context.initialize()
        if DEBUG:
            print("[runtime] Event bus active.")
        self.state.transition(RuntimeState.IDLE)
        if DEBUG:
            print(f"[runtime] Runtime state: {self.state.state.value.upper()}")
            print("[runtime] Cognitive loop ready.")

    def shutdown(self):
        self.state.transition(RuntimeState.SHUTDOWN)
        self.bus.emit("runtime:shutdown", {"status": "shutting_down"})
        if DEBUG:
            print("[runtime] NIRA cognitive runtime shutting down.")
