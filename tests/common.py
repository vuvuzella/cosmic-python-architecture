import datetime
from random import random
from typing import List, Optional, Tuple
from uuid import uuid1

from sqlalchemy import String, cast, text
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
    return f"{rand_name}-int(random() * 1000000000)"


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


def delete_all_data(session: Session):
    result = session.execute(
        text(
            """
            DELETE FROM public.allocations;
            DELETE FROM public.order_lines;
            DELETE FROM public.batch;
            DELETE FROM public.product;
            """
        )
    )
    session.commit()
    return result


def get_allcated_batch_ref(session: Session, orderid: str, batch_ref: str):
    result = session.execute(
        text(
            """
            SELECT batch_id
            FROM public.allocations
            WHERE batch_id = ':batch_ref' AND orderline_id = :orderid
            LIMIT 1;
            """
        ),
        dict(batch_ref=batch_ref, orderid=orderid),
    )
    session.commit()
    return result
