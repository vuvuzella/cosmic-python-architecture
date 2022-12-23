from batch import Batch, DeallocateStocksException
from order_line import OrderLine
from datetime import date
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
