from typing import List
from sqlalchemy.orm import Session

from models import (
    OrderLine,
    Batch,
    InsufficientStocksException,
    allocate as model_allocate,
)
from infrastructure.repository import AbstractRepository

# Seems like this module sits between the Application (API) Layer and the Domain Layer
# This is used by the application (API) layer to perform domain verbs/actions


def allocate(
    line: OrderLine, repo: AbstractRepository, session: Session
) -> Batch | None:
    batch = repo.list()

    if not is_valid_sku(line.sku, batch):
        raise InvalidSkuError(f"Invalid sku: {line.sku}")

    allocation = model_allocate(line, batch)
    session.commit()  # TODO: refactor this so that application service layer is not dependent on specific DB
    return allocation


# TODO: As an exercise, implement deallocate
def deallocate(line: OrderLine, repo: AbstractRepository, session: Session):
    raise NotImplementedError


class InvalidSkuError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def is_valid_sku(sku, batches: List[Batch]):
    return sku in {batch.name for batch in batches}
