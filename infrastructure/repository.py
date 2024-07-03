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

AggregateOrEntityT = TypeVar(
    "AggregateOrEntityT", bound=Union[AbstractAggregate, Entity]
)


class AbstractRepository(ABC, Generic[AggregateOrEntityT]):
    @abstractmethod
    def add(self, aggregate: AggregateOrEntityT) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, reference: Any) -> AggregateOrEntityT:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[AggregateOrEntityT]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository, Generic[AggregateOrEntityT]):
    """Generic Sql Alchemy repository
    usually this should return an aggregate
    aggregates are entrypoints to entities
    """

    @property
    @abstractmethod
    def _aggregate(self) -> Type[AggregateOrEntityT]:
        ...

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: AggregateOrEntityT):
        self._session.add(batch)

    def get(self, sku: str) -> AggregateOrEntityT:
        return self._session.query(self._aggregate).filter_by(sku=sku).one()

    def list(self) -> List[AggregateOrEntityT]:
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


class FakeRepository(AbstractRepository, Generic[AggregateOrEntityT]):
    @abstractmethod
    def _get_identifier(self, item: AggregateOrEntityT):
        ...

    def __init__(self, initial_data: List[AggregateOrEntityT] | None = None) -> None:
        self._data = initial_data or []
        super().__init__()

    def add(self, aggregate: AggregateOrEntityT) -> None:
        self._data.append(aggregate)

    def get(self, reference: str) -> AggregateOrEntityT:
        items = [i for i in self._data if self._get_identifier(i) == reference]
        items = iter(items)
        return next(items)

    def list(self) -> List[AggregateOrEntityT]:
        return self._data


class ProductFakeRepository(FakeRepository[Product]):
    def _get_identifier(self, item: Product):
        return item.sku


class BatchFakeRepository(FakeRepository[Batch]):
    def _get_identifier(self, item: Batch):
        return item.reference
