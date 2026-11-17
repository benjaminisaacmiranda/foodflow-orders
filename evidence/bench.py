"""Micro-benchmark de la capa de dominio/aplicación (en proceso, sin red ni BD)."""
import os, sys, time, statistics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from orders.events import EventBus
from orders.pricing import PercentageDiscount
from orders.repository import InMemoryOrderRepository
from orders.service import OrderService

svc = OrderService(InMemoryOrderRepository(), EventBus(), discount=PercentageDiscount(10))
bus_hits = []
svc.bus.subscribe("order.created", lambda p: bus_hits.append(1))
items = [{"product_id": "p1", "name": "Pizza", "unit_price": 9990, "quantity": 2},
         {"product_id": "p2", "name": "Bebida", "unit_price": 1500, "quantity": 3}]
N = 20000
lat = []
t0 = time.perf_counter()
for i in range(N):
    s = time.perf_counter()
    svc.create_order(f"c{i % 500}", "r1", items)
    lat.append((time.perf_counter() - s) * 1000)
tot = time.perf_counter() - t0
lat.sort()
print(f"Pedidos creados: {N}")
print(f"Throughput: {N / tot:,.0f} pedidos/s")
print(f"Latencia media: {statistics.mean(lat):.4f} ms")
print(f"Latencia p95:   {lat[int(N * 0.95)]:.4f} ms")
print(f"Latencia p99:   {lat[int(N * 0.99)]:.4f} ms")
print(f"Eventos entregados: {len(bus_hits)}")
