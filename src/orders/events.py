"""Patrón Observer / Publish-Subscribe: bus de eventos de dominio en memoria."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List

Handler = Callable[[Dict], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, payload: Dict) -> int:
        """Notifica a los suscriptores. Un fallo en uno no afecta a los demás."""
        delivered = 0
        for handler in list(self._handlers[event_type]):
            try:
                handler(payload)
                delivered += 1
            except Exception:  # aislamiento de fallos entre consumidores
                continue
        return delivered
