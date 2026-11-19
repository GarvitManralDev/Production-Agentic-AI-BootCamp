# 1. Intro to FastAPI + CRUD

FastAPI is a modern, high-performance Python web framework for building APIs. It uses standard **type hints** to:

- validate incoming data,
- convert it to the right Python types,
- generate interactive docs at `/docs` (Swagger UI) and `/redoc`.

`crud.py` is a full Create / Read / Update / Delete API over an in-memory dict.

## Run

From the `Module 4 - Fast API` folder:

```bash
python 01_intro_crud/crud.py
```

Then open <http://127.0.0.1:8080/docs>.

## Try it

```bash
# Read
curl http://127.0.0.1:8080/products
curl http://127.0.0.1:8080/products/1

# Create  -> 201
curl -X POST http://127.0.0.1:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Keyboard", "price": 2500}'

# Replace (all fields)
curl -X PUT http://127.0.0.1:8080/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Gaming Laptop", "price": 90000}'

# Partial update (only price)
curl -X PATCH http://127.0.0.1:8080/products/2 \
  -H "Content-Type: application/json" \
  -d '{"price": 799}'

# Delete -> 204
curl -X DELETE -i http://127.0.0.1:8080/products/2

# Not found -> 404
curl -i http://127.0.0.1:8080/products/999

# Invalid body -> 422 (price must be > 0)
curl -i -X POST http://127.0.0.1:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Free thing", "price": 0}'
```

## HTTP verbs ↔ CRUD

| CRUD | Verb | Success code |
| --- | --- | --- |
| Create | `POST` | `201 Created` |
| Read | `GET` | `200 OK` |
| Update (replace) | `PUT` | `200 OK` |
| Update (partial) | `PATCH` | `200 OK` |
| Delete | `DELETE` | `204 No Content` |

Common errors: `404 Not Found` (no such resource) and `422 Unprocessable Entity` (body failed validation).

## Takeaway

> The server owns the ids, and type hints do the validation. A route is just a Python function with a decorator.
