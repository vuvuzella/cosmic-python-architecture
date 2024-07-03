import threading
import traceback
from time import sleep

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.aggregates import Product
from domain.models import Orderline
from services.services import change_batch_quantity
from services.unit_of_work import BatchUnitOfWork, ProductUnitOfWork
from tests.common import (
    delete_all_data,
    get_allcated_batch_ref,
    insert_allocations,
    insert_batch,
    insert_order_lines,
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


@pytest.fixture(scope="function")
def data_with_allocations(test_data, session: Session):
    sku, batch_ref = test_data

    order_five = Orderline(orderid=random_order_id(), sku=sku, qty=5)
    order_three = Orderline(orderid=random_order_id(), sku=sku, qty=3)
    order_two = Orderline(orderid=random_order_id(), sku=sku, qty=2)

    insert_order_lines(
        session=session,
        orderid=order_five.orderid,
        sku=order_five.sku,
        qty=order_five.qty,
    )
    insert_allocations(session=session, orderid=order_five.orderid, batch_ref=batch_ref)
    insert_order_lines(
        session=session,
        orderid=order_three.orderid,
        sku=order_three.sku,
        qty=order_three.qty,
    )
    insert_allocations(
        session=session, orderid=order_three.orderid, batch_ref=batch_ref
    )
    insert_order_lines(
        session=session,
        orderid=order_two.orderid,
        sku=order_two.sku,
        qty=order_two.qty,
    )
    insert_allocations(session=session, orderid=order_two.orderid, batch_ref=batch_ref)

    yield str(sku), str(batch_ref), [order_five, order_three, order_two]

    delete_all_data(session=session)
    print("Done")


def test_change_product_batch_quantity(data_with_allocations, session: Session):
    sku, batch_ref, orderlines = data_with_allocations

    print(sku)
    print(batch_ref)
    print(orderlines)

    uow = ProductUnitOfWork()
    new_quantity = 20

    change_batch_quantity(
        batch_ref=batch_ref, sku=sku, new_quantity=new_quantity, uow=uow
    )

    [[qty]] = session.execute(
        text(
            "SELECT _purchased_quantity FROM public.batch WHERE reference = :batch_ref"
        ),
        dict(batch_ref=batch_ref),
    )
    assert qty == new_quantity


def test_uow_retrieve_batch_and_allocate(session: Session, test_data):
    # TODO: implement tests for the unit of work
    sku, batch_ref = test_data
    orderid = random_order_id()
    uow = BatchUnitOfWork()
    with uow:
        batch = uow.repository.get(reference=batch_ref)
        line = Orderline(orderid=orderid, sku=sku, qty=10)
        batch.allocate(line=line)
        uow.commit()

    results = get_allcated_batch_ref(
        session=session, orderid=orderid, batch_ref=batch_ref
    )
    results = results.fetchall()
    print(results)

    assert results is not None
    [[results]] = results
    assert int(results) == batch_ref


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

    q = list(
        session.execute(
            text(
                """
    SELECT version FROM public.product WHERE sku = :sku LIMIT 1;
    """
            ),
            dict(sku=sku),
        )
    )

    # session.commit()
    [[version]] = q

    assert version != None
    # must increment version only once
    assert version == 2
    # must have thrown an exception
    assert len(exceptions) == 1


def test_rolls_back_uncommitted_work_by_default(session: Session):
    sku = random_sku()
    new_product = Product(sku=sku, batches=[])

    uow = ProductUnitOfWork()

    with uow:
        uow.repository.add(new_product)
        # uow.commit()

    result = list(
        session.execute(
            text("SELECT * FROM public.product WHERE sku = :sku"), dict(sku=sku)
        )
    )

    assert len(result) == 0


def test_rolls_back_on_error(session: Session):
    sku = random_sku()
    new_product = Product(sku=sku, batches=[])

    uow = ProductUnitOfWork()

    class MyException(Exception):
        ...

    with pytest.raises(MyException, match="CustomException"):
        with uow:
            uow.repository.add(new_product)
            raise MyException("CustomException")

    q_exec = session.execute(
        text("SELECT * FROM public.product WHERE sku = :sku"), dict(sku=sku)
    )
    results = q_exec.fetchall()

    assert len(results) == 0
