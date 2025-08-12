from typing import Any
from loguru import logger
from dataclasses import dataclass
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.users import User
from src.domain.repositories.users.interface import IUsersRepo
from src.domain.repositories.exc import CustomRepoException, RefreshTokenNotFound, UserNotFound

from ..models import RefreshToken as RefreshTokenDBModel, User as UserDBModel


@dataclass
class SqlAlchemyUsersRepo(IUsersRepo):
    _session: AsyncSession
        
    async def add_user(self, user: User) -> User:
        user_db = UserDBModel(
            email=user.email,
            password_hash=user.password_hash,
        )
        
        self._session.add(user_db)
        await self._session.flush()
        await self._session.refresh(user_db)
        
        return User(
            id=user_db.id,
            email=user_db.email,
            password_hash=user_db.password_hash,
        )
        
    async def _get_user(self, *conditions: Any) -> User:
        
        stmt = select(UserDBModel).where(*conditions)
        result = await self._session.execute(stmt)
        
        db_user: UserDBModel = result.scalar_one_or_none()
        logger.debug(db_user)
        if not db_user:
            raise UserNotFound
        
        return User(
            id=db_user.id,
            email=db_user.email,
            password_hash=db_user.password_hash
        )
        
    async def get_by_id(
        self,
        id: int,
    ) -> User:
        return await self._get_user(
            UserDBModel.id == id
        )
        
    async def get_by_email(
        self,
        email: str,
    ) -> User:
        return await self._get_user(
            UserDBModel.email == email
        )
            
    async def get_refresh_token(self, user_id: int) -> str:
        stmt = (
            select(RefreshTokenDBModel.token)
            .where(RefreshTokenDBModel.user_id == user_id)
        )
        
        result = await self._session.execute(stmt)
        refresh_token = result.scalar_one_or_none()
        if not refresh_token:
            raise RefreshTokenNotFound
        
        return refresh_token

    async def update_refresh_token(self, user_id: int, refresh_token: str):
        stmt = (
            update(RefreshTokenDBModel)
            .where(
                RefreshTokenDBModel.user_id == user_id
            )
            .values(
                token=refresh_token
            )
        )
        result = await self._session.execute(stmt)
        
        updated_count = result.rowcount
        
        if updated_count == 0:
            logger.warning(f"Row in table '{RefreshTokenDBModel.__tablename__}' with 'user_id={user_id}' not found.")
            raise RefreshTokenNotFound
        elif updated_count > 0:
            logger.debug(f"Row in table '{RefreshTokenDBModel.__tablename__} with 'user_id={user_id}' succesfully updated.")
        else:
            error_msg = f"updated_count={updated_count}; type(updated_count)={type(updated_count)}"
            logger.error(error_msg)
            raise CustomRepoException(message=f"Updating row FAILED: {error_msg}")
            
    async def add_refresh_token(self, user_id: int, refresh_token: str):
        refresh_token_db = RefreshTokenDBModel(
            user_id=user_id,
            token=refresh_token
        )
        
        self._session.add(refresh_token_db)
