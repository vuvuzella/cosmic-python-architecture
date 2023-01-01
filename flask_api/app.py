from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import global_settings

from ..infrastructure.orm import start_mappers, create_tables
from ..models import Batch, OrderLine, InsufficientStocksException
from ..services.services import allocate, is_valid_sku, InvalidSkuError
from ..infrastructure.repository import SqlAlchemyRepository

engine = create_engine(global_settings.DB_DSN)

# setup the database with tables
create_tables(engine)

# map the models to database tables and relationships
start_mappers()
get_session = sessionmaker(bind=engine)
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()

    order_id = request.json["orderid"]  # type: ignore
    sku = request.json["sku"]  # type: ignore
    qty = request.json["qty"]  # type: ignore

    line = OrderLine(order_id, sku, qty)

    try:
        batchref = allocate(line, SqlAlchemyRepository(session), session)
    except (InsufficientStocksException, InvalidSkuError) as e:
        return {"message": str(e)}, 400

    session.commit()
    return {"batchref": batchref}, 201


# TODO: implement deallocate endpoint


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
