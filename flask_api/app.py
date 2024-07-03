import json
from dataclasses import asdict

from flask import Flask, request

from domain.models import InsufficientStocksException
from infrastructure.orm import start_mappers
from services.services import InvalidSkuError, allocate, deallocate, restock
from services.unit_of_work import BatchUnitOfWork, ProductUnitOfWork

# map the models to database tables and relationships

app = Flask(__name__)
start_mappers()


# @app.route("/batches", methods=["GET"])
# def get_batches_endpoint():
#     uow = BatchUnitOfWork()
#     with uow:
#         batches = uow.repository.list()
#         return {"batches": batches}, 200


@app.route("/products", methods=["GET"])
def get_products_endpoint():
    uow = ProductUnitOfWork()
    with uow:
        products = uow.repository.list()
        return {"products": [product.to_json() for product in products]}, 200


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    order_id = request.json["orderid"]  # type: ignore
    sku = request.json["sku"]  # type: ignore
    qty = request.json["qty"]  # type: ignore

    try:
        batchref = allocate(
            order_id=order_id, sku=sku, quantity=qty, uow=BatchUnitOfWork()
        )
    except (InsufficientStocksException, InvalidSkuError) as e:
        return {"message": str(e)}, 400

    return {"batchref": asdict(batchref)}, 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    order_id = request.json["orderid"]  # type: ignore
    sku = request.json["sku"]  # type: ignore
    qty = request.json["qty"]  # type: ignore

    try:
        batchref = deallocate(orderid=order_id, sku=sku, qty=qty, uow=BatchUnitOfWork())
    except InvalidSkuError as e:
        return {"message": str(e)}, 400

    return {"batchref": asdict(batchref)}, 201


@app.route("/restock", methods=["POST"])
def restock_endpoint():
    body = json.loads(request.get_data(as_text=True))

    reference = body.get("reference")
    name = body.get("name")
    qty = body.get("qty")
    eta = body.get("eta")

    try:
        batch = restock(
            reference=reference, sku=name, qty=qty, eta=eta, uow=BatchUnitOfWork()
        )

        return {"batchref": batch.to_dict()}, 200

    except Exception as e:
        return {"message": str(e)}, 400
