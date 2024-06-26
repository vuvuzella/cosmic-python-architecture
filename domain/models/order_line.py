from dataclasses import dataclass

from sqlalchemy_serializer import SerializerMixin

from domain.models.base import Entity


@dataclass(frozen=False)
class Orderline(Entity, SerializerMixin):
    orderid: str
    sku: str
    qty: int

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Orderline):
            return False
        return self.__hash__() == __o.__hash__()

    def __hash__(self) -> int:
        return hash(f"{self.orderid}{self.sku}{self.qty}")
