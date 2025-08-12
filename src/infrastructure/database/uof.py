import inspect
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.uof.abstract import IUnitOfWork
from src.infrastructure.database.repositories.users import SqlAlchemyUsersRepo


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        async_session_maker,
        users_repo_class: Type[SqlAlchemyUsersRepo] | None = None
    ):
        if not inspect.isclass(users_repo_class):
            raise TypeError(f"Excpected a class, got object of class '{type(users_repo_class).__name__}'")
        
        self.__async_session_maker = async_session_maker
        self.__users_repo_class = users_repo_class
        self.__session: AsyncSession | None = None
        self.__users = None
    
    @property
    def users(self,):
        return self.__users
    
    async def commit(self) -> None:
        await self.__session.commit()
    
    async def rollback(self) -> None:
        await self.__session.rollback()

    async def __aenter__(self,) -> "SQLAlchemyUnitOfWork":
        self.__session = self.__async_session_maker()
        self.__session.begin()
        self.__users = self.__users_repo_class(self.__session)
        return self
