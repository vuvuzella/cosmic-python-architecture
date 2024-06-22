import logging
from typing import Set

from sqlalchemy import Column, Date, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import clear_mappers, mapper, relationship

from domain.aggregates import Product

# the ORM imports the domain model, not the other way around
from domain.models import Batch, Orderline

logger = logging.getLogger(__name__)

metadata = MetaData()

# SQLAlchemy's table abstractions
order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255), unique=True),
    # Column("parentid", Integer, ForeignKey("batch.id"), nullable=True),
)

batch = Table(
    "batch",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255), unique=True),
    Column("sku", ForeignKey("product.sku")),
    Column("_purchased_quantity", Integer),
    Column("eta", Date),
)

# This serves as the many-to-many mapping between orderline and batch
allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.orderid")),
    Column("batch_id", ForeignKey("batch.reference")),
)

product = Table(
    "product",
    metadata,
    Column("sku", String(255), primary_key=True, autoincrement=False),
    Column("version", Integer, default=0),
)


def create_tables(engine: Engine):
    metadata.create_all(engine, checkfirst=True)


def start_mappers():
    lines_mapper = mapper(Orderline, order_lines)
    batch_mapper = mapper(
        Batch,
        batch,
        properties={
            "_allocations": relationship(
                argument=lines_mapper,
                secondary=allocations,
                collection_class=set,
                lazy="subquery",
            )
        },
    )
    products_mapper = mapper(
        Product,
        product,
        properties={
            "batches": relationship(
                argument=batch_mapper, collection_class=list, lazy="subquery"
            )
        },
    )
