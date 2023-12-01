import pytest
from typing import List
from sqlalchemy.orm import Session
from datetime import date, timedelta

from models import OrderLine, Batch, InsufficientStocksException
from infrastructure.repository import FakeRepository
from services.services import allocate, deallocate, InvalidSkuError
from services import FakeUnitOfWork

# tests about orchestration stuff


class FakeSession(Session):
    committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

def test_returns_allocations():

    batch = Batch("batch-ref-1", "MY-CHAIR", 100)

    line_order_id = "order1"
    line_sku = "MY-CHAIR"
    line_qty = 10

    fake_uow = FakeUnitOfWork([batch])
    result = allocate(order_id=line_order_id, quantity=line_qty, sku=line_sku, uow=fake_uow)
    if result:
        assert result == batch
    else:
        raise KeyError


def test_error_for_invalid_sku():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "NOT-MY-CHAIR", 100)
    uow = FakeUnitOfWork([batch])

    with pytest.raises(InvalidSkuError, match="Invalid sku: MY-CHAIR"):
        allocate(order_id=line.orderid, sku=line.sku, quantity=line.qty, uow=uow)

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100)
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        100,
        eta=(date.today() + timedelta(days=1)),
    )
    uow = FakeUnitOfWork([in_stock_batch, shipping_batch])
    order_line = OrderLine("order-ref", "RETRO-CLOCK", 10)
    batch = allocate(order_id=order_line.orderid, sku=order_line.sku, quantity=order_line.qty, uow=uow)
    assert in_stock_batch.available_quantity == 90
    assert batch == in_stock_batch


def test_allocation_fails_if_not_enough_stock():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 10)
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        10,
        eta=(date.today() + timedelta(days=1)),
    )

    uow = FakeUnitOfWork([in_stock_batch, shipping_batch])

    first_order_clock = OrderLine("order-ref", "RETRO-CLOCK", 10)

    allocate(order_id=first_order_clock.orderid, sku=first_order_clock.sku, quantity=first_order_clock.qty, uow=uow)

    second_order_clock = OrderLine("another-order-ref", "RETRO-CLOCK", 10)

    allocate(order_id=second_order_clock.orderid, sku=second_order_clock.sku, quantity=second_order_clock.qty, uow=uow)

    order_line = OrderLine("order-ref", "RETRO-CLOCK", 1)

    with pytest.raises(InsufficientStocksException):
        batch = allocate(order_id=order_line.orderid, sku=order_line.sku, quantity=order_line.qty, uow=uow)




def test_allocate_in_shipping_batches_only():
    delayed_shipping_batch = Batch("in-stock-batch", "RETRO-CLOCK", 10, eta=(date.today() + timedelta(days=2)))
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        10,
        eta=(date.today() + timedelta(days=1)),
    )
    uow = FakeUnitOfWork([delayed_shipping_batch, shipping_batch])
    first_order_clock = OrderLine("order-ref", "RETRO-CLOCK", 10)

    allocate(order_id=first_order_clock.orderid, sku=first_order_clock.sku, quantity=first_order_clock.qty, uow=uow)

    assert shipping_batch.contains(first_order_clock)

# TODO: add tests that can distribute a single order line to multiple batches according to availability
def test_allocate_order_next_available_batch():
    delayed_shipping_batch = Batch("in-stock-batch", "RETRO-CLOCK", 10, eta=(date.today() + timedelta(days=2)))
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        10,
        eta=(date.today() + timedelta(days=1)),
    )
    uow = FakeUnitOfWork([delayed_shipping_batch, shipping_batch])

    first_order_clock = OrderLine("order-1-ref", "RETRO-CLOCK", 10)
    second_order_clock = OrderLine("order-2-ref", "RETRO-CLOCK", 10)
    third_order_clock = OrderLine("order-2-ref", "RETRO-CLOCK", 10)

    allocate(order_id=first_order_clock.orderid, sku=first_order_clock.sku, quantity=first_order_clock.qty, uow=uow)
    allocate(order_id=second_order_clock.orderid, sku=second_order_clock.sku, quantity=second_order_clock.qty, uow=uow)

    assert shipping_batch.contains(first_order_clock)
    assert delayed_shipping_batch.contains(second_order_clock)

    with pytest.raises(InsufficientStocksException):
        allocate(order_id=third_order_clock.orderid, sku=third_order_clock.sku, quantity=third_order_clock.qty, uow=uow)



def test_deallocate_order_from_batches():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 10)
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        10,
        eta=(date.today() + timedelta(days=1)),
    )

    first_order_clock = OrderLine("order-ref", "RETRO-CLOCK", 10)
    shipping_batch._allocations.add(first_order_clock)

    uow = FakeUnitOfWork([in_stock_batch, shipping_batch])

    assert shipping_batch.contains(first_order_clock) == True

    deallocate(orderid=first_order_clock.orderid, sku=first_order_clock.sku, qty=first_order_clock.qty, uow=uow)

    assert shipping_batch.contains(first_order_clock) == False
