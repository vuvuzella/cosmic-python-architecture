from models.order_line import OrderLine
from datetime import date
from typing import Optional, List

import inspect


def _get_function_name():
    # from https://stackoverflow.com/questions/900392/getting-the-caller-function-name-inside-another-function-in-python
    return inspect.stack()[1].function  # type: ignore


class Batch:
    def __init__(self, reference: str, name: str, qty: int, eta: Optional[date] = None):
        self.reference = reference
        self.name = name
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations: List[
            OrderLine
        ] = (
            []
        )  # TODO: create a pydantic validator to maintain uniqueness of the contents

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

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            if not self._order_exists(line):
                self._allocations.append(line)
        else:
            raise InsufficientStocksException(
                f"Unable to allocate {line.qty} of {self.name}, only {self.available_quantity} remaining "
            )

    # business validation
    def can_allocate(self, line: OrderLine) -> bool:
        return (
            self.available_quantity - line.qty >= 0
            and line.sku.lower() == self.name.lower()
        )

    def _order_exists(self, line: OrderLine) -> bool:
        for order_line in self._allocations:
            if order_line == line:
                return True
        return False

    def _can_deallocate(self, line: OrderLine) -> bool:
        for order_line in self._allocations:
            if order_line == line:
                return True
        return False

    def deallocate(self, line) -> None:
        if self._can_deallocate(line):
            self._allocations.remove(line)
        else:
            raise DeallocateStocksException("Stock not allocated")


class InsufficientStocksException(Exception):
    ...


class DeallocateStocksException(Exception):
    ...
