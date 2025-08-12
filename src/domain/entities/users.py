from dataclasses import dataclass

from .base import BaseEntity


@dataclass
class User(BaseEntity):
    id:             int
    email:          str
    password_hash:  str
    
    def __eq__(self, obj):
        return self.__dict__ == obj.__dict__
