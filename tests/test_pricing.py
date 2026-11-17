from decimal import Decimal

import pytest

from orders.domain import Order, OrderItem
from orders.pricing import (FlatDeliveryFee, FreeDeliveryOver,
                            MinimumPurchaseDiscount, NoDiscount,
                            PercentageDiscount)


def order(price="10000", qty=1):
    return Order("c", "r", [OrderItem("p", "x", Decimal(price), qty)])


def test_sin_descuento():
    assert NoDiscount().calculate(order()) == 0


def test_descuento_porcentual():
    assert PercentageDiscount(10).calculate(order("10000")) == Decimal("1000")


def test_descuento_porcentual_redondea_a_peso_entero():
    assert PercentageDiscount(15).calculate(order("3333")) == Decimal("500")


@pytest.mark.parametrize("p", [-1, 101])
def test_porcentaje_fuera_de_rango(p):
    with pytest.raises(ValueError):
        PercentageDiscount(p)


def test_descuento_por_compra_minima():
    s = MinimumPurchaseDiscount(Decimal("15000"), Decimal("2000"))
    assert s.calculate(order("15000")) == Decimal("2000")
    assert s.calculate(order("14999")) == Decimal("0")


def test_despacho_fijo():
    assert FlatDeliveryFee().fee(order()) == Decimal("1990")


def test_despacho_gratis_sobre_umbral():
    p = FreeDeliveryOver(Decimal("20000"))
    assert p.fee(order("20000")) == Decimal("0")
    assert p.fee(order("19999")) == Decimal("1990")
