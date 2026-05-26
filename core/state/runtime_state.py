from enum import Enum


class RuntimeState(Enum):
    BOOTING = "booting"
    IDLE = "idle"
    PROCESSING = "processing"
    RESPONDING = "responding"
    SHUTDOWN = "shutdown"


class RuntimeStateManager:
    def __init__(self):
        self._state = RuntimeState.BOOTING
        self._listeners = []

    @property
    def state(self):
        return self._state

    def transition(self, new_state: RuntimeState):
        prev = self._state
        self._state = new_state
        for listener in self._listeners:
            listener(prev, new_state)

    def on_transition(self, callback):
        self._listeners.append(callback)

    def is_idle(self):
        return self._state == RuntimeState.IDLE

    def is_processing(self):
        return self._state == RuntimeState.PROCESSING

    def can_process(self):
        return self._state in (RuntimeState.IDLE, RuntimeState.BOOTING)
