"""Patrón Strategy: políticas intercambiables de descuento y despacho."""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

from .domain import Order


def _clp(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Decimal:
        """Retorna el monto (CLP) a descontar del subtotal."""


class NoDiscount(DiscountStrategy):
    def calculate(self, order: Order) -> Decimal:
        return Decimal("0")


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: int):
        if not 0 <= percent <= 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        self.percent = percent

    def calculate(self, order: Order) -> Decimal:
        return _clp(order.subtotal * Decimal(self.percent) / Decimal(100))


class MinimumPurchaseDiscount(DiscountStrategy):
    """Descuento fijo si el subtotal supera un monto mínimo."""

    def __init__(self, minimum: Decimal, amount: Decimal):
        self.minimum = Decimal(minimum)
        self.amount = Decimal(amount)

    def calculate(self, order: Order) -> Decimal:
        return self.amount if order.subtotal >= self.minimum else Decimal("0")


class DeliveryFeePolicy(ABC):
    @abstractmethod
    def fee(self, order: Order) -> Decimal: ...


class FlatDeliveryFee(DeliveryFeePolicy):
    def __init__(self, amount: Decimal = Decimal("1990")):
        self.amount = Decimal(amount)

    def fee(self, order: Order) -> Decimal:
        return self.amount


class FreeDeliveryOver(DeliveryFeePolicy):
    def __init__(self, threshold: Decimal = Decimal("20000"),
                 amount: Decimal = Decimal("1990")):
        self.threshold = Decimal(threshold)
        self.amount = Decimal(amount)

    def fee(self, order: Order) -> Decimal:
        return Decimal("0") if order.subtotal >= self.threshold else self.amount
