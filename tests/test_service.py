import pytest
from sqlalchemy.orm import Session

from models import OrderLine, Batch
from infrastructure.repository import FakeRepository
from services.services import allocate, InvalidSkuError


# tests about orchestration stuff


class FakeSession(Session):
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocations():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "MY-CHAIR", 100)

    repo = FakeRepository([batch])
    result = allocate(line, repo, FakeSession())

    assert result == "batch-ref-1"


def test_error_for_invalid_sku():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "NOT-MY-CHAIR", 100)
    repo = FakeRepository([batch])

    with pytest.raises(InvalidSkuError, match="Invalid sku MY-CHAIR"):
        allocate(line, repo, FakeSession())


def test_commits():
    line = OrderLine("order1", "MY-CHAIR", 10)
    batch = Batch("batch-ref-1", "MY-CHAIR", 100)
    repo = FakeRepository([batch])
    session = FakeSession()
    result = allocate(line, repo, session)

    assert session.committed == True
