from abc import ABC, abstractmethod
from typing import Generic, List, Type, TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.aggregates import Product
from domain.models import Batch
from infrastructure import (
    AbstractRepository,
    BatchRepository,
    FakeRepository,
    ProductRepository,
    SqlAlchemyRepository,
)
from settings import global_settings

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(url=global_settings.DB_DSN, isolation_level="REPEATABLE READ"),
    expire_on_commit=False,
)

RepositoryT = TypeVar("RepositoryT", bound=SqlAlchemyRepository)


class AbstractUnitOfWork(ABC):
    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def __enter__(self, *args):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, *args):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork, Generic[RepositoryT]):
    """
    This contains the units of work that needs to be done
    given that the storage is SQL Alchemy
    """

    repository: RepositoryT

    @property
    def _repository(self) -> Type[RepositoryT]:
        ...

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    def __enter__(self):
        """
        This UoW can be used as a context manager
        """
        self.session = self.session_factory()
        self.repository = self._repository(self.session)

    def __exit__(self, *args):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def _commit(self):
        return self.commit()

    def commit(self):
        self.session.commit()


class ProductUnitOfWork(SqlAlchemyUnitOfWork[ProductRepository]):
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


class BatchUnitOfWork(SqlAlchemyUnitOfWork[BatchRepository]):
    @property
    def _repository(self) -> Type[BatchRepository]:
        return BatchRepository


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, batches: List[Batch] = []) -> None:
        self.repository = FakeRepository(batches)
        super().__init__()

    def rollback(self):
        ...

    def commit(self):
        ...

    def __enter__(self, *args):
        ...

    def __exit__(self, *args):
        ...
