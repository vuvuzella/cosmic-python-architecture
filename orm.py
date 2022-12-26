from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, event

# the ORM imports the domain model, not the other way around
from models import OrderLine, Batch

import logging

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
)

batch = Table(
    "batch",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", Integer),
    Column("name", String(255)),
    Column("_purchased_quantity", Integer),
    Column("eta", Date),
    # Column(
    #     "_allocations",
    # ),  # TODO: This is a relationship.
)


def start_mappers():
    lines_mapper = mapper(OrderLine, order_lines)
    batch_mapper = mapper(Batch, batch)
