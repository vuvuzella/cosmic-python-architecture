import json
from dataclasses import asdict
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import global_settings

from infrastructure.orm import start_mappers, create_tables
from infrastructure.repository import SqlAlchemyRepository

from services.services import allocate, deallocate, restock, InvalidSkuError
from services.unit_of_work import SqlAlchemyUnitOfWork

from models import Batch, Orderline, InsufficientStocksException

engine = create_engine(global_settings.DB_DSN)

# setup the database with tables
create_tables(engine)

# map the models to database tables and relationships
start_mappers()
get_session = sessionmaker(bind=engine)
app = Flask(__name__)


@app.route("/batches", methods=["GET"])
def get_batches_endpoint():
    session = get_session()
    repo = SqlAlchemyRepository(session)

    batches = [batch for batch in repo.list()]

    return {"batches": batches}, 200


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    order_id = request.json["orderid"]  # type: ignore
    sku = request.json["sku"]  # type: ignore
    qty = request.json["qty"]  # type: ignore

    uow = SqlAlchemyUnitOfWork()

    try:
        batchref = allocate(order_id=order_id, sku=sku, quantity=qty, uow=uow)
    except (InsufficientStocksException, InvalidSkuError) as e:
        return {"message": str(e)}, 400

    return {"batchref": asdict(batchref)}, 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    order_id = request.json["orderid"]  # type: ignore
    sku = request.json["sku"]  # type: ignore
    qty = request.json["qty"]  # type: ignore

    uow = SqlAlchemyUnitOfWork()

    try:
        batchref = deallocate(orderid=order_id, sku=sku, qty=qty, uow=uow)
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

    uow = SqlAlchemyUnitOfWork()

    try:
        batch = restock(reference=reference, name=name, qty=qty, eta=eta, uow=uow)

        return {"batchref": batch.to_dict()}, 200

    except Exception as e:
        return {"message": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
