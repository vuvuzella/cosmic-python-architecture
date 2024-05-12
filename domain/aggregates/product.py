from abc import ABC
from typing import List

from domain.aggregates.base import AbstractAggregate
from domain.events import OutOfStockEvent
from domain.models import Batch, InsufficientStocksException, Orderline


class OutOfStock(Exception):
    ...


class Product(AbstractAggregate):
    """
    A product aggregate collates all the batches of a specific product SKU
    """

    def __init__(self, sku: str, batches: List[Batch]) -> None:
        self.sku = sku
        self.batches = batches
        self.events = []

    def allocate(self, line: Orderline) -> str | None:
        try:
            batch = next(b for b in self.batches if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            # raise OutOfStock(f"Out of stock for sku {line.sku}")
            self.events.append(OutOfStockEvent(sku=self.sku))
            return None
