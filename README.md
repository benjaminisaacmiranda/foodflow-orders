# FoodFlow · Servicio de Pedidos

Componente mínimo del Proyecto Final de **Arquitectura de Software** (docente: Álvaro Colmenares).
Implementa el Servicio de Pedidos de FoodFlow, con los patrones Strategy, State, Observer y Repository,
pruebas automatizadas y un pipeline de integración continua en GitHub Actions.

El Documento de Arquitectura de Software está en `docs/DAS_FoodFlow_Benjamin_Miranda.pdf`;
los diagramas UML, en `docs/diagramas/`.

## Ejecutar localmente

```bash
python -m venv .venv && source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
flake8 src tests                 # análisis estático
pytest                           # 29 pruebas + cobertura (umbral 85 %)
python -m build                  # paquete wheel / sdist (pip install build)
```

Levantar la API (desarrollo):

```bash
PYTHONPATH=src flask --app "orders.api:create_app" run
curl -X POST localhost:5000/orders -H "Content-Type: application/json" \
  -d '{"customer_id":"c1","restaurant_id":"r1","items":[{"product_id":"p1","name":"Pizza","unit_price":9990,"quantity":2}]}'
```

## Pipeline CI (`.github/workflows/ci.yml`)

`lint` (flake8) → `test` (pytest + cobertura, Python 3.11 y 3.12) → `build` (wheel + imagen Docker).

## Cómo obtener las evidencias en GitHub

1. Crear un repositorio vacío en GitHub y ejecutar:
   `git remote add origin <URL>` y `git push -u origin main` (renombrar la rama con `git branch -M main` si hace falta).
2. Abrir la pestaña **Actions** y capturar la ejecución con las tres etapas en verde.
3. (Opcional) Crear una rama, romper una prueba, abrir un pull request y capturar el pipeline en rojo.

La carpeta `evidence/` contiene los registros de la ejecución local (pruebas, cobertura, complejidad y micro-benchmark).
