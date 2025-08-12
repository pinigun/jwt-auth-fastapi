from typing import Type
from abc import ABC, abstractmethod

from ..repositories.users.interface import IUsersRepo


class IUnitOfWork(ABC):
    @abstractmethod
    def __init__(self, users_repo_class: Type[IUsersRepo]):
        ...

    @property
    @abstractmethod
    def users(self,) -> IUsersRepo:
        ...
    
    @abstractmethod
    async def commit(self,):
        ...
    
    @abstractmethod
    async def rollback(self,):
        ...
    
    @abstractmethod
    async def __aenter__(self,) -> "IUnitOfWork":
        ...
    
    async def __aexit__(self, exc_type: Type[Exception], *args):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
