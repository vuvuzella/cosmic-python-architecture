from models import OrderLine

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


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
