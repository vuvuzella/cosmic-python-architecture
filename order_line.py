from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    orderedid: str
    sku: str
    qty: int
