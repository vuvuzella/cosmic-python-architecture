from datetime import date
from typing import List, Optional

from domain.aggregates import Product
from domain.models import (
    Batch,
    Orderline,
)
from domain.models import (
    allocate as model_allocate,
)
from domain.models import (
    deallocate as model_deallocate,
)
from services import AbstractUnitOfWork, BatchUnitOfWork, ProductUnitOfWork

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
    uow: AbstractUnitOfWork,
) -> Batch:
    """
    Creates an orderline given an order_id, sku and quantity, and assigns
    """
    line = Orderline(order_id, sku, quantity)

    with uow:
        batch = uow.repository.list()

        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")

        allocation = model_allocate(order_line=line, batches=batch)
        uow.commit()  # commit refers to the abstract uow commit, not from a db connector

        return allocation


def deallocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    line = Orderline(orderid=orderid, sku=sku, qty=qty)
    with uow:
        batch = uow.repository.list()
        if not is_valid_sku(line.sku, batch):
            raise InvalidSkuError(f"Invalid sku: {line.sku}")
        deallocated_batch = model_deallocate(order_line=line, batches=batch)
        uow.commit()
        return deallocated_batch


def restock(reference: str, sku: str, qty: int, eta: date | None, uow: BatchUnitOfWork):
    batch = Batch(reference=reference, sku=sku, qty=qty, eta=eta)
    with uow:
        uow.repository.add(batch=batch)
        uow.commit()
        return batch


def change_batch_quantity(
    batch_ref: str, sku: str, new_quantity: int, uow: ProductUnitOfWork
):
    with uow:
        product = uow.get(sku=sku)
        batch = [batch for batch in product.batches if batch.reference == batch_ref]

        if len(batch) > 1:
            raise DuplicateBatchError(
                f"Duplicate Batch Error with reference: {batch_ref}"
            )

        batch = batch[0]

        batch._purchased_quantity = new_quantity

        # pop any lines until available quantity is positive
        deallocated_lines = []
        while batch.available_quantity < 0:
            deallocated_lines.append(batch.deallocate_one())

        uow.commit()

    return deallocated_lines


class DuplicateBatchError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidSkuError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def is_valid_sku(sku, batches: List[Batch]):
    return sku in {batch.sku for batch in batches}
