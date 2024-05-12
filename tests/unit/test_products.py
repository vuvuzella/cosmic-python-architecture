import datetime

from domain.aggregates import Product
from domain.events import OutOfStockEvent
from domain.models import Batch, Orderline


def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=datetime.date.today())
    product = Product(sku="SMALL-FORK", batches=[batch])

    first_allocate_result = product.allocate(Orderline("order1", "SMALL-FORK", 10))

    second_allocate_result = product.allocate(Orderline("order2", "SMALL-FORK", 1))

    assert product.events[-1] == OutOfStockEvent
    assert first_allocate_result is not None
    assert second_allocate_result is None
