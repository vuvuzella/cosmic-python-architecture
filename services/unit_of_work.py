from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Generic, List, Protocol, Type, TypeVar, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.aggregates import AbstractAggregate, Product
from domain.models import Batch, Entity
from infrastructure import (
    AbstractRepository,
    BatchFakeRepository,
    BatchRepository,
    FakeRepository,
    ProductFakeRepository,
    ProductRepository,
    SqlAlchemyRepository,
)
from settings import global_settings

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(url=global_settings.DB_DSN, isolation_level="REPEATABLE READ"),
    expire_on_commit=False,
    autocommit=False,
)

RepositoryT = TypeVar("RepositoryT", bound=AbstractRepository)
SqlAlchemyRepositoryT = TypeVar("SqlAlchemyRepositoryT", bound=SqlAlchemyRepository)


class AbstractUnitOfWork(ABC, Generic[RepositoryT]):
    repository: RepositoryT

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def __enter__(self, *args):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, *args):
        raise NotImplementedError


class BaseUnitOfWork(AbstractUnitOfWork, ABC, Generic[SqlAlchemyRepositoryT]):
    # _repository resides in the Base class because it is part of how to implement
    # a generic Base Unit Of Work with common implementations of
    # rollback, _commit, __enter__ and __exit__ methods
    @property
    @abstractmethod
    def _repository(self) -> Type[SqlAlchemyRepositoryT]:
        ...

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    def __enter__(self):
        """
        This UoW can be used as a context manager
        """
        self.session = self.session_factory()
        self.repository = self._repository(session=self.session)

    def __exit__(self, *args):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def _commit(self):
        return self.commit()

    def commit(self):
        self.session.commit()


class SqlAlchemyUnitOfWork(BaseUnitOfWork[SqlAlchemyRepository]):
    """
    This contains the units of work that needs to be done
    given that the storage is SQL Alchemy
    """

    @property
    def _repository(self) -> Type[SqlAlchemyRepository]:
        return SqlAlchemyRepository


class ProductUnitOfWork(BaseUnitOfWork[ProductRepository]):
    @property
    def _repository(self) -> Type[ProductRepository]:
        return ProductRepository

    def get(self, sku: str) -> Product:
        try:
            product = self.repository.get(sku=sku)
            return product
        except Exception as e:
            # TODO: add logger
            raise e


class BatchUnitOfWork(BaseUnitOfWork[BatchRepository]):
    @property
    def _repository(self) -> Type[BatchRepository]:
        return BatchRepository


EntityOrAggregateT = TypeVar("EntityOrAggregateT", bound=Entity | AbstractAggregate)
FakeRepositoryT = TypeVar("FakeRepositoryT", bound=FakeRepository)


class FakeUnitOfWork(
    AbstractUnitOfWork, ABC, Generic[FakeRepositoryT, EntityOrAggregateT]
):
    @property
    @abstractmethod
    def _repository(self) -> Type[FakeRepositoryT]:
        ...

    def __init__(self, data: List[EntityOrAggregateT] | None = []) -> None:
        self.repository = self._repository(data)
        super().__init__()

    def _commit(self):
        self.comitted = True

    def __enter__(self, *args):
        ...

    def __exit__(self, *args):
        ...

    def rollback(self):
        ...

    def commit(self):
        self._commit()


class BatchFakeUnitOfWork(FakeUnitOfWork[BatchFakeRepository, Batch]):
    @property
    def _repository(self) -> Type[BatchFakeRepository]:
        return BatchFakeRepository


class ProductFakeUnitOfWork(FakeUnitOfWork[ProductFakeRepository, Product]):
    @property
    def _repository(self) -> Type[ProductFakeRepository]:
        return ProductFakeRepository
