from order_line import OrderLine
from datetime import date
from typing import Optional


class Batch:
    def __init__(
        self, id: str, name: str, qty: int, eta: Optional[date] = date.today()
    ):
        self.id = id
        self.name = name
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self.available_quantity -= line.qty
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

    def deallocate(self, line) -> None:
        ...


class InsufficientStocksException(Exception):
    ...


class DeallocateStocksException(Exception):
    ...
