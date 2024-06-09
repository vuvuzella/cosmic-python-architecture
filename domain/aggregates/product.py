from abc import ABC
from dataclasses import dataclass
from functools import reduce
from typing import List

from sqlalchemy_serializer import SerializerMixin

from domain.aggregates.base import AbstractAggregate
from domain.events import OutOfStockEvent
from domain.models import (
    Batch,
    DeallocateStocksException,
    InsufficientStocksException,
    Orderline,
)

# class OutOfStock(Exception):
#     ...


@dataclass
class Product(AbstractAggregate):
    """
    A product aggregate collates all the batches of a specific product SKU
    """

    sku: str
    batches: List[Batch]
    version: int
    # events: List[str] = []

    def __init__(self, sku: str, batches: List[Batch]) -> None:
        self.sku = sku
        self.batches = batches
        self.events = []

    @property
    def available_quantity(self) -> int:
        return reduce(
            lambda a, b: a + b, [batch.available_quantity for batch in self.batches]
        )

    def allocate(self, line: Orderline) -> str | None:
        try:
            batch = next(b for b in self.batches if b.can_allocate(line))
            batch.allocate(line)
            self.version += 1
            return batch.reference
        except StopIteration:
            # raise OutOfStock(f"Out of stock for sku {line.sku}")
            self.events.append(OutOfStockEvent(sku=self.sku))
            return None

    def deallocate(self, line: Orderline):
        sorted_deallocatable_batch = [
            batch_item
            for batch_item in sorted(self.batches)
            if batch_item._can_deallocate(line)
        ]

        try:
            deallocated_batch = next(iter(sorted_deallocatable_batch))
            deallocated_batch.deallocate(line)
            self.version += 1
            return deallocated_batch.reference
        except StopIteration:
            # Not a business event, so raise an exception instead
            raise DeallocateStocksException(
                f"No batches available to deallocate orderline {line.orderid}"
            )
