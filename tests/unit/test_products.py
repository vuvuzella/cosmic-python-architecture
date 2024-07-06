import datetime

import pytest

from domain.aggregates import Product
from domain.events import OutOfStockEvent
from domain.models import Batch, DeallocateStocksException, Orderline


@pytest.mark.skip
def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=datetime.date.today())
    product = Product(sku="SMALL-FORK", batches=[batch])

    first_allocate_result = product.allocate(Orderline("order1", "SMALL-FORK", 10))

    second_allocate_result = product.allocate(Orderline("order2", "SMALL-FORK", 1))

    assert len(product.events) > 0
    assert isinstance(product.events[-1], OutOfStockEvent) == True  # noqa: E712
    assert first_allocate_result is not None
    assert second_allocate_result is None


def test_product_available_quantity():
    batch_1 = Batch("batch_id_1", "SMALL-FORK", 15, eta=datetime.date.today())
    batch_2 = Batch("batch_id_2", "SMALL-FORK", 50, eta=datetime.date.today())
    product = Product(sku="SMALL-FORK", batches=[batch_1, batch_2])
    available_quantity = product.available_quantity
    assert available_quantity == 65


def test_deallocation_successful():
    orderline = Orderline("order_id_1", "SMALL-FORK", 10)

    batch_1 = Batch("batch_id_1", "SMALL-FORK", 15, eta=datetime.date.today())
    batch_2 = Batch("batch_id_2", "SMALL-FORK", 50, eta=datetime.date.today())
    product = Product(sku="SMALL-FORK", batches=[batch_1, batch_2])

    alloc_ref = product.allocate(orderline)

    assert alloc_ref == batch_1.reference
    available_quantity = product.available_quantity
    assert available_quantity == 55

    dealloc_ref = product.deallocate(orderline)

    assert dealloc_ref == batch_1.reference
    assert alloc_ref == dealloc_ref
    available_quantity = product.available_quantity
    assert product.available_quantity == 65


def test_raise_deallocation_exception_if_orderline_not_allocated():
    orderline = Orderline("order_id_1", "LENOVO_LEGION", 10)

    batch_1 = Batch("batch_id_1", "SMALL-FORK", 10, eta=datetime.date.today())
    batch_2 = Batch("batch_id_1", "SMALL-FORK", 10, eta=datetime.date.today())
    product = Product(sku="SMALL-FORK", batches=[batch_1, batch_2])

    with pytest.raises(DeallocateStocksException):
        product.deallocate(orderline)
