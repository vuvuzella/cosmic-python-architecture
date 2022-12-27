from abc import ABC, abstractclassmethod
from sqlalchemy.orm import Session
from typing import List

from models import Batch

# TODO: use python generics to generalize this one
class AbstractRepository(ABC):
    @abstractclassmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractclassmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: Batch):
        self._session.add(batch)

    def get(self, reference) -> Batch:
        return self._session.query(Batch).filter_by(reference=reference).one()

    def list(self) -> List[Batch]:
        return self._session.query(Batch).all()
