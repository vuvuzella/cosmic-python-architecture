from typing import List
from abc import ABC

from models import Batch, Orderline, InsufficientStocksException


class AbstractAggregate(ABC):
    ...


class OutOfStock(Exception):
    ...


class Product:
    """
    A product aggregate collates all the batches of a specific product SKU
    """

    def __init__(self, sku: str, batches: List[Batch]) -> None:
        self.sku = sku
        self.batches = batches

    def allocate(self, line: Orderline) -> str:
        try:
            batch = next(b for b in self.batches if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {line.sku}")
