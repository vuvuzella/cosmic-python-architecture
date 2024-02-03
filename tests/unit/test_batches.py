from models import (
    Batch,
    DeallocateStocksException,
    InsufficientStocksException,
    Orderline,
    allocate,
    deallocate,
)

from datetime import date, timedelta
from typing import Iterator, Tuple, Optional

import pytest


def create_test_components(
    sku: str, batch_qty: int, line_qty: int, eta: Optional[date] = date.today()
) -> Tuple[Batch, Orderline]:
    return (
        Batch("batch-001", sku, qty=batch_qty, eta=eta),
        Orderline("order-ref", sku, line_qty),
    )


@pytest.mark.skip
def test_allocating_to_a_batch_reduces_available_quantity():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 2)
    batch.allocate(line=line)
    assert batch.available_quantity == 18


@pytest.mark.skip
def test_can_allocate_if_available_greater_than_required():
    batch, line = create_test_components("ELEGANT-LAMP", 20, 2)
    assert batch.can_allocate(line=line) is True


@pytest.mark.skip
def test_cannot_allocate_if_available_less_than_required():
    batch, line = create_test_components("ELEGANT-LAMP", 2, 20)
    assert batch.can_allocate(line=line) is False


@pytest.mark.skip
def test_can_allocate_if_available_equalt_to_required():
    batch, line = create_test_components("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line=line) is True


@pytest.mark.skip
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


@pytest.mark.skip
def test_can_allocate_same_lines_multiple_times_without_double_accounting():
    batch, line = create_test_components("SIMPLE-CHAIR", 20, 5)
    batch.allocate(line)
    assert batch.available_quantity == 15
    batch.allocate(line)
    assert batch.available_quantity == 15

    new_line_order = Orderline("order-002", "SIMPLE-CHAIR", 5)
    batch.allocate(new_line_order)
    assert batch.available_quantity == 10


@pytest.mark.skip
def test_same_valued_order_lines_are_equal():
    line1 = Orderline("order-ref-1", "SMALL-CHAIR", 10)
    line2 = Orderline("order-ref-1", "SMALL-CHAIR", 10)
    assert (line1 == line2) == True


@pytest.mark.skip
def test_different_valued_order_lines_are_not_equal():
    order_ref_one = "order-ref-1"
    order_ref_two = "order-ref-2"
    qty_ten = 10
    qty_five = 5

    small_chair_ol = Orderline(order_ref_one, "SMALL-CHAIR", qty_ten)
    large_chair_ol = Orderline(order_ref_one, "LARGE-CHAIR", qty_ten)
    assert (small_chair_ol == large_chair_ol) == False
    new_small_chair_ol = Orderline(order_ref_two, "SMALL-CHAIR", qty_ten)
    assert (small_chair_ol == new_small_chair_ol) == False
    different_quantity_ol = Orderline(order_ref_one, "SMALL-CHAIR", qty_five)
    assert (small_chair_ol == different_quantity_ol) == False


def test_deallocate_allocated_order():
    batch = Batch("batch-ref-1", "TABLE", 100, None)
    order = Orderline("order-ref-1", "TABLE", 10)

    batch.allocate(order)

    assert batch.available_quantity == 90

    deallocated_batch = deallocate(batches=[batch], order_line=order)

    assert batch == deallocated_batch
    assert batch.available_quantity == deallocated_batch.available_quantity
    assert deallocated_batch.available_quantity == 100
