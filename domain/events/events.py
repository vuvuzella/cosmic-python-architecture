from dataclasses import dataclass


@dataclass
class Event:
    pass


@dataclass
class OutOfStockEvent(Event):
    sku: str
