import pytest

from orders.api import create_app

BODY = {"customer_id": "c1", "restaurant_id": "r1",
        "items": [{"product_id": "p1", "name": "Pizza", "unit_price": 9990, "quantity": 2}]}


@pytest.fixture
def client():
    return create_app().test_client()


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_crear_y_consultar_pedido(client):
    r = client.post("/orders", json=BODY)
    assert r.status_code == 201
    oid = r.get_json()["id"]
    assert client.get(f"/orders/{oid}").get_json()["status"] == "CREADO"


def test_campo_requerido(client):
    r = client.post("/orders", json={"restaurant_id": "r1"})
    assert r.status_code == 400


def test_pedido_sin_items(client):
    r = client.post("/orders", json={**BODY, "items": []})
    assert r.status_code == 422


def test_pedido_inexistente(client):
    assert client.get("/orders/xyz").status_code == 404


def test_cambio_de_estado_valido_e_invalido(client):
    oid = client.post("/orders", json=BODY).get_json()["id"]
    ok = client.patch(f"/orders/{oid}/status", json={"status": "PAID"})
    assert ok.status_code == 200 and ok.get_json()["status"] == "PAGADO"
    bad = client.patch(f"/orders/{oid}/status", json={"status": "DELIVERED"})
    assert bad.status_code == 409
    assert client.patch(f"/orders/{oid}/status", json={"status": "FOO"}).status_code == 400
    assert client.patch("/orders/nope/status", json={"status": "PAID"}).status_code == 404
