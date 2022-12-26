from models import (
    Batch,
    DeallocateStocksException,
    InsufficientStocksException,
    OrderLine,
)
from services import allocate

from datetime import date, timedelta
from typing import Iterator, Tuple, Optional

import pytest


def create_test_components(
    sku: str, batch_qty: int, line_qty: int, eta: Optional[date] = date.today()
) -> Tuple[Batch, OrderLine]:
    return (
        Batch("batch-001", sku, qty=batch_qty, eta=eta),
        OrderLine("order-ref", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_available_quantity():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 2)
    batch.allocate(line=line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = create_test_components("ELEGANT-LAMP", 20, 2)
    assert batch.can_allocate(line=line) is True


def test_cannot_allocate_if_available_less_than_required():
    batch, line = create_test_components("ELEGANT-LAMP", 2, 20)
    assert batch.can_allocate(line=line) is False


def test_can_allocate_if_available_equalt_to_required():
    batch, line = create_test_components("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line=line) is True


def test_cannot_allocate_if_skus_do_not_match():
    another_batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 20)
    _, line = create_test_components("SIMPLE-CHAIR", 20, 2)
    assert another_batch.can_allocate(line=line) is False


def test_can_only_deallocate_allocated_lines():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 10)
    with pytest.raises(DeallocateStocksException):
        batch.deallocate(line)


def test_can_deallocate_allocated_lines():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 10)
    batch.allocate(line=line)
    assert batch.available_quantity == 10
    batch.deallocate(line=line)
    assert batch.available_quantity == 20


def test_can_allocate_same_lines_multiple_times_without_double_accounting():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 5)
    batch.allocate(line)
    assert batch.available_quantity == 15
    batch.allocate(line)
    assert batch.available_quantity == 15

    new_line_order = OrderLine("order-002", "SIMPLE-CHAIR", 5)
    batch.allocate(new_line_order)
    assert batch.available_quantity == 10


def test_same_valued_order_lines_are_equal():
    line1 = OrderLine("order-ref-1", "SMALL-CHAIR", 10)
    line2 = OrderLine("order-ref-1", "SMALL-CHAIR", 10)
    assert (line1 == line2) == True


def test_different_valued_order_lines_are_not_equal():
    order_ref_one = "order-ref-1"
    order_ref_two = "order-ref-2"
    qty_ten = 10
    qty_five = 5

    small_chair_ol = OrderLine(order_ref_one, "SMALL-CHAIR", qty_ten)
    large_chair_ol = OrderLine(order_ref_one, "LARGE-CHAIR", qty_ten)
    assert (small_chair_ol == large_chair_ol) == False
    new_small_chair_ol = OrderLine(order_ref_two, "SMALL-CHAIR", qty_ten)
    assert (small_chair_ol == new_small_chair_ol) == False
    different_quantity_ol = OrderLine(order_ref_one, "SMALL-CHAIR", qty_five)
    assert (small_chair_ol == different_quantity_ol) == False


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100)
    shipping_batch = Batch(
        "shipping-batch",
        "RETRO-CLOCK",
        100,
        eta=(date.today() + timedelta(days=1)),
    )
    order_line = OrderLine("order-ref", "RETRO-CLOCK", 10)
    batch = allocate(order_line, [in_stock_batch, shipping_batch])
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
    allocate(
        OrderLine("order-ref", "RETRO-CLOCK", 10), [in_stock_batch, shipping_batch]
    )
    allocate(
        OrderLine("another-order-ref", "RETRO-CLOCK", 10),
        [in_stock_batch, shipping_batch],
    )
    order_line = OrderLine("order-ref", "RETRO-CLOCK", 1)

    with pytest.raises(InsufficientStocksException):
        batch = allocate(order_line, [in_stock_batch, shipping_batch])


# TODO: add tests for in_shipping only stock batches
# TODO: add tests that can distribute a single order line to multiple batches according to availability
