from models import Batch

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from repository import SqlAlchemyRepository


def test_repository_can_save_a_batch(session: Session):
    batch = Batch("batch-no-1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlAlchemyRepository(session)
    repo.add(batch=batch)
    session.commit()

    rows = session.execute(
        text("SELECT reference, sku, _purchased_quantity, eta FROM batches")
    ).all()

    assert rows == [batch]
