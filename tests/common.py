import datetime
from random import random
from typing import List, Optional, Tuple
from uuid import uuid1

from sqlalchemy import text
from sqlalchemy.orm import Session

from infrastructure.orm import metadata


def random_sku(sku: Optional[str] = None):
    return f"sku-{uuid1()}"


def random_batch_ref(number: Optional[int] = None):
    return int(random() * 1000000000)


def random_batch_id():
    return int(random() * 1000000000)


def random_order_id(name: str | None = None):
    # return f"order-id-{uuid1()}"
    rand_name = name if name else "random_name"
    return int(random() * 1000000000)


# TODO: inserts a stock to the database!
def add_stock(stocks: List[Tuple]):
    raise NotImplementedError


def insert_product(session: Session, sku: str, product_version: int = 1):
    result = session.execute(
        text(
            """
            INSERT INTO public.product
                (sku, version)
            VALUES
                (:sku, :version)
            ;
            """
        ),
        dict(sku=sku, version=product_version),
    )
    result = session.commit()
    print(result)
    return result


def insert_batch(
    session: Session,
    ref: int,
    sku: str,
    qty: int,
    eta: datetime.datetime | None = None,
):
    result = session.execute(
        text(
            """
            INSERT INTO public.batch
                (reference, sku, _purchased_quantity, eta)
            VALUES
                (:reference, :sku, :qty, :eta)
            ;
            """
        ),
        dict(reference=ref, sku=sku, qty=qty, eta=eta),
    )
    result = session.commit()
    print(result)
    return result


def delete_order_line(session: Session, sku: str):
    result = session.execute(
        text(
            """
            DELETE from public.order_lines WHERE sku = :sku;
            """
        ),
        dict(sku=sku),
    )
    session.commit()
    return result
