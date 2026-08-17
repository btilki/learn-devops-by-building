import sys
from pathlib import Path

from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_liveness_reports_process_health() -> None:
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_catalog_contract() -> None:
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert products
    assert set(products[0]) == {"id", "name", "price_cents"}
    assert all(product["price_cents"] > 0 for product in products)


def test_unknown_route_is_not_successful() -> None:
    assert client.get("/does-not-exist").status_code == 404

