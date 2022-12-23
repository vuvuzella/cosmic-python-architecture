from order_line import OrderLine
from datetime import date
from typing import Optional

import inspect


def _get_function_name():
    # from https://stackoverflow.com/questions/900392/getting-the-caller-function-name-inside-another-function-in-python
    return inspect.stack()[1].function  # type: ignore


class Batch:
    def __init__(
        self, id: str, name: str, qty: int, eta: Optional[date] = date.today()
    ):
        self.id = id
        self.name = name
        self.available_quantity = qty
        self.eta = eta
        self.allocations = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self.available_quantity -= line.qty
            self.allocations.add(line)
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

    def _can_deallocate(self, line: OrderLine) -> bool:
        return not self.allocations.isdisjoint({line})

    def deallocate(self, line) -> None:
        if self._can_deallocate(line):
            self.allocations.remove(line)
            self.available_quantity += line.qty
        else:
            raise DeallocateStocksException("Stock not allocated")


class InsufficientStocksException(Exception):
    ...


class DeallocateStocksException(Exception):
    ...
