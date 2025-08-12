from abc import ABC, abstractmethod
from ...entities.users import User


class IUsersRepo(ABC):
    @abstractmethod
    async def add_user(self, user: User) -> User:
        ...
        
    @abstractmethod
    async def get_by_email(self, email: str):
        ...
        
    @abstractmethod
    async def get_by_id(self, id: str):
        ...
    
    @abstractmethod
    async def get_refresh_token(self, user_id: int):
        ...
    
    @abstractmethod
    async def add_refresh_token(self, user_id: int, refresh_token: str):
        ...
        
    @abstractmethod
    async def update_refresh_token(self, user_id: int, refresh_token: str):
        ...
