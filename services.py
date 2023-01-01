from typing import List
from sqlalchemy.orm import Session

from .models import OrderLine, Batch, InsufficientStocksException
from .repository import AbstractRepository

# Seems like this module sits between the Application (API) Layer and the Domain Layer
# This is used by the application (API) layer to perform domain verbs/actions


def allocate(
    line: OrderLine, repo: AbstractRepository, session: Session
) -> Batch | None:
    batch = repo.list()
    sorted_allocatable_batch = [
        batch_item for batch_item in sorted(batch) if batch_item.can_allocate(line=line)
    ]

    if not is_valid_sku(line.sku, sorted_allocatable_batch):
        raise InvalidSkuError(f"Invalid sku: {line.sku}")

    try:
        allocatable_batch = next(iter(sorted_allocatable_batch))
        allocatable_batch.allocate(line)
        session.commit()
        return allocatable_batch
    except StopIteration:
        raise InsufficientStocksException(f"Insufficient in stock for {line.sku}")


class InvalidSkuError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def is_valid_sku(sku, batches: List[Batch]):
    return sku in {batch.name for batch in batches}
