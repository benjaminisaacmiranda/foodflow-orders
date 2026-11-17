from decimal import Decimal

import pytest

from orders.domain import Order, OrderError, OrderItem, OrderStatus


def make_order():
    return Order("c1", "r1", [OrderItem("p1", "Pizza", Decimal("9990"), 2),
                              OrderItem("p2", "Bebida", Decimal("1500"), 1)])


def test_subtotal_y_total_sin_descuento():
    o = make_order()
    assert o.subtotal == Decimal("21480")
    assert o.total == Decimal("21480")


def test_total_con_descuento_y_despacho():
    o = make_order()
    o.discount = Decimal("1000")
    o.delivery_fee = Decimal("1990")
    assert o.total == Decimal("22470")


def test_total_nunca_negativo_por_descuento():
    o = make_order()
    o.discount = Decimal("999999")
    assert o.total == Decimal("0")


@pytest.mark.parametrize("qty", [0, -1])
def test_cantidad_invalida(qty):
    with pytest.raises(OrderError):
        OrderItem("p", "x", Decimal("100"), qty)


def test_precio_negativo():
    with pytest.raises(OrderError):
        OrderItem("p", "x", Decimal("-1"), 1)


def test_ciclo_de_vida_valido():
    o = make_order()
    for s in (OrderStatus.PAID, OrderStatus.PREPARING, OrderStatus.READY,
              OrderStatus.DELIVERED):
        o.transition_to(s)
    assert o.status is OrderStatus.DELIVERED


def test_transicion_invalida():
    o = make_order()
    with pytest.raises(OrderError):
        o.transition_to(OrderStatus.DELIVERED)


def test_pedido_cancelado_es_final():
    o = make_order()
    o.transition_to(OrderStatus.CANCELLED)
    with pytest.raises(OrderError):
        o.transition_to(OrderStatus.PAID)
