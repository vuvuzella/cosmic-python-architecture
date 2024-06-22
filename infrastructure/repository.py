from abc import ABC, abstractmethod
from typing import Any, Generic, List, Type, TypeVar, Union

from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from domain.aggregates import Product
from domain.aggregates.base import AbstractAggregate
from domain.models import Batch
from domain.models.base import Entity

# This module encapsulates the way of communicating with a specific database by means of an interface
# which in this case, is the AbstractRepository.
# The idea is to separate the database access specific functions from the model themselves.
# Repositories should never know about the model

AggregateT = TypeVar("AggregateT", bound=Union[AbstractAggregate, Entity])
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
    """Generic Sql Alchemy repository
    usually this should return an aggregate
    aggregates are entrypoints to entities
    """

    @property
    @abstractmethod
    def _aggregate(self) -> Type[AggregateT]:
        ...

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: AggregateT):
        self._session.add(batch)

    def get(self, sku: str) -> AggregateT:
        return self._session.query(self._aggregate).filter_by(sku=sku).one()

    def list(self) -> List[AggregateT]:
        return self._session.query(self._aggregate).all()


# This is an antipattern! Repositories should be returning just aggregates! not Entities!
# We just demonstrate it here
class BatchRepository(SqlAlchemyRepository[Batch]):
    @property
    def _aggregate(self) -> Type[Batch]:
        return Batch

    def get(self, reference: str) -> Batch:
        return (
            self._session.query(self._aggregate)
            .filter_by(reference=cast(reference, String))
            .one()
        )


class ProductRepository(SqlAlchemyRepository[Product]):
    @property
    def _aggregate(self) -> Type[Product]:
        return Product


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
