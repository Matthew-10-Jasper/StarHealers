import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Callable, Any, Optional
import json

class EventBus:
    """Central in-process event bus for cross-module real-time pub/sub."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event_type: str, data: Dict[str, Any], source_module: str):
        payload = {
            "event_type": event_type,
            "source_module": source_module,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                print(f"[EventBus Error] Exception handling {event_type}: {e}")

event_bus = EventBus()
