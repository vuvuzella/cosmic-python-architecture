from dataclasses import asdict, dataclass
from typing import Set


@dataclass
class AbstractAggregate:
    def to_json(self):
        def serialize(v):
            if isinstance(v, Set):
                return list(v)
            return v

        return asdict(
            self,
            dict_factory=lambda fields: {f"{k}": serialize(v) for (k, v) in fields},
        )
