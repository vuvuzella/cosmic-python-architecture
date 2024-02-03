from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, TypeVar, Generic, Any

from models import Batch
from aggregates import Product

# This module encapsulates the way of communicating with a specific database by means of an interface
# which in this case, is the AbstractRepository.
# The idea is to separate the database access specific functions from the model themselves.
# Repositories should never know about the model

AggregateT = TypeVar("AggregateT")
EntityT = TypeVar("EntityT")


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, aggregate: AggregateT):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference: Any) -> AggregateT:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[AggregateT]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository, Generic[AggregateT]):
    aggregates: AggregateT

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: AggregateT):
        self._session.add(batch)

    def get(self, reference: str) -> AggregateT:
        return self._session.query(AggregateT).filter_by(reference=reference).one()

    def list(self) -> List[AggregateT]:
        return self._session.query(AggregateT).all()


# This is an antipattern! Repositories should be returning just aggregates! not Entities!
# We just demonstrate it here
class BatchRepository(SqlAlchemyRepository[Batch]):
    ...


class ProductRepository(SqlAlchemyRepository[Product]):
    ...


class FakeRepository(AbstractRepository):
    def __init__(self, batches: List[Batch] = []) -> None:
        self._batches = batches
        super().__init__()

    # TODO: no uniqueness validation or check!
    def add(self, batch) -> None:
        self._batches.append(batch)

    def get(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[Batch]:
        return self._batches
