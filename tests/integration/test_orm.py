from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from domain.models import Orderline


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
        Orderline("order1", "RED-CHAIR", 12),
        Orderline("order2", "RED-TABLE", 13),
        Orderline("order3", "BLUE-LIPSTICK", 14),
    ]

    assert session.query(Orderline).all() == expected


def test_orderline_mapper_can_save_lines(session: Session):
    new_line = Orderline("order1", "DECORATIVE-WIDGET", 12)
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
