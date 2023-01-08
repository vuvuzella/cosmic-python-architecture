import pytest
from sqlalchemy.orm import Session
from datetime import date, timedelta

from models import OrderLine, Batch, InsufficientStocksException
from infrastructure.repository import FakeRepository
from services.services import allocate, deallocate, InvalidSkuError


# tests about orchestration stuff


class FakeSession(Session):
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocations():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "MY-CHAIR", 100)

    repo = FakeRepository([batch])
    result = allocate(line, repo, FakeSession())
    if result:
        assert result.reference == "batch-ref-1"
    else:
        raise KeyError


def test_error_for_invalid_sku():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "NOT-MY-CHAIR", 100)
    repo = FakeRepository([batch])

    with pytest.raises(InvalidSkuError, match="Invalid sku: MY-CHAIR"):
        allocate(line, repo, FakeSession())


def test_commits():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "MY-CHAIR", 100)
    repo = FakeRepository([batch])
    session = FakeSession()
    result = allocate(line, repo, session)

    assert session.committed == True


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100)
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        100,
        eta=(date.today() + timedelta(days=1)),
    )
    repo = FakeRepository([in_stock_batch, shipping_batch])
    sess = FakeSession()
    order_line = OrderLine("order-ref", "RETRO-CLOCK", 10)
    batch = allocate(order_line, repo, sess)
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

    repo = FakeRepository([in_stock_batch, shipping_batch])
    sess = FakeSession()

    first_order_clock = OrderLine("order-ref", "RETRO-CLOCK", 10)

    allocate(first_order_clock, repo, sess)

    second_order_clock = OrderLine("another-order-ref", "RETRO-CLOCK", 10)

    allocate(second_order_clock, repo, sess)

    order_line = OrderLine("order-ref", "RETRO-CLOCK", 1)

    with pytest.raises(InsufficientStocksException):
        batch = allocate(order_line, repo, sess)


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

    repo = FakeRepository([in_stock_batch, shipping_batch])
    sess = FakeSession()

    assert shipping_batch.contains(first_order_clock) == True

    deallocate(first_order_clock, repo, sess)

    assert shipping_batch.contains(first_order_clock) == False


# TODO: add tests for in_shipping only stock batches
# TODO: add tests that can distribute a single order line to multiple batches according to availability
