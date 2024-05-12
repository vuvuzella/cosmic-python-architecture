from typing import Callable, Dict, List, Type

from domain.events import Event, OutOfStockEvent

HANDLERS: Dict[Type[Event], List[Callable]] = {OutOfStockEvent: []}


def handle_event(event: Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_out_of_stock_notification(event: Event):
    print(f"Sending an email for event: {event}")
