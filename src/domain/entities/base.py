from dataclasses import asdict, dataclass


@dataclass
class BaseEntity:
    def asdict(self,):
        return asdict(self)
