from models import Batch, OrderLine

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from infrastructure.repository import SqlAlchemyRepository


def insert_order_lines(session: Session):
    session.execute(
        text(
            """
        INSERT INTO order_lines (orderid, sku, qty) VALUES
            ('order-one', 'GENERIC-SOFA', 12);
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
        {"orderid": "order-one", "sku": "GENERIC-SOFA"},
    )
    return order_line_id


# TODO: implement batch insertion
def insert_batch(session: Session, batch_reference: str) -> int:
    statement = text(
        """
        INSERT INTO public.batch (reference, name, _purchased_quantity, eta)
            values (:batch_reference, 'GENERIC-SOFA', 100, NULL)
        """,
    )
    session.execute(statement=statement, params=dict(batch_reference=batch_reference))
    session.commit()

    [[batch_id]] = session.execute(
        text(
            """
            SELECT id FROM public.batch
                WHERE reference = :batch_reference
                AND name = 'GENERIC-SOFA';
            """
        ),
        dict(batch_reference=batch_reference),
    )
    return batch_id


# TODO: implement insert allocation
# This might require modifying tables and mappings!
def insert_allocation(session: Session, order_line_id: int, batch_id: int):
    session.execute(
        text(
            """
            INSERT INTO order_lines (orderid, sku, qty)
                VALUES (:order_line_id, 'GENERIC-SOFA', 10);
            """
        ),
        dict(order_line_id=order_line_id, batch_id=batch_id),
    )
    session.execute(
        text(
            """
            INSERT INTO allocations (orderline_id, batch_id)
                VALUES (:order_line_id, :batch_id);
            """
        ),
        dict(order_line_id=order_line_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(
    session: Session, restart_api: str
):
    order_line_id = insert_order_lines(session)
    batch_one_id = insert_batch(session, "batch-one")
    batch_two_id = insert_batch(session, "batch-two")
    insert_allocation(session, order_line_id, batch_one_id)  # TODO: implement this one
    repo = SqlAlchemyRepository(session)
    retrieved = repo.get("batch-one")
    expected = Batch("batch-one", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.name == expected.name
    assert retrieved.available_quantity == expected.available_quantity
    assert retrieved._allocations == set([OrderLine("order-one", "GENERIC-SOFA", 12)])


def test_repository_can_save_a_batch(session: Session):
    batch = Batch("batch-no-1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlAlchemyRepository(session)
    repo.add(batch=batch)
    session.commit()

    rows = session.execute(
        text(
            """
        SELECT reference, name, _purchased_quantity, eta FROM batch
            WHERE reference = 'batch-no-1' and name = 'RUSTY-SOAPDISH'
        """
        )
    ).all()

    assert rows == [("batch-no-1", "RUSTY-SOAPDISH", 100, None)]
