from typing import List
from datetime import date

from models import (
    OrderLine,
    Batch,
    allocate as model_allocate,
    deallocate as model_deallocate,
)
from services import AbstractUnitOfWork

# Seems like this module sits between the Application (API) Layer and the Domain Layer
# This is used by the application (API) layer to perform domain verbs/actions


def allocate(
    # line: OrderLine, repo: AbstractRepository, session: Session
    order_id: str,
    sku: str,
    quantity: int,
    uow: AbstractUnitOfWork,
) -> Batch:
    line = OrderLine(order_id, sku, quantity)

    with uow:
        batch = uow.batches.list()

        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")

        allocation = model_allocate(line, batch)
        uow.commit()  # commit refers to the abstract uow commit, not from a db connector

        return allocation


def deallocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    with uow:
        batch = uow.batches.list()
        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")
        deallocated_batch = model_deallocate(order_line=line, batches=batch)
        uow.commit()
        return deallocated_batch


def restock(
    reference: str, name: str, qty: int, eta: date | None, uow: AbstractUnitOfWork
):
    batch = Batch(reference=reference, name=name, qty=qty, eta=eta)
    with uow:
        uow.batches.add(batch=batch)
        uow.commit()
        return batch


class InvalidSkuError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def is_valid_sku(sku, batches: List[Batch]):
    return sku in {batch.name for batch in batches}
