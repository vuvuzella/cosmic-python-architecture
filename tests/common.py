import datetime
import string
from random import choices, random
from typing import List, Optional, Tuple
from uuid import uuid1

from sqlalchemy import String, cast, text
from sqlalchemy.orm import Session

from domain.models.order_line import Orderline
from infrastructure.orm import metadata


def generate_random_strings(length: int = 8):
    return "".join(choices(string.ascii_letters, k=length))


def random_sku(sku: Optional[str] = None):
    return f"sku-{uuid1()}"


def random_batch_ref(ref_name: Optional[str] = generate_random_strings()):
    return f"{ref_name}-{int(random() * 1000000000)}"


def random_batch_id():
    return int(random() * 1000000000)


def random_order_id(name: str | None = None):
    # return f"order-id-{uuid1()}"
    rand_name = name if name else "random_name"
    return f"{rand_name}-{int(random() * 1000000000)}"


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
    return result


def insert_batch(
    session: Session,
    ref: str,
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
    return result


def insert_order_lines(session: Session, orderid: str, sku: str, qty: int):
    result = session.execute(
        text(
            """
    INSERT INTO public.order_lines
    (sku, qty, orderid)
    VALUES
    (:sku, :qty, :orderid)
    ;
    """
        ),
        dict(sku=sku, qty=qty, orderid=orderid),
    )
    session.commit()
    return result


def insert_allocations(session: Session, orderid: str, batch_ref: str):
    result = session.execute(
        text(
            """
        INSERT INTO public.allocations (orderline_id, batch_id)
        VALUES (:orderid, :batch_id)
        """
        ),
        dict(orderid=orderid, batch_id=batch_ref),
    )
    session.commit()
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
