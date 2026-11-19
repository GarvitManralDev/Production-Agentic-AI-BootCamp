"""
Section 1.2 - CRUD with FastAPI

Create / Read / Update / Delete products stored in an in-memory "database".

    POST   /products              -> Create   (201)
    GET    /products              -> Read all
    GET    /products/{id}         -> Read one (404 if missing)
    PUT    /products/{id}         -> Replace  (all fields required)
    PATCH  /products/{id}         -> Update   (only the fields you send)
    DELETE /products/{id}         -> Delete   (204)

Run:   python 01_intro_crud/crud.py
Docs:  http://127.0.0.1:8080/docs
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="CRUD Demo API")


# =========================
# MODELS
# =========================

class ProductIn(BaseModel):
    """What the client sends when creating / replacing a product."""

    name: str = Field(min_length=1, examples=["Keyboard"])
    price: float = Field(gt=0, examples=[2500])


class ProductUpdate(BaseModel):
    """PATCH body - every field is optional."""

    name: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, gt=0)


class Product(ProductIn):
    """What the API returns (includes the server-generated id)."""

    id: int


# =========================
# FAKE DATABASE
# =========================

products: dict[int, Product] = {
    1: Product(id=1, name="Laptop", price=50000),
    2: Product(id=2, name="Mouse", price=1000),
}


def get_or_404(product_id: int) -> Product:
    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return products[product_id]


# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "Welcome to the CRUD API! Open /docs to try it."}


@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductIn):
    # Server decides the id - clients should not pick primary keys
    new_id = max(products, default=0) + 1
    products[new_id] = Product(id=new_id, **product.model_dump())
    return products[new_id]


@app.get("/products", response_model=list[Product])
def list_products():
    return list(products.values())


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    return get_or_404(product_id)


@app.put("/products/{product_id}", response_model=Product)
def replace_product(product_id: int, product: ProductIn):
    get_or_404(product_id)
    products[product_id] = Product(id=product_id, **product.model_dump())
    return products[product_id]


@app.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: int, changes: ProductUpdate):
    current = get_or_404(product_id)

    # exclude_unset=True -> only the fields the client actually sent
    updated = current.model_copy(update=changes.model_dump(exclude_unset=True))
    products[product_id] = updated
    return updated


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    get_or_404(product_id)
    del products[product_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
