"""Capa de presentación: API REST (Flask) del módulo de pedidos."""
from __future__ import annotations

from flask import Flask, jsonify, request

from .domain import Order, OrderError, OrderStatus
from .events import EventBus
from .pricing import PercentageDiscount
from .repository import InMemoryOrderRepository
from .service import OrderService


def serialize(order: Order) -> dict:
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "restaurant_id": order.restaurant_id,
        "status": order.status.value,
        "subtotal": str(order.subtotal),
        "discount": str(order.discount),
        "delivery_fee": str(order.delivery_fee),
        "total": str(order.total),
        "items": [
            {"product_id": i.product_id, "name": i.name,
             "unit_price": str(i.unit_price), "quantity": i.quantity}
            for i in order.items
        ],
    }


def create_app(service: OrderService | None = None) -> Flask:
    app = Flask(__name__)
    svc = service or OrderService(InMemoryOrderRepository(), EventBus(),
                                  discount=PercentageDiscount(0))

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/orders")
    def create_order():
        data = request.get_json(silent=True) or {}
        try:
            order = svc.create_order(data["customer_id"], data["restaurant_id"],
                                     data.get("items", []))
        except KeyError as exc:
            return jsonify(error=f"Campo requerido: {exc.args[0]}"), 400
        except (OrderError, ValueError) as exc:
            return jsonify(error=str(exc)), 422
        return jsonify(serialize(order)), 201

    @app.get("/orders/<order_id>")
    def get_order(order_id: str):
        try:
            return jsonify(serialize(svc.get_order(order_id)))
        except OrderError as exc:
            return jsonify(error=str(exc)), 404

    @app.patch("/orders/<order_id>/status")
    def change_status(order_id: str):
        data = request.get_json(silent=True) or {}
        try:
            status = OrderStatus[data.get("status", "")]
        except KeyError:
            return jsonify(error="Estado inválido"), 400
        try:
            return jsonify(serialize(svc.change_status(order_id, status)))
        except OrderError as exc:
            code = 404 if "no encontrado" in str(exc) else 409
            return jsonify(error=str(exc)), code

    return app
