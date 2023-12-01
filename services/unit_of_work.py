from abc import ABC, abstractmethod
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure import AbstractRepository, SqlAlchemyRepository, FakeRepository
from models import Batch
from settings import global_settings

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(url=global_settings.DB_DSN), expire_on_commit=False
)


class AbstractUnitOfWork(ABC):
    batches: AbstractRepository

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


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    This contains the units of work that needs to be done
    given that the storage is SQL Alchemy
    """

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    def __enter__(self):
        """
        This UoW can be used as a context manager
        """
        self.session = self.session_factory()
        self.batches = SqlAlchemyRepository(self.session)

    def __exit__(self, *args):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, batches: List[Batch] = []) -> None:
        self.batches = FakeRepository(batches)
        super().__init__()

    def rollback(self):
        ...

    def commit(self):
        ...

    def __enter__(self, *args):
        ...

    def __exit__(self, *args):
        ...
