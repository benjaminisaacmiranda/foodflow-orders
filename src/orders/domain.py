"""Modelo de dominio del módulo de pedidos (capa de dominio, sin dependencias externas)."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List
import uuid


class OrderError(Exception):
    """Error de regla de negocio del módulo de pedidos."""


class OrderStatus(str, Enum):
    CREATED = "CREADO"
    PAID = "PAGADO"
    PREPARING = "EN_PREPARACION"
    READY = "LISTO"
    DELIVERED = "ENTREGADO"
    CANCELLED = "CANCELADO"


# Patrón State (tabla de transiciones): define el ciclo de vida válido del pedido.
ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    name: str
    unit_price: Decimal
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise OrderError("La cantidad debe ser mayor a cero")
        if self.unit_price < 0:
            raise OrderError("El precio unitario no puede ser negativo")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    customer_id: str
    restaurant_id: str
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    discount: Decimal = Decimal("0")
    delivery_fee: Decimal = Decimal("0")
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def subtotal(self) -> Decimal:
        return sum((i.subtotal for i in self.items), Decimal("0"))

    @property
    def total(self) -> Decimal:
        return max(self.subtotal - self.discount, Decimal("0")) + self.delivery_fee

    def transition_to(self, new_status: OrderStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise OrderError(
                f"Transición inválida: {self.status.value} -> {new_status.value}"
            )
        self.status = new_status
