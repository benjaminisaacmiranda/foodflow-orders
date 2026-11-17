"""Capa de aplicación: casos de uso del módulo de pedidos."""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, List, Optional

from .domain import Order, OrderError, OrderItem, OrderStatus
from .events import EventBus
from .pricing import DeliveryFeePolicy, DiscountStrategy, FreeDeliveryOver, NoDiscount
from .repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository, bus: EventBus,
                 discount: Optional[DiscountStrategy] = None,
                 delivery: Optional[DeliveryFeePolicy] = None) -> None:
        self.repository = repository
        self.bus = bus
        self.discount = discount or NoDiscount()
        self.delivery = delivery or FreeDeliveryOver()

    def create_order(self, customer_id: str, restaurant_id: str,
                     items: Iterable[dict]) -> Order:
        order_items: List[OrderItem] = [
            OrderItem(i["product_id"], i["name"], Decimal(str(i["unit_price"])),
                      int(i["quantity"]))
            for i in items
        ]
        if not order_items:
            raise OrderError("El pedido debe contener al menos un ítem")
        order = Order(customer_id=customer_id, restaurant_id=restaurant_id,
                      items=order_items)
        order.discount = self.discount.calculate(order)
        order.delivery_fee = self.delivery.fee(order)
        self.repository.save(order)
        self.bus.publish("order.created", {"order_id": order.id, "total": str(order.total)})
        return order

    def change_status(self, order_id: str, new_status: OrderStatus) -> Order:
        order = self.repository.get(order_id)
        if order is None:
            raise OrderError("Pedido no encontrado")
        order.transition_to(new_status)
        self.repository.save(order)
        self.bus.publish(f"order.{new_status.name.lower()}", {"order_id": order.id})
        return order

    def get_order(self, order_id: str) -> Order:
        order = self.repository.get(order_id)
        if order is None:
            raise OrderError("Pedido no encontrado")
        return order
