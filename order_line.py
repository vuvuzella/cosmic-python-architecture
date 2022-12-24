from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    orderedid: str
    sku: str
    qty: int

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, OrderLine):
            return False
        return self.__hash__() == __o.__hash__()

    def __hash__(self) -> int:
        return hash(f"{self.orderedid}{self.sku}{self.qty}")
