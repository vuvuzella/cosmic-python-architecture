from models import Batch, OrderLine

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from repository import SqlAlchemyRepository


def insert_order_lines(session: Session):
    session.execute(
        text(
            """
        INSERT INTO order_lines (orderid, sku, qty) VALUES
            ('order1', 'GENERIC-SOFA', 12);
        """
        )
    )

    [[order_line_id]] = session.execute(
        text(
            """
        SELECT id FROM order_lines
        WHERE orderid=:orderid AND sku=:sku
        """
        ),
        {"orderid": "order1", "sku": "GENERIC-SOFA"},
    )
    return order_line_id


# TODO: implement batch insertion
def insert_batch(session: Session, batch_reference: str) -> int:
    ...


# TODO: implement insert allocation
# This might require modifying tables and mappings!
def insert_allocation(session: Session, order_line_id: int, batch_id: int):
    ...


def test_repository_can_retrieve_a_batch_with_allocations(session: Session):
    order_line_id = insert_order_lines(session)
    batch_one_id = insert_batch(session, "batch-one")
    batch_two_id = insert_batch(session, "batch-two")
    insert_allocation(session, order_line_id, batch_one_id)  # TODO: implement this one
    repo = SqlAlchemyRepository(session)
    retrieved = repo.get("batch-one")
    expected = Batch("batch-one", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.name == expected.name
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {OrderLine("order-one", "GENEROC-SOFA", 12)}


def test_repository_can_save_a_batch(session: Session):
    batch = Batch("batch-no-1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlAlchemyRepository(session)
    repo.add(batch=batch)
    session.commit()

    rows = session.execute(
        text("SELECT reference, name, _purchased_quantity, eta FROM batch")
    ).all()

    assert rows == [("batch-no-1", "RUSTY-SOAPDISH", 100, None)]
