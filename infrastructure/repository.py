from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List

from models import Batch

# This module encapsulates the way of communicating with a specific database by means of an interface
# which in this case, is the AbstractRepository.
# The idea is to separate the database access specific functions from the model themselves.
# Repositories should never know about the model


# TODO: use python generics to generalize this one
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Batch]:
        raise NotImplementedError


# How can we make this generic to have repository of any entity in
# our database?
class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: Batch):
        self._session.add(batch)

    def get(self, reference: str) -> Batch:
        return self._session.query(Batch).filter_by(reference=reference).one()

    def list(self) -> List[Batch]:
        return self._session.query(Batch).all()


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
