from settings import settings
from order_line import OrderLine
from orm import start_mappers
from orm import order_lines
from sqlalchemy.engine import Connection, create_engine, Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text, select
from typing import Generator

import pytest

# code mostly from https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(settings.DB_DSN)  # TODO: curate special DSN for test database


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    order_lines.metadata.create_all(engine)
    start_mappers()
    yield
    order_lines.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def session(engine: Engine, tables) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close


def test_orderline_mapper_can_load_lines(session: Session):
    sql_statement = text(
        """
        INSERT INTO order_lines (orderid, sku, qty) VALUES
        ('order1', 'RED-CHAIR', 12),
        ('order2', 'RED-TABLE', 13),
        ('order3', 'BLUE-LIPSTICK', 14);
        """
    )
    session.execute(sql_statement)

    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order2", "RED-TABLE", 13),
        OrderLine("order3", "BLUE-LIPSTICK", 14),
    ]

    assert session.query(OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session: Session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = session.execute(
        text(
            """
        SELECT orderid, sku, qty from order_lines where sku = 'DECORATIVE-WIDGET';
        """
        )
    ).all()
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
