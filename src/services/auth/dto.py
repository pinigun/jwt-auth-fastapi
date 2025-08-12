from dataclasses import asdict, dataclass


@dataclass
class TokensDTO:
    access_token: str
    refresh_token: str
    
    def asdict(self):
        return asdict(self)
