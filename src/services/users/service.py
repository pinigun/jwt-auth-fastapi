from loguru import logger
from dataclasses import dataclass

from .dto import UserDTO
from ..exc import UserNotFound

from src.domain.uof.abstract import IUnitOfWork
from src.domain.repositories.exc import UserNotFound as UserNotFoundDB


@dataclass
class UsersService:
    unit_of_work: IUnitOfWork
    
    async def get_user(
        self,
        id: int
    ) -> UserDTO:
        try:
            logger.debug(f"Trying find user with id={id} in database")
            async with self.unit_of_work as uof:
                user = await uof.users.get_by_id(
                    id=id,
                )
        except UserNotFoundDB:
            logger.debug(f"User id={id} not found")
            raise UserNotFound
        
        except Exception as ex:
            logger.error(f"User getting failed User(id={id}). Error: {type(ex)}: {str(ex)}")
            raise ex
        
        return UserDTO(
            id=user.id,
            email=user.email
        )
