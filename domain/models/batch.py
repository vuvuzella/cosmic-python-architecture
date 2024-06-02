import json
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, List, Optional, Set

from sqlalchemy_serializer import SerializerMixin

from domain.models.base import Entity
from domain.models.order_line import Orderline


@dataclass
class Batch(Entity):
    reference: str
    name: str
    _purchased_quantity: int
    eta: date | None
    # TODO: make type hints work without causing circular dependencies
    # in the application
    _allocations: Set["Orderline"]

    def __init__(self, reference: str, name: str, qty: int, eta: Optional[date] = None):
        self.reference = reference
        self.name = name
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations = set()

    @property
    def available_quantity(self):
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        sum_allocations = 0
        for line in self._allocations:
            sum_allocations += line.qty
        return sum_allocations

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Batch):
            return False
        return __o.reference == self.reference

    def __gt__(self, __o: object) -> bool:
        if self.eta is None:
            return False
        if __o is None:
            return True
        if not isinstance(__o, Batch):
            raise ValueError("{__o} not of type Batch")
        return self.eta > __o.eta  # type: ignore

    def __hash__(self) -> int:
        return hash(self.reference)

    # Domain model level allocate function
    def allocate(self, line: "Orderline") -> None:
        if self.can_allocate(line):
            # if not self._order_exists(line):
            self._allocations.add(
                line
            )  # I think this uses the __eq__ definition of the OrderLine
        else:
            raise InsufficientStocksException(
                f"Unable to allocate {line.qty} of {self.name}, only {self.available_quantity} remaining "
            )

    # business validation
    def can_allocate(self, line: "Orderline") -> bool:
        return (
            self.available_quantity - line.qty >= 0
            and line.sku.lower() == self.name.lower()
        )

    def _can_deallocate(self, line: "Orderline") -> bool:
        for order_line in self._allocations:
            if order_line == line:
                return True
        return False

    def deallocate(self, line) -> None:
        if self._can_deallocate(line):
            self._allocations.remove(line)
        else:
            raise DeallocateStocksException("Stock not allocated")

    def contains(self, line: "Orderline") -> bool:
        return set([line]).issubset(self._allocations)


# TODO: For deprecation. This is superceded by the aggregate method
def allocate(order_line: "Orderline", batches: List[Batch]):
    sorted_allocatable_batch = [
        batch_item
        for batch_item in sorted(batches)  # also uses hash to sort by reference?
        if batch_item.can_allocate(line=order_line)
    ]

    try:
        # allocates to the next
        allocatable_batch = next(iter(sorted_allocatable_batch))
        allocatable_batch.allocate(order_line)
        return allocatable_batch
    except StopIteration:
        raise InsufficientStocksException(f"Insufficient in stock for {order_line.sku}")


# TODO: For deprecation. This is superceded by the aggregate method
def deallocate(order_line: "Orderline", batches: List[Batch]):
    sorted_deallocatable_batch = [
        batch_item for batch_item in batches if batch_item._can_deallocate(order_line)
    ]

    try:
        deallocated_batch = next(iter(sorted_deallocatable_batch))
        deallocated_batch.deallocate(order_line)
        return deallocated_batch
    except StopIteration:
        # the list is exhausted, no batches can deallocate
        raise DeallocateStocksException(
            f"No batches available to allovate orderline {order_line.orderid}"
        )


class InsufficientStocksException(Exception):
    ...


class DeallocateStocksException(Exception):
    ...
