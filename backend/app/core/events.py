from typing import Any, Callable, Dict, List
import asyncio
from backend.app.core.logging import logger


class EventSystem:
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_type: str, listener: Callable[..., Any]) -> None:
        """Subscribe a listener callable to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable[..., Any]) -> None:
        """Unsubscribe a listener callable from an event type."""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    async def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """Publish an event to all subscribers asynchronously."""
        if event_type not in self._listeners:
            return

        tasks = []
        for listener in self._listeners[event_type]:
            if asyncio.iscoroutinefunction(listener):
                tasks.append(asyncio.create_task(listener(*args, **kwargs)))
            else:
                try:
                    listener(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        "Error running sync listener",
                        event_type=event_type,
                        error=str(e),
                    )

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    logger.error(
                        "Error in event listener execution",
                        event_type=event_type,
                        error=str(res),
                    )


# Global event bus
event_bus = EventSystem()
