import threading
import traceback
from time import sleep

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.models import Orderline
from services.unit_of_work import BatchUnitOfWork, ProductUnitOfWork
from tests.common import (
    delete_all_data,
    get_allcated_batch_ref,
    insert_batch,
    insert_product,
    random_batch_ref,
    random_order_id,
    random_sku,
)


@pytest.fixture(scope="function")
def test_data(session: Session):
    sku = random_sku()
    batch_ref = random_batch_ref()

    insert_product(session=session, sku=sku)
    insert_batch(session=session, ref=batch_ref, sku=sku, qty=10)

    yield sku, batch_ref

    delete_all_data(session=session)
    print("Done")


def test_uow_retrieve_batch_and_allocate(session: Session, test_data):
    # TODO: implement tests for the unit of work
    sku, batch_ref = test_data
    orderid = random_order_id()
    uow = BatchUnitOfWork()
    with uow:
        batch = uow.repository.get(reference=batch_ref)
        line = Orderline(orderid=orderid, sku=sku, qty=10)
        batch.allocate(line=line)
        # uow.commit()

    results = get_allcated_batch_ref(
        session=session, orderid=orderid, batch_ref=batch_ref
    )
    results = results.fetchall()
    print(results)

    assert results is not None
    [[results]] = results
    assert results == batch_ref


def try_to_allocate(orderid, sku, exceptions):
    line = Orderline(orderid=orderid, sku=sku, qty=10)

    uow = ProductUnitOfWork()

    try:
        with uow:
            product = uow.get(sku=sku)
            product.allocate(line)
            sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(test_data, session: Session):
    sku, batch_ref = test_data

    orderid_one = random_order_id("one")
    orderid_two = random_order_id("two")

    exceptions = []

    try_1 = lambda: try_to_allocate(orderid=orderid_one, sku=sku, exceptions=exceptions)  # noqa: E731
    try_2 = lambda: try_to_allocate(orderid=orderid_two, sku=sku, exceptions=exceptions)  # noqa: E731
    thread1 = threading.Thread(target=try_1)
    thread2 = threading.Thread(target=try_2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    q = session.execute(
        text(
            """
    SELECT version FROM public.product WHERE sku = :sku LIMIT 1;
    """
        ),
        dict(sku=sku),
    )

    session.commit()
    [[version]] = q.fetchall()

    assert version != None
    # must increment version only once
    assert version == 2
    # must have thrown an exception
    assert len(exceptions) == 1
