from dataclasses import asdict, dataclass


@dataclass
class UserDTO:
    id:     int
    email:  str
    
    def asdict(self):
        return asdict(self)
