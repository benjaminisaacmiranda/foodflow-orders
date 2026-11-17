from decimal import Decimal

import pytest

from orders.domain import OrderError, OrderStatus
from orders.events import EventBus
from orders.pricing import PercentageDiscount
from orders.repository import InMemoryOrderRepository
from orders.service import OrderService

ITEMS = [{"product_id": "p1", "name": "Pizza", "unit_price": 10000, "quantity": 2}]


@pytest.fixture
def setup():
    bus = EventBus()
    received = []
    for ev in ("order.created", "order.paid", "order.cancelled"):
        bus.subscribe(ev, lambda p, ev=ev: received.append((ev, p)))
    svc = OrderService(InMemoryOrderRepository(), bus, discount=PercentageDiscount(10))
    return svc, received


def test_crear_pedido_aplica_descuento_y_publica_evento(setup):
    svc, received = setup
    o = svc.create_order("c1", "r1", ITEMS)
    assert o.discount == Decimal("2000")
    assert o.delivery_fee == Decimal("0")  # subtotal 20000 => despacho gratis
    assert o.total == Decimal("18000")
    assert received[0][0] == "order.created"


def test_pedido_vacio_rechazado(setup):
    svc, _ = setup
    with pytest.raises(OrderError):
        svc.create_order("c1", "r1", [])


def test_cambio_de_estado_publica_evento(setup):
    svc, received = setup
    o = svc.create_order("c1", "r1", ITEMS)
    svc.change_status(o.id, OrderStatus.PAID)
    assert ("order.paid", {"order_id": o.id}) in received


def test_estado_inexistente(setup):
    svc, _ = setup
    with pytest.raises(OrderError):
        svc.change_status("no-existe", OrderStatus.PAID)
    with pytest.raises(OrderError):
        svc.get_order("no-existe")


def test_listar_por_cliente(setup):
    svc, _ = setup
    svc.create_order("c1", "r1", ITEMS)
    svc.create_order("c2", "r1", ITEMS)
    assert len(svc.repository.list_by_customer("c1")) == 1


def test_fallo_de_un_suscriptor_no_afecta_a_otros():
    bus = EventBus()
    ok = []
    bus.subscribe("e", lambda p: 1 / 0)
    bus.subscribe("e", lambda p: ok.append(p))
    assert bus.publish("e", {"x": 1}) == 1
    assert ok == [{"x": 1}]
