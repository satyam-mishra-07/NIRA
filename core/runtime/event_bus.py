from collections import defaultdict
from typing import Callable, Any


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def on(self, event: str, handler: Callable):
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable):
        if handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def emit(self, event: str, data: Any = None):
        for handler in self._handlers[event]:
            handler(data)

    def clear(self):
        self._handlers.clear()


_bus = EventBus()


def get_bus():
    return _bus
