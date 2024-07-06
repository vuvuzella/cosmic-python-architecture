import pytest
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from domain.models import Batch, Orderline
from infrastructure.repository import BatchRepository
from tests.common import (
    insert_allocations,
    insert_batch,
    insert_order_lines,
    insert_product,
    random_batch_ref,
    random_order_id,
    random_sku,
)


@pytest.fixture(scope="function")
def prepare_test_data(session: Session):
    order_line_id = random_order_id()
    sku = random_sku()
    ordered_qty = 12

    batch_one = random_batch_ref()
    purchased_quantity = 20

    batch_two = random_batch_ref()
    p_qty = 10

    insert_product(session=session, sku=sku)
    insert_batch(session=session, ref=batch_one, sku=sku, qty=purchased_quantity)
    insert_batch(session=session, ref=batch_two, sku=sku, qty=p_qty)
    insert_order_lines(session=session, orderid=order_line_id, sku=sku, qty=ordered_qty)
    insert_allocations(session=session, orderid=order_line_id, batch_ref=batch_one)

    return (
        dict(orderid=order_line_id, sku=sku, ordered_qty=ordered_qty),
        dict(batch_ref=batch_one, purchased_quantity=purchased_quantity),
        dict(batch_ref=batch_two, purchased_quantity=p_qty),
        sku,
    )


def test_repository_can_retrieve_a_batch_with_allocations(
    session: Session, prepare_test_data
):
    order, batch_one, batch_two, sku = prepare_test_data
    repo = BatchRepository(session)
    retrieved = repo.get(batch_one.get("batch_ref"))
    expected = Batch(
        batch_one.get("batch_ref"),
        sku,
        int(batch_one.get("purchased_quantity")) - int(order.get("ordered_qty")),
        eta=None,
    )
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved.available_quantity == expected.available_quantity
    assert retrieved._allocations == set(
        [Orderline(order.get("orderid"), sku, order.get("ordered_qty"))]
    )


def test_repository_can_save_a_batch(session: Session, prepare_test_data):
    batch_ref = random_batch_ref()
    qty = 100

    order, batch_one, batch_two, sku = prepare_test_data

    batch = Batch(batch_ref, sku, qty, eta=None)

    repo = BatchRepository(session)
    repo.add(batch=batch)
    session.commit()

    rows = session.execute(
        text(
            """
        SELECT reference, sku, _purchased_quantity, eta FROM batch
            WHERE reference = :batch_ref and sku = :sku
        """
        ),
        dict(batch_ref=batch_ref, sku=sku),
    ).all()

    assert rows == [(batch_ref, sku, 100, None)]
