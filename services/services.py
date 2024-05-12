from typing import List, Optional
from datetime import date

from domain.models import (
    Orderline,
    Batch,
    allocate as model_allocate,
    deallocate as model_deallocate,
)
from domain.aggregates import Product
from services import AbstractUnitOfWork, ProductUnitOfWork, BatchUnitOfWork

# Seems like this module sits between the Application (API) Layer and the Domain Layer
# This is used by the application (API) layer to perform domain verbs/actions


def add_batch(
    reference: str,
    sku: str,
    quantity: int,
    eta: date | None,
    uow: ProductUnitOfWork,
):
    """
    Adds in a new batch to a Product
    """
    with uow:
        product = uow.repository.get(reference)
        if product is None:
            # Product does not exist, create new product with zero batches
            product = Product(sku=sku, batches=[])
            # persist new product to database
            uow.repository.add(product)

        product.batches.append(Batch(reference, sku, quantity, eta))
        uow.commit()


def allocate(
    # line: OrderLine, repo: AbstractRepository, session: Session
    order_id: str,
    sku: str,
    quantity: int,
    uow: BatchUnitOfWork,
) -> Batch:
    line = Orderline(order_id, sku, quantity)

    with uow:
        batch = uow.repository.list()

        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")

        allocation = model_allocate(line, batch)
        uow.commit()  # commit refers to the abstract uow commit, not from a db connector

        return allocation


def deallocate(orderid: str, sku: str, qty: int, uow: BatchUnitOfWork):
    line = Orderline(orderid=orderid, sku=sku, qty=qty)
    with uow:
        batch = uow.repository.list()
        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")
        deallocated_batch = model_deallocate(order_line=line, batches=batch)
        uow.commit()
        return deallocated_batch


def restock(
    reference: str, name: str, qty: int, eta: date | None, uow: BatchUnitOfWork
):
    batch = Batch(reference=reference, name=name, qty=qty, eta=eta)
    with uow:
        uow.repository.add(batch=batch)
        uow.commit()
        return batch


class InvalidSkuError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def is_valid_sku(sku, batches: List[Batch]):
    return sku in {batch.name for batch in batches}
