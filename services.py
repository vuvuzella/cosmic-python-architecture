from typing import List

from models import OrderLine, Batch, InsufficientStocksException


def allocate(line: OrderLine, batch: List[Batch]) -> Batch | None:
    sorted_allocatable_batch = [
        batch_item for batch_item in sorted(batch) if batch_item.can_allocate(line=line)
    ]
    try:
        allocatable_batch = next(iter(sorted_allocatable_batch))
        allocatable_batch.allocate(line)
        return allocatable_batch
    except StopIteration:
        raise InsufficientStocksException(f"Insufficient in stock fpr {line.sku}")
