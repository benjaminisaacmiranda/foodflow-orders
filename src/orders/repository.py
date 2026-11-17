"""Patrón Repository: abstrae la persistencia del dominio."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .domain import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def get(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    def list_by_customer(self, customer_id: str) -> List[Order]: ...


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._data: Dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._data[order.id] = order

    def get(self, order_id: str) -> Optional[Order]:
        return self._data.get(order_id)

    def list_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._data.values() if o.customer_id == customer_id]
