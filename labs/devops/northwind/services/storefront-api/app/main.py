from fastapi import FastAPI

app = FastAPI(title="Northwind Storefront API", version="0.1.0")


@app.get("/livez")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/products")
def products() -> list[dict[str, object]]:
    return [
        {"id": "prod-coffee-001", "name": "Northwind Coffee", "price_cents": 1299},
        {"id": "prod-tea-001", "name": "Northwind Tea", "price_cents": 899},
    ]

