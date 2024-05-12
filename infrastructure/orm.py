import logging
from typing import Set

from sqlalchemy import Column, Date, ForeignKey, Integer, MetaData, String, Table, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import mapper, relationship

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
    Column("orderid", String(255)),
    # Column("parentid", Integer, ForeignKey("batch.id"), nullable=True),
)

batch = Table(
    "batch",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("name", String(255)),
    Column("_purchased_quantity", Integer),
    Column("eta", Date),
)

# This serves as the many-to-many mapping between orderline and batch
allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batch.id")),
)


def create_tables(engine: Engine):
    metadata.create_all(engine)


# TODO: Im still fuzzy in how the relationship works without its own model. How does it add orders in batches and preserve its mappings?
def start_mappers():
    lines_mapper = mapper(Orderline, order_lines)
    batch_mapper = mapper(
        Batch,
        batch,
        properties={
            "_allocations": relationship(
                argument=lines_mapper, secondary=allocations, collection_class=set
            )
        },
    )
